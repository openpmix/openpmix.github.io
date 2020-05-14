---
layout: page
title: Example: Direct-Launch Debugger Tool
---

UNDER CONSTRUCTION
==================

Please note that the tool-based launch of applications is a subject of
current RFC development. Thus, the description on this page should be
considered a “draft” at this time and is provided to help stimulate
discussion.

![RFC0022 Fig](/images/rfc0022.png 'RFC0022 Fig')

In the direct-launch use-case, the resource manager (RM) itself is
directly responsible for launching all processes, including debugger
daemons – i.e., there is no intermediate launcher such as *mpiexec*. The
user invokes a tool (typically on a non-compute, or “head”, node) to
launch their application. An allocation of resources may or may not have
been made in advance – if not, then the spawn request must include
allocation request information. Once invoked, the tool connects to a
system-level PMIx server, typically hosted by the resource manager (RM),
constructs a PMIx\_Spawn command, and communicates that command to the
server.

The system-level PMIx server “uplifts” the spawn request to its host RM
daemon for processing. If an allocation must be made, then the host RM
daemon is responsible for communicating that request to its associated
scheduler. Once resources are available, the host RM initiates the
launch process, sending the application launch command to its daemons on
the allocated nodes. The remote daemons then start their local client
processes and the debugger daemons, providing the latter with all
information required for them to attach to their targets.

The RM must parse the spawn request for relevant directives, returning
an error if any required directive cannot be supported. Whether the
parsing occurs on the initial daemon, or on the remote compute-node
daemons, is left to the RM.

In the following example, the debugger tool initially queries the host
RM regarding two key areas of support:

-   ability to co-launch debugger daemons with application processes –
    i.e., does the RM support combining debugger daemons with
    application descriptions in the same call to PMIx\_Spawn? If not,
    then the debugger tool must issue two spawn requests, one for the
    application and the other for the debugger daemons
-   debugger attach modes – i.e., does the RM support stopping the
    application at first instruction until the debugger daemon releases
    it? If not, then the debugger must either be instructed that the
    application will be stopping in its own internal location, or
    instruct the PMIx client library in the application to instead stop
    in PMIx\_Init until the debugger daemon releases it

The example assumes that co-launch is not supported on this RM, and so
it proceeds to construct two spawn commands, issuing the one to launch
the debugger daemons once it has determined that the application has
been successfully spawned. The example code then waits until it has been
notified by the RM (via registration of an appropriate PMIx event
handler) that the debugger and application have both completed.

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

    /* define a structure for collecting returned
     * info from a query */
    typedef struct {
        mylock_t lock;
        pmix_info_t *info;
        size_t ninfo;
    } myquery_data_t;

    static mylock_t waiting_for_debugger, waiting_for_client;
    static pmix_proc_t myproc;
    static char dspace[PMIX_MAX_NSLEN+1];
    static char clientspace[PMIX_MAX_NSLEN+1];

    /* this is a callback function for the PMIx_Query
     * API. The query will callback with a status indicating
     * if the request could be fully satisfied, partially
     * satisfied, or completely failed. The info parameter
     * contains an array of the returned data, with the
     * info->key field being the key that was provided in
     * the query call. Thus, you can correlate the returned
     * data in the info->value field to the requested key.
     *
     * Once we have dealt with the returned data, we must
     * call the release_fn so that the PMIx library can
     * cleanup */
    static void cbfunc(pmix_status_t status,
                       pmix_info_t *info, size_t ninfo,
                       void *cbdata,
                       pmix_release_cbfunc_t release_fn,
                       void *release_cbdata)
    {
        myquery_data_t *mq = (myquery_data_t*)cbdata;
        size_t n;

        /* save the returned info - the PMIx library "owns" it
         * and will release it and perform other cleanup actions
         * when release_fn is called */
        if (0 < ninfo) { PMIX_INFO_CREATE(mq->info, ninfo);
            mq->ninfo = ninfo;
            for (n=0; n < ninfo; n++) { fprintf(stderr, "Transferring %s\n", info[n].key); PMIX_INFO_XFER(&mq->info[n], &info[n]);
            }
        }

        /* let the library release the data and cleanup from
         * the operation */
        if (NULL != release_fn) {
            release_fn(release_cbdata);
        }

        /* release the block */
        DEBUG_WAKEUP_THREAD(&mq->lock);
    }

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
        /* if this was the debugger daemon, then flag it */
        if (0 == strncmp(source->nspace, dspace, PMIX_MAX_NSLEN)) {
            fprintf(stderr, "DEBUGGER DAEMON HAS EXITED\n");
            DEBUG_WAKEUP_THREAD(&waiting_for_debugger);
        } else if (0 == strncmp(source->nspace, clientspace, PMIX_MAX_NSLEN)) {
            fprintf(stderr, "CLIENT JOB HAS EXITED\n");
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
        pmix_info_t *info;
        pmix_app_t *app;
        size_t ninfo, napps;
        char *nspace = NULL;
        int i;
        pmix_query_t *query;
        size_t nq, n;
        myquery_data_t myquery_data;
        bool cospawn = false, stop_on_exec = false;
        char cwd[1024];
        pmix_status_t code;
        mylock_t mylock;
        pid_t pid;
        pmix_info_t *dinfo;
        pmix_app_t *debugger;
        size_t dninfo;
        pmix_proc_t wildcard;

        pid = getpid();

        info = NULL;
        ninfo = 0;

        DEBUG_CONSTRUCT_LOCK(&waiting_for_debugger);
        DEBUG_CONSTRUCT_LOCK(&waiting_for_client);

        /* we are going to ask the RM directly to launch
         * the application (plus debugger daemons) for us,
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

        /* register another handler specifically for when the
         * application and/or debugger completes */
        DEBUG_CONSTRUCT_LOCK(&mylock);
        code = PMIX_ERR_JOB_TERMINATED;
        PMIx_Register_event_handler(&code, 1, NULL, 0,
                                    release_fn, evhandler_reg_callbk, (void*)&mylock);
        DEBUG_WAIT_THREAD(&mylock);
        DEBUG_DESTRUCT_LOCK(&mylock);

        /* we need to know if this RM supports co-spawning of daemons with
         * the application, or if we need to launch the daemons as a separate
         * spawn command. The former is faster and more scalable, but not
         * every RM may support it. We also need to ask for debug support
         * so we know if the RM can stop-on-exec, or only supports stop-in-init */
        nq = 1;
        PMIX_QUERY_CREATE(query, nq);
        PMIX_ARGV_APPEND(rc, query[0].keys, PMIX_QUERY_SPAWN_SUPPORT);
        PMIX_ARGV_APPEND(rc, query[0].keys, PMIX_QUERY_DEBUG_SUPPORT);
        /* setup the caddy to retrieve the data */
        DEBUG_CONSTRUCT_LOCK(&myquery_data.lock);
        myquery_data.info = NULL;
        myquery_data.ninfo = 0;
        /* execute the query */
        fprintf(stderr, "Debugger: querying capabilities\n");
        if (PMIX_SUCCESS != (rc = PMIx_Query_info_nb(query, nq, cbfunc, (void*)&myquery_data))) {
            fprintf(stderr, "PMIx_Query_info failed: %d\n", rc);
            goto done;
        }
        DEBUG_WAIT_THREAD(&myquery_data.lock);
        DEBUG_DESTRUCT_LOCK(&myquery_data.lock);

        /* we should have received back two info structs, one containing
         * a comma-delimited list of PMIx spawn attributes the RM supports,
         * and the other containing a comma-delimited list of PMIx debugger
         * attributes it supports */
        if (2 != myquery_data.ninfo) {
            /* this is an error */
            fprintf(stderr, "PMIx Query returned an incorrect number of results: %lu\n", myquery_data.ninfo);
            PMIX_INFO_FREE(myquery_data.info, myquery_data.ninfo);
            goto done;
        }

        /* we would like to co-spawn the debugger daemons with the app, but
         * let's first check to see if this RM supports that operation by
         * looking for the PMIX_COSPAWN_APP attribute in the spawn support
         *
         * We will also check to see if "stop_on_exec" is supported. Few RMs
         * do so, which is why we have to check.
         *
         * Note that the PMIx reference server always returns the query results
         * in the same order as the query keys. However, this is not guaranteed,
         * so we need to search the entire returned info structures to find
         * the desired key */
        for (n=0; n < myquery_data.ninfo; n++) {
            if (0 == strcmp(myquery_data.info[n].key, PMIX_QUERY_SPAWN_SUPPORT)) {
                /* the returned value is a comma-delimited string of PMIx attributes
                 * related to the PMIx_Spawn command - see if the cospawn attribute is included */
                if (NULL != strstr(myquery_data.info[n].value.data.string, PMIX_COSPAWN_APP)) {
                    cospawn = true;
                } else {
                    cospawn = false;
                }
            } else if (0 == strcmp(myquery_data.info[n].key, PMIX_QUERY_DEBUG_SUPPORT)) {
                /* the returned value is a comma-delimited string of PMIx attributes
                 * related to debugger operations - see if the stop-on-exec attribute is included */
                if (NULL != strstr(myquery_data.info[n].value.data.string, PMIX_DEBUG_STOP_ON_EXEC)) {
                    stop_on_exec = true;
                } else {
                    stop_on_exec = false;
                }
            }
        }

        /* for the purposes of this example, we assume that cospawn is
         * not available. We will therefore do these as separate launches,
         * so do the app first */
        napps = 1;
        PMIX_APP_CREATE(app, napps);
        /* setup the executable */
        app[0].cmd = strdup("client");
        PMIX_ARGV_APPEND(rc, app[0].argv, "./client");
        getcwd(cwd, 1024);  // point us to our current directory
        app[0].cwd = strdup(cwd);
        app[0].maxprocs = 2;
        /* provide job-level directives instructing the RM as to the
         * desired behaviors. This can include directives on mapping
         * algorithms, allocation requirements, or any spawn-related
         * attribute the user may wish to request */
        ninfo = 5;
        PMIX_INFO_CREATE(info, ninfo);
        /* for purposes of this example, we assume that the user has
         * requested a specific mapping algorithm, and that this
         * debugger wishes to receive stdout/stderr from the app */
        PMIX_INFO_LOAD(&info[0], PMIX_MAPBY, "slot", PMIX_STRING);  // map by slot
        if (stop_on_exec) {
            PMIX_INFO_LOAD(&info[1], PMIX_DEBUG_STOP_ON_EXEC, NULL, PMIX_BOOL);  // procs are to stop on first instruction
        } else {
            PMIX_INFO_LOAD(&info[1], PMIX_DEBUG_STOP_IN_INIT, NULL, PMIX_BOOL);  // procs are to pause in PMIx_Init for debugger attach
        }
        PMIX_INFO_LOAD(&info[2], PMIX_FWD_STDOUT, NULL, PMIX_BOOL);  // forward stdout to me
        PMIX_INFO_LOAD(&info[3], PMIX_FWD_STDERR, NULL, PMIX_BOOL);  // forward stderr to me
        PMIX_INFO_LOAD(&info[4], PMIX_NOTIFY_COMPLETION, NULL, PMIX_BOOL); // notify us when the job completes

        /* spawn the job - the function will return when the app
         * has been launched */
        fprintf(stderr, "Debugger: spawning %s\n", app[0].cmd);
        if (PMIX_SUCCESS != (rc = PMIx_Spawn(info, ninfo, app, napps, clientspace))) {
            fprintf(stderr, "Application failed to launch with error: %s(%d)\n", PMIx_Error_string(rc), rc);
            goto done;
        }
        PMIX_INFO_FREE(info, ninfo);
        PMIX_APP_FREE(app, napps);

        /* now setup and launch the debugger daemons */
        PMIX_APP_CREATE(debugger, 1);
        debugger[0].cmd = strdup("./debuggerd");
        PMIX_ARGV_APPEND(rc, debugger[0].argv, "./debuggerd");
        getcwd(cwd, 1024);  // point us to our current directory
        debugger[0].cwd = strdup(cwd);
        /* provide directives so the daemons go where we want, and
         * let the RM know these are debugger daemons */
        dninfo = 7;
        PMIX_INFO_CREATE(dinfo, dninfo);
        PMIX_INFO_LOAD(&dinfo[0], PMIX_MAPBY, "ppr:1:node", PMIX_STRING);  // instruct the RM to launch one copy of the executable on each node
        PMIX_INFO_LOAD(&dinfo[1], PMIX_DEBUGGER_DAEMONS, NULL, PMIX_BOOL); // these are debugger daemons
        PMIX_INFO_LOAD(&dinfo[1], PMIX_DEBUG_JOB, clientspace, PMIX_STRING); // the nspace being debugged
        PMIX_INFO_LOAD(&dinfo[2], PMIX_NOTIFY_COMPLETION, NULL, PMIX_BOOL); // notify us when the debugger job completes
        PMIX_INFO_LOAD(&dinfo[3], PMIX_DEBUG_WAITING_FOR_NOTIFY, NULL, PMIX_BOOL);  // tell the daemon that the proc is waiting
                                                                                    // to be released via a PMIx event
        PMIX_INFO_LOAD(&dinfo[4], PMIX_FWD_STDOUT, NULL, PMIX_BOOL);  // forward stdout to me
        PMIX_INFO_LOAD(&dinfo[5], PMIX_FWD_STDERR, NULL, PMIX_BOOL);  // forward stderr to me
        wildcard = PMIX_RANK_WILDCARD;
        PMIX_INFO_LOAD(&dinfo[6], PMIX_FWD_STDIN, &wildcard, PMIX_PROC_RANK);  // forward a copy of my stdin to all debugger daemons

        /* spawn the daemons */
        fprintf(stderr, "Debugger: spawning %s\n", debugger[0].cmd);
        if (PMIX_SUCCESS != (rc = PMIx_Spawn(dinfo, dninfo, debugger, 1, dspace))) {
            fprintf(stderr, "Debugger daemons failed to launch with error: %s\n", PMIx_Error_string(rc));
        }
        fprintf(stderr, "SPAWNED DEBUGGERD\n");
        /* cleanup */
        PMIX_INFO_FREE(dinfo, dninfo);
        PMIX_APP_FREE(debugger, 1);

        /* this is where a debugger tool would wait until the debug operation is complete */
        DEBUG_WAIT_THREAD(&waiting_for_debugger);
        DEBUG_WAIT_THREAD(&waiting_for_client);

      done:
        DEBUG_DESTRUCT_LOCK(&waiting_for_debugger);
        PMIx_tool_finalize();

        return(rc);
    }

