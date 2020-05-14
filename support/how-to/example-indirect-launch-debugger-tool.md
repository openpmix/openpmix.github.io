---
layout: default
title: Example: Indirect-Launch Debugger Tool
---

UNDER CONSTRUCTION
==================

Please note that the tool-based launch of applications is a subject of
current RFC development. Thus, the description on this page should be
considered a “draft” at this time and is provided to help stimulate
discussion.

![RFC0022b Fig](/images/rfc0022b.png 'RFC0022b Fig')

In the indirect-launch use-case, the resource manager (RM) itself is not
involved in launching application processes or debugger daemons. Indeed,
in some cases the RM has no actual visibility of those processes, nor
knowledge of their existence. Instead, processes are started via an
intermediate launcher such as *mpiexec* (which we will use for this
example). In turn, the intermediate launcher starts its own network of
daemons (e.g., *mpid*) that assume responsibility for launching and
supporting the job. The intermediate launcher may use the RM to launch
the daemons, or *ssh*, depending on the precise implementation,
environment, and user preferences.

A primary objective during the design of this operational mode is to
avoid any requirement that the debugger parse and/or understand the
command line of *mpiexec*. Thus, the focus is on cleanly passing all
non-debugger options from the initial command line to *mpiexec*, using
the PMIx tool-to-server connection to communicate any other directives.

In this operational mode, the user invokes a tool (typically on a
non-compute, or “head”, node) that in turn uses *mpiexec* to launch
their application – a typical command line might look like the
following:

    $ dbgr -dbgoption mpiexec -n 32 ./myapp

The tool may subsequently invoke *mpiexec* by simply executing it from a
command line (e.g., using the Posix “system” function), or it may
fork/exec it, or may request that it be started by the RM using the
PMIx\_Spawn API. The above illustration uses the last method. Regardless
of how it is started, the debugger sets the
PMIX\_LAUNCHER\_PAUSE\_FOR\_TOOL in the environment of *mpiexec* or in
the pmix\_info\_t array in the spawn command. This instructs *mpiexec*
to pause after initialization so it can receive further instructions
from the debugger. This might include a request to co-spawn debugger
daemons along with the application, or further directives relating to
the startup of the application (e.g., to LD\_PRELOAD a library, or
replace the launcher’s local spawn agent with one provided by the
debugger).

As *mpiexec* starts up, it calls PMIx\_server\_init to setup its PMIx
server. The server initialization includes writing a server-level
rendezvous file that allows other processes (such as the originating
debugger) to connect to the server. It then pauses, awaiting further
instructions from the debugger.

Armed with the pid (returned by fork/exec or the “system” command) or
the namespace (returned by PMIx\_Spawn) of the executing *mpiexec*, the
debugger tool utilizes the PMIx\_tool\_switch\_server API to complete
the connection to the *mpiexec* server. Note that:

-   PMIx does not allow servers to initiate connections – thus, the
    debugger tool must initiate the connection to the *mpiexec* server.
-   tools can only be connected to one server at a time. Therefore, if
    connected to the system-level server to use PMIx\_Spawn to launch
    *mpiexec*, the debugger tool will be disconnected from that server
    and connected to the PMIx server in *mpiexec*

At this point, the debugger can execute any PMIx operation, including:

-   query *mpiexec* capabilities;
-   pass directives to configure application behavior – e.g., specifying
    the desired pause point where application processes shall wait for
    debugger release;
-   request launch of debugger daemons, providing the appropriate
    pmix\_app\_t description
-   specify a replacement fork/exec agent; and
-   define/modify standard environmental variables for the application

Once ready to launch, *mpiexec* parses its command line to obtain a
description of the desired job. An allocation of resources may or may
not have been made in advance (either by the user, or by the tool prior
to starting *mpiexec*)- if not, then *mpiexec* may itself utilize the
PMIx\_Alloc API to obtain one from the system-level PMIx server. Once
resources are available, *mpiexec* initiates the launch process by first
spawning its daemon network across the allocation – in the above
diagram, this is done via *ssh* commands. After the daemons have
launched and wired up, *mpiexec* sends an application launch command to
its daemons, which then start their local client processes and debugger
daemons, providing the latter with all information required for them to
attach to their targets.

The following example illustrates how a debugger tool would execute an
indirect launch using the *mpiexec* launcher from some supporting MPI
library. There are a few points worth noting:

-   the debugger tool itself doesn’t need to know if *mpiexec* can
    co-launch the debugger daemons, or must launch the application and
    debugger daemons as separate operations. We require that mpiexec
    notify the tool when the entire spawn is completed
-   the *mpiexec* launcher is required to provide each debugger daemon
    with the nspace of the target application it is to debug. This is
    done via a job-level PMIx attribute that the debugger daemon can
    query upon startup. Once the daemon has the target nspace, it can
    obtain the local (and complete, if desired) table of process pid’s
    and hostnames (commonly called the *proctable*) by querying it from
    the local PMIx server hosted in the local mpid
-   the debugger tool command-line parser does not need to identify the
    application to be executed. It can parse only its own options,
    taking everything else as being an opaque array of argv to be passed
    along
-   the job-level information provided by mpiexec to the debugger
    daemons must include the mechanism by which the daemon can release
    the target application processes. This could include release via
    PMIx event notification (the precise notification code must be
    given), use of a specific signal, or some other mechanism. The
    debugger is free to terminate the job if it cannot support the given
    mechanism

<!-- -->

    #define _GNU_SOURCE
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <time.h>
    #include <pthread.h>

    #include <pmix_tool.h>

    typedef struct {
        pthread_mutex_t mutex;
        pthread_cond_t cond;
        volatile bool active;
        pmix_status_t status;
    } mylock_t;

    #define DEBUG_CONSTRUCT_LOCK(l)                     \
        do {                                            \
            pthread_mutex_init(&(l)->mutex, NULL);      \
            pthread_cond_init(&(l)->cond, NULL);        \
            (l)->active = true;                         \
            (l)->status = PMIX_SUCCESS;                 \
        } while(0)

    #define DEBUG_DESTRUCT_LOCK(l)              \
        do {                                    \
            pthread_mutex_destroy(&(l)->mutex); \
            pthread_cond_destroy(&(l)->cond);   \
        } while(0)

    #define DEBUG_WAIT_THREAD(lck)                                      \
        do {                                                            \
            pthread_mutex_lock(&(lck)->mutex);                          \
            while ((lck)->active) {                                     \
                pthread_cond_wait(&(lck)->cond, &(lck)->mutex);         \
            }                                                           \
            pthread_mutex_unlock(&(lck)->mutex);                        \
        } while(0)

    #define DEBUG_WAKEUP_THREAD(lck)                        \
        do {                                                \
            pthread_mutex_lock(&(lck)->mutex);              \
            (lck)->active = false;                          \
            pthread_cond_broadcast(&(lck)->cond);           \
            pthread_mutex_unlock(&(lck)->mutex);            \
        } while(0)

    static mylock_t waiting_for_client;
    static pmix_proc_t myproc;
    static char mpiexec_nspace[PMIX_MAX_NSLEN+1];

    /* this is the event notification function we pass down below
     * when registering for general events - i.e.,, the default
     * handler. */
    static void notification_fn(size_t evhdlr_registration_id,
                                pmix_status_t status,
                                const pmix_proc_t *source,
                                pmix_info_t info[], size_t ninfo,
                                pmix_info_t results[], size_t nresults,
                                pmix_event_notification_cbfunc_fn_t cbfunc,
                                void *cbdata)
    {
        /* this example doesn't do anything with default events */
        if (NULL != cbfunc) {
            cbfunc(PMIX_EVENT_ACTION_COMPLETE, NULL, 0, NULL, NULL, cbdata);
        }
    }

    /* this is an event notification function that we explicitly request
     * be called when the PMIX_ERR_JOB_TERMINATED notification is issued.
     * We could catch it in the general event notification function and test
     * the status to see if it was "job terminated", but it often is simpler
     * to declare a use-specific notification callback point. In this case,
     * we are asking to know whenever a job terminates, and we will then
     * know we can exit */
    static void release_fn(size_t evhdlr_registration_id,
                           pmix_status_t status,
                           const pmix_proc_t *source,
                           pmix_info_t info[], size_t ninfo,
                           pmix_info_t results[], size_t nresults,
                           pmix_event_notification_cbfunc_fn_t cbfunc,
                           void *cbdata)
    {
        /* tell the event handler state machine that we are the last step */
        if (NULL != cbfunc) {
            cbfunc(PMIX_EVENT_ACTION_COMPLETE, NULL, 0, NULL, NULL, cbdata);
        }
        /* if this was mpiexec, then flag it */
        if (0 == strncmp(source->nspace, mpiexec_space, PMIX_MAX_NSLEN)) {
            waiting_for_client.status = status;
            fprintf(stderr, "JOB HAS EXITED\n");
            DEBUG_WAKEUP_THREAD(&waiting_for_client);
        }
    }

    /* event handler registration is done asynchronously because it
     * may involve the PMIx server registering with the host RM for
     * external events. So we provide a callback function that returns
     * the status of the request (success or an error), plus a numerical index
     * to the registered event. The index is used later on to deregister
     * an event handler - if we don't explicitly deregister it, then the
     * PMIx server will do so when it see us exit */
    static void evhandler_reg_callbk(pmix_status_t status,
                                     size_t evhandler_ref,
                                     void *cbdata)
    {
        mylock_t *lock = (mylock_t*)cbdata;

        if (PMIX_SUCCESS != status) {
            fprintf(stderr, "Client %s:%d EVENT HANDLER REGISTRATION FAILED WITH STATUS %d, ref=%lu\n",
                       myproc.nspace, myproc.rank, status, (unsigned long)evhandler_ref);
        }
        lock->status = status;
        DEBUG_WAKEUP_THREAD(lock);
    }

    int main(int argc, char **argv)
    {
        pmix_status_t rc;
        pmix_app_t app, debugger;
        pmix_info_t *info;
        char cwd[1024], *tmp;
        pmix_status_t code;
        mylock_t mylock;
        pid_t pid;
        pmix_proc_t wildcard;
        pmix_envar_t preload;

        pid = getpid();

        info = NULL;
        ninfo = 0;

        DEBUG_CONSTRUCT_LOCK(&waiting_for_client);
        memset(clientnspace, 0, sizeof(clientnspace));

        /* we are going to ask the RM to launch mpiexec for us,
         * so we want to connect only to the system-level
         * PMIx server */
        PMIX_INFO_CREATE(info, 1);
        PMIX_INFO_LOAD(&info[0], PMIX_CONNECT_SYSTEM_ONLY, NULL, PMIX_BOOL);
        /* init as a tool */
        if (PMIX_SUCCESS != (rc = PMIx_tool_init(&myproc, info, ninfo))) {
            fprintf(stderr, "PMIx_tool_init failed: %d\n", rc);
            exit(rc);
        }
        PMIX_INFO_FREE(info, ninfo);

        fprintf(stderr, "Tool ns %s rank %d pid %lu: Running\n", myproc.nspace, myproc.rank, (unsigned long)pid);

        /* register a default event handler. We don't technically
         * need to register one, but it is usually good practice to
         * catch any events that occur */
        DEBUG_CONSTRUCT_LOCK(&mylock);
        PMIx_Register_event_handler(NULL, 0, NULL, 0,
                                    notification_fn, evhandler_reg_callbk, (void*)&mylock);
        DEBUG_WAIT_THREAD(&mylock);
        DEBUG_DESTRUCT_LOCK(&mylock);

        /* register another handler specifically for when
         * mpiexec completes */
        DEBUG_CONSTRUCT_LOCK(&mylock);
        code = PMIX_ERR_JOB_TERMINATED;
        PMIx_Register_event_handler(&code, 1, NULL, 0,
                                    release_fn, evhandler_reg_callbk, (void*)&mylock);
        DEBUG_WAIT_THREAD(&mylock);
        DEBUG_DESTRUCT_LOCK(&mylock);

        /* we will use one pmix_app_t struct for mpiexec
         * which will include the argv required for mpiexec to construct
         * its launch command */
        PMIX_APP_CONSTRUCT(&app);

        getcwd(cwd, 1024);  // point us to our current directory

        /* In this example, no debugger cmd line options were given, so
         * we can start with the first argv position being the
         * "mpiexec" command */
        app.cmd = strdup(argv[1]);
        /* copy over the argv array provided by the user. This will
         * ensure that mpiexec is able to parse its own cmd line
         * and avoids forcing the debugger to understand it */
        for (n=1; n < argc; n++ {
            PMIX_ARGV_APPEND(rc, app.argv, argv[n]);
        }
        app.cwd = strdup(cwd);
        app.maxprocs = 1;
        /* we do have some attributes to pass for this app */
        app.ninfo = 8;
        PMIX_INFO_CREATE(app.info, app.ninfo);
        /* mark that this app is a launcher - the RM may not care, but we provide
         * the additional info just in case it does */
        PMIX_INFO_LOAD(&app.info[0], PMIX_SPAWN_LAUNCHER, NULL, PMIX_BOOL);
        /* indicate that we want all output forwarded to us - note that
         * we don't need to forward the output from the application or
         * debugger daemons directly as we expect mpiexec to do that
         * for us, so we just need to tell mpiexec to send it to us */
        PMIX_INFO_LOAD(&app.info[1], PMIX_FWD_STDOUT, NULL, PMIX_BOOL);  // forward stdout to me
        PMIX_INFO_LOAD(&app.info[2], PMIX_FWD_STDERR, NULL, PMIX_BOOL);  // forward stderr to me
        /* ask that we be notified when the entire job completes so we can exit */
        PMIX_INFO_LOAD(&app.info[3], PMIX_NOTIFY_COMPLETION, NULL, PMIX_BOOL);
        /* instruct mpiexec to use our own local fork/exec agent in place
         * of its internal one */
        PMIX_INFO_LOAD(&app.info[4], PMIX_SPAWN_LOCAL_FORK_AGENT, "localforker", PMIX_STRING);
        /* indicate that we want the procs to wait for debugger release according to the
         * following preferred mechanisms, taking the first one that is supported:
         *    - at first instruction
         *    - in a location programmed by the app or embedded library 
         *    - in PMIx_Init
         */
        asprintf(&tmp, "%s,%s,%s", PMIX_DEBUG_STOP_ON_EXEC, PMIX_DEBUG_STOP_IN_APP, PMIX_DEBUG_STOP_IN_INIT);
        PMIX_INFO_LOAD(&app.info[5], PMIX_SPAWN_STOP_FOR_DEBUGGER, tmp, PMIX_STRING);
        free(tmp);
        /* tell it to wait for further instructions */
        PMIX_INFO_LOAD(&app.info[6], PMIX_LAUNCHER_PAUSE_FOR_TOOL, NULL, PMIX_BOOL);
        /* ask that it preload our special library */
        preload.envar = "LD_PRELOAD";
        preload.value = "ourlib.so";
        preload.separator = ':';
        PMIX_INFO_LOAD(&app.info[7], PMIX_PREPEND_ENVAR, &preload, PMIX_ENVAR);

        /* spawn mpiexec - the function will return when mpiexec has
         * been started */
        fprintf(stderr, "Debugger: spawning mpiexec\n");
        if (PMIX_SUCCESS != (rc = PMIx_Spawn(NULL, 0, &app, 1, mpiexec_nspace))) {
            fprintf(stderr, "mpiexec failed to launch with error: %s(%d)\n", PMIx_Error_string(rc), rc);
            goto done;
        }
        PMIX_APP_DESTRUCT(&app);

        /* now that mpiexec has started, we can initiate the connection request.
         * The process will scan for rendezvous files matching the specified
         * description - this will continue until complete, or a given timeout
         * is reached. If successful, the connection to the system server
         * will have been replaced with a connection to the mpiexec server */
        if (PMIX_SUCCESS != (rc = PMIx_tool_switch_server(mpiexec_nspace, NULL, 0))) {
            fprintf(stderr, "Failed to connect to mpiexec server\n");
            goto done;
        }

        /* construct the debugger description */
        PMIX_APP_CONSTRUCT(&debugger);
        debugger.cmd = strdup("debuggerd");
        PMIX_ARGV_APPEND(rc, debugger.argv, "debuggerd");
        debugger.cwd = strdup(cwd);
        /* provide directives so the daemons go where we want, and
         * let mpiexec know these are debugger daemons */
        debugger.ninfo = 4;
        PMIX_INFO_CREATE(debugger.info, app[1].ninfo);
        /* instruct mpiexec to launch one copy of the debugger daemon for
         * each application process - each daemon will know its relative
         * rank on the local node, and the relative rank of all application
         * procs on the node. Thus, the daemons have all required info to
         * identify their target proc */
        PMIX_INFO_LOAD(&debugger.info[0], PMIX_MAPBY, "ppr:1:proc", PMIX_STRING);
        /* flag that these are debugger daemons */
        PMIX_INFO_LOAD(&debugger.info[1], PMIX_DEBUGGER_DAEMONS, NULL, PMIX_BOOL);
        /* tell the debugger daemon that app procs are waiting to be released - the
         * debugger must obtain the mechanism by querying it from the
         * provided job-level info of the target application */
        PMIX_INFO_LOAD(&debugger.info[2], PMIX_DEBUG_WAITING_FOR_NOTIFY, NULL, PMIX_BOOL);
        /* ask our PMIx library to forward a copy of my stdin to all debugger daemons */
        wildcard = PMIX_RANK_WILDCARD;
        PMIX_INFO_LOAD(&debugger.info[3], PMIX_FWD_STDIN, &wildcard, PMIX_PROC_RANK);

        /* provide a directive instructing mpiexec to execute its actions */
        PMIX_INFO_CONSTRUCT(&info);
        PMIX_INFO_LOAD(&info, PMIX_LAUNCHER_RELEASE, NULL, PMIX_BOOL);

        /* spawn */
        fprintf(stderr, "Debugger: spawning application\n");
        if (PMIX_SUCCESS != (rc = PMIx_Spawn(&info, 1, &debugger, 1, debuggernspace))) {
            fprintf(stderr, "mpiexec failed to launch with error: %s(%d)\n", PMIx_Error_string(rc), rc);
            goto done;
        }
        PMIX_APP_DESTRUCT(&debugger);

        /* this is where a debugger tool would wait until the debug operation is complete. Note
         * that the PMIx progress thread is capturing stdin and forwarding it in the background */
        DEBUG_WAIT_THREAD(&waiting_for_client);
        rc = waiting_for_client.status;

      done:
        DEBUG_DESTRUCT_LOCK(&waiting_for_client);
        PMIx_tool_finalize();

        return(rc);
    }

