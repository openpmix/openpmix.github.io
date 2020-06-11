---
layout: default
title: Job Control and Monitoring
---

RFC0015
=======

Title
-----

Job Control and Monitoring APIs

Abstract
--------

Provide APIs by which applications and tools can issue job control
directives (e.g., pause and signal) to the local PMIx server and host
system management stack, and request monitoring for application
processes

Labels
------

\[EXTENSION\] \[CLIENT-API\] \[SERVER-API\] \[RM-INTERFACE\]

Action
------

\[ACCEPTED\]

Copyright Notice
----------------

Copyright 2017 Intel, Inc. All rights reserved

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

As HPC systems grow in size and capability, applications have
increasingly needed a mechanism by which they can actively participate
in "steering" the overall execution. This RFC deals with one aspect of
this requirement by providing the application with the ability to
communicate job control and monitoring directives to the host system
management stack (SMS). While a few specific directives have been
identified, it is expected that this capability will grow "organically"
in response to evolving requirements. Thus, care has been taken to make
the APIs in this RFC as generic as possible to avoid modifying them
going forward.

#### Job Control

As applications take more control over their operation, they will
increasingly need an ability to respond to reported changes in
application execution and/or their environment. One dimension of the
response involves requesting control operations from the host SMS –
e.g., to restart a specified set of processes.

There is one proposed new client-side API for this purpose:

    pmix_status_t PMIx_Job_control_nb(const pmix_proc_t targets[], size_t ntargets,
                                      const pmix_info_t directives[], size_t ndirs,
                                      pmix_info_cbfunc_t cbfunc, void *cbdata);

The *targets* array identifies the processes to which the requested job
control action is to be applied. A NULL value can be used to indicate
all processes in the caller’s nspace. The use of *PMIX\_RANK\_WILDARD*
in a target *pmix\_proc\_t* can also be used to indicate that all
processes in the given nspace are to be included.

The callback function provides a status to indicate whether or not the
request was granted, and to provide some information as to the reason
for any denial in the *pmix\_info\_cbfunc\_t* array of *pmix\_info\_t*
structures.

Currently identified attributes (and their associated data type) that
can be used to steer behavior via the directives array include:

    /* job control attributes */
    #define PMIX_JOB_CTRL_ID                    "pmix.jctrl.id"         // (char*) provide a string identifier for this request
    #define PMIX_JOB_CTRL_PAUSE                 "pmix.jctrl.pause"      // (bool) pause the specified processes
    #define PMIX_JOB_CTRL_RESUME                "pmix.jctrl.resume"     // (bool) "un-pause" the specified processes
    #define PMIX_JOB_CTRL_CANCEL                "pmix.jctrl.cancel"     // (char*) cancel the specified request
                                                                        //         (NULL => cancel all requests from this requestor)
    #define PMIX_JOB_CTRL_KILL                  "pmix.jctrl.kill"       // (bool) forcibly terminate the specified processes and cleanup
    #define PMIX_JOB_CTRL_RESTART               "pmix.jctrl.restart"    // (char*) restart the specified processes using the given checkpoint ID
    #define PMIX_JOB_CTRL_CHECKPOINT            "pmix.jctrl.ckpt"       // (char*) checkpoint the specified processes and assign the given ID to it
    #define PMIX_JOB_CTRL_CHECKPOINT_EVENT      "pmix.jctrl.ckptev"     // (pmix_status_t) use given event code to trigger process checkpoint
    #define PMIX_JOB_CTRL_CHECKPOINT_SIGNAL     "pmix.jctrl.ckptsig"    // (int) use the given signal to trigger process checkpoint
    #define PMIX_JOB_CTRL_CHECKPOINT_TIMEOUT    "pmix.jctrl.ckptsig"    // (int) time in seconds to wait for checkpoint to complete
    #define PMIX_JOB_CTRL_SIGNAL                "pmix.jctrl.sig"        // (int) send given signal to specified processes
    #define PMIX_JOB_CTRL_PROVISION             "pmix.jctrl.pvn"        // (char*) regex identifying nodes that are to be provisioned
    #define PMIX_JOB_CTRL_PROVISION_IMAGE       "pmix.jctrl.pvnimg"     // (char*) name of the image that is to be provisioned
    #define PMIX_JOB_CTRL_PREEMPTIBLE           "pmix.jctrl.preempt"    // (bool) declare that job can be pre-empted

Requests use arrays of attributes to fully describe the request – e.g.,
the directives array might contain the following:

    pmix_info_t directives[2];
    PMIX_INFO_LOAD(&directives[0], PMIX_JOB_CTRL_CHECKPOINT, "mycheckpoint.1", PMIX_STRING)
    PMIX_INFO_LOAD(&directives[1], PMIX_JOB_CTRL_CHECKPOINT_SIGNAL, SIGUSR2, PMIX_INT);

which directs the host RM to checkpoint the specified processes, naming
the checkpoint "mycheckpoint.1", and to send the SIGUSR2 signal to each
process to trigger the checkpoint operation.

Each job control request can specify a user-created "request ID" string.
This allows the initiator to issue follow-on requests (e.g., for status
updates via the PMIx\_Query function), or to issue a subsequent
PMIx\_Job\_control call to cancel the request. A request to cancel job
control requests that does not specify an ID will result in cancellation
of *all* outstanding requests associated with the requestor.

The server-side callback function is defined as follows:

    typedef pmix_status_t (*pmix_server_job_control_fn_t)(const pmix_proc_t *requestor,
                                                          const pmix_proc_t targets[], size_t ntargets,
                                                          const pmix_info_t directives[], size_t ndirs,
                                                          pmix_info_cbfunc_t cbfunc, void *cbdata);

The local PMIx server essentially passes all information provided by the
client, plus the identifier of the requestor, to the host environment
for processing. Return of an error status indicates that the host
environment is unable to perform the requested operation, with the value
of the status indicating the reason for the rejection. In this case, the
callback function will not be executed, and the local PMIx server must
return the error to the requestor to avoid hanging.

If the host environment accepts the request, then the provided callback
function will be executed upon completion. Note that this does *not*
mean that success is guaranteed – it only means that the host
environment has at least accepted the request for processing (i.e.,
there are no immediately obvious errors). The lack of required
authorities or other factors may still cause a request to ultimately
fail.

In addition to the job control APIs and attributes, several supporting
definitions are provided, including the following status codes:

    /* status code for notification of checkpoint events */
    #define PMIX_JCTRL_CHECKPOINT                 (PMIX_ERR_V2X_BASE - 6)    // monitored by client to trigger checkpoint operation
    #define PMIX_JCTRL_CHECKPOINT_COMPLETE        (PMIX_ERR_V2X_BASE - 7)    // sent by client and monitored by server to notify that requested
                                                                             //     checkpoint operation has completed
    #define PMIX_JCTRL_PREEMPT_ALERT              (PMIX_ERR_V2X_BASE - 8)    // monitored by client to detect RM intends to preempt

An application can register for event notifications to receive alerts of
intended preemptions, or to see that a checkpoint is being requested.
Similarly, the host SMS can register for an event notifying it that the
application process has completed its checkpoint operation, and thus is
ready to either be terminated or preempted.

Tools, of course, have no way of knowing what method and/or signal an
application is using for checkpoint support. Accordingly, this RFC
includes an attribute by which an application can register its
checkpoint support methods with the local server:

    #define PMIX_JOB_CTRL_CHECKPOINT_METHOD     "pmix.jctrl.ckmethod"   // (pmix_data_array_t) array of pmix_info_t declaring each
                                                                        //      method and value supported by this application

Tools can then simply issue a job control request to
PMIX\_JOB\_CTRL\_CHECKPOINT and the server will use the first registered
method that it supports. If an application has not registered a
checkpoint method, then the server will return an error to the tool as
it cannot know if and how the application supports that operation.

Users may also wish to know when job control operations have been
requested and/or performed. Accordingly, new log attributes have been
added to support user notifications. These include:

    /* log attributes */
    #define PMIX_LOG_EMAIL                      "pmix.log.email"        // (pmix_data_array_t) log via email based on pmix_info_t
                                                                        //       containing directives
    #define PMIX_LOG_EMAIL_ADDR                 "pmix.log.emaddr"       // (char*) comma-delimited list of email addresses that are to recv msg
    #define PMIX_LOG_EMAIL_SUBJECT              "pmix.log.emsub"        // (char*) subject line for email
    #define PMIX_LOG_EMAIL_MSG                  "pmix.log.emmsg"        // (char*) msg to be included in email

#### Monitoring

Parallel applications sometimes deadlock or block indefinitely without
making progress. This problem can arise from race conditions in the
application code as well as bugs in system software or hardware. Such
jobs waste compute resources, especially on large-scale systems.

There is one proposed new client-side API that defines an interface to
enable the system to automatically detect and act on such jobs. It is
inspired by the development of and experiences with
[io-watchdog](https://github.com/grondo/io-watchdog) and on prior work
that used changes in a "canary" file as a marker of progress. The
proposed client-side API is:

    pmix_status_t PMIx_Process_monitor_nb(const pmix_info_t *monitor, pmix_status_t error,
                                          const pmix_info_t directives[], size_t ndirs,
                                          pmix_info_cbfunc_t cbfunc, void *cbdata);

The *monitor* parameter declares the type of monitoring being requested
(e.g., heartbeat). The *error* parameter indicates the status code to be
used when generating an event notification alerting that the monitor has
been triggered. The range of the notification defaults to
PMIX\_RANGE\_NAMESPACE – this can be changed by providing a PMIX\_RANGE
directive. The *directives* array characterizes the monitoring request
(e.g., monitor file size) and frequency of checking to be done. Finally,
the *cbfunc* provides a status to indicate whether or not the request
was granted, and to provide some information as to the reason for any
denial in the pmix\_info\_cbfunc\_t array of pmix\_info\_t structures.

The server-side callback function simply adds the identity of the
requesting process so that the host SMS knows which process is to be
monitored:

    /* Request that a client be monitored for activity */
    typedef pmix_status_t (*pmix_server_monitor_fn_t)(const pmix_proc_t *requestor,
                                                      const pmix_info_t *monitor, pmix_status_t error,
                                                      const pmix_info_t directives[], size_t ndirs,
                                                      pmix_info_cbfunc_t cbfunc, void *cbdata);

Monitoring is a little different than other PMIx features in that PMIx
actually contains its own internal (rather limited) monitoring
capability. This was provided both as a means of ensuring broad
availability of a few key features, and to help offload the SMS
(heartbeats, for example, are easily handled by the PMIx client-server
messaging system). However, PMIx will defer operations to the host SMS
unless requested otherwise by including the
PMIX\_SERVER\_ENABLE\_MONITORING attribute to PMIx\_server\_init. The
attributes and status codes defined to support monitoring include:

    /* server initialization attributes */
    #define PMIX_SERVER_ENABLE_MONITORING       "pmix.srv.monitor"      // (bool) Enable PMIx internal monitoring by server

    /* monitoring event codes */
    #define PMIX_MONITOR_HEARTBEAT_ALERT        (PMIX_ERR_V2X_BASE -  9)
    #define PMIX_MONITOR_FILE_ALERT             (PMIX_ERR_V2X_BASE - 10)

    /* monitoring attributes */
    #define PMIX_MONITOR_ID                     "pmix.monitor.id"       // (char*) provide a string identifier for this request
    #define PMIX_MONITOR_CANCEL                 "pmix.monitor.cancel"   // (char*) identifier to be canceled (NULL = cancel all
                                                                        //         monitoring for this process
    #define PMIX_MONITOR_APP_CONTROL            "pmix.monitor.appctrl"  // (bool) the application desires to control the response to
                                                                        //        a monitoring event
    #define PMIX_MONITOR_HEARTBEAT              "pmix.monitor.mbeat"    // (void) register to have the server monitor the requestor for heartbeats
    #define PMIX_SEND_HEARTBEAT                 "pmix.monitor.beat"     // (void) send heartbeat to local server
    #define PMIX_MONITOR_HEARTBEAT_TIME         "pmix.monitor.btime"    // (uint32_t) time in seconds before declaring heartbeat missed
    #define PMIX_MONITOR_HEARTBEAT_DROPS        "pmix.monitor.bdrop"    // (uint32_t) number of heartbeats that can be missed before
                                                                        //            generating the event (defaults to alert on first drop)
    #define PMIX_MONITOR_FILE                   "pmix.monitor.fmon"     // (char*) register to monitor file for signs of life
    #define PMIX_MONITOR_FILE_SIZE              "pmix.monitor.fsize"    // (bool) monitor size of given file is growing to determine app is running
    #define PMIX_MONITOR_FILE_ACCESS            "pmix.monitor.faccess"  // (char*) monitor time since last access of given file to determine app is running
    #define PMIX_MONITOR_FILE_MODIFY            "pmix.monitor.fmod"     // (char*) monitor time since last modified of given file to determine app is running
    #define PMIX_MONITOR_FILE_CHECK_TIME        "pmix.monitor.ftime"    // (uint32_t) time in seconds between checking file
    #define PMIX_MONITOR_FILE_DROPS             "pmix.monitor.fdrop"    // (uint32_t) number of file checks that can be missed before
                                                                        //            generating the event

The monitoring event codes can be used by the SMS itself to trigger a
defined response. However, application developers may prefer that the
application register for these events so that the application can (via
the job control API) determine the desired response. In this case, the
application will provide the PMIX\_MONITOR\_APP\_CONTROL attribute in
the directives to request that the SMS not respond on its own behalf.

Since sending of a heartbeat will be a common operation, a macro is
provided to simplify the call:

    /* define a special macro to simplify sending of a heartbeat */
    #define PMIx_Heartbeat()                                                    \
        do {                                                                    \
            pmix_info_t _in;                                                    \
            PMIX_INFO_CONSTRUCT(&_in);                                          \
            PMIX_LOAD_INFO(&_in, PMIX_SEND_HEARTBEAT, NULL, PMIX_POINTER);      \
            PMIx_Process_monitor_nb(&_in, PMIX_SUCCESS, NULL, 0, NULL, NULL);   \
            PMIX_INFO_DESTRUCT(&_in);                                           \
        } while(0)

Example
-------

    #define _GNU_SOURCE
    #include <stdbool.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <time.h>

    #include <pmix.h>

    static pmix_proc_t myproc;

    /* this is the event notification function we pass down below
     * when registering for general events - i.e.,, the default
     * handler. We don't technically need to register one, but it
     * is usually good practice to catch any events that occur */
    static void notification_fn(size_t evhdlr_registration_id,
                                pmix_status_t status,
                                const pmix_proc_t *source,
                                pmix_info_t info[], size_t ninfo,
                                pmix_info_t results[], size_t nresults,
                                pmix_event_notification_cbfunc_fn_t cbfunc,
                                void *cbdata)
    {
        if (NULL != cbfunc) {
            cbfunc(PMIX_EVENT_ACTION_COMPLETE, NULL, 0, NULL, NULL, cbdata);
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
        volatile int *active = (volatile int*)cbdata;

        if (PMIX_SUCCESS != status) {
            fprintf(stderr, "Client %s:%d EVENT HANDLER REGISTRATION FAILED WITH STATUS %d, ref=%lu\n",
                       myproc.nspace, myproc.rank, status, (unsigned long)evhandler_ref);
        }
        *active = status;
    }

    static void infocbfunc(pmix_status_t status,
                           pmix_info_t *info, size_t ninfo,
                           void *cbdata,
                           pmix_release_cbfunc_t release_fn,
                           void *release_cbdata)
    {
        volatile int *active = (volatile int*)cbdata;

        /* release the caller */
        if (NULL != release_fn) {
            release_fn(release_cbdata);
        }

        *active = status;
    }

    int main(int argc, char **argv)
    {
        int rc;
        pmix_value_t value;
        pmix_value_t *val = &value;
        pmix_proc_t proc;
        uint32_t nprocs, n;
        pmix_info_t *info, *iptr;
        bool flag;
        volatile int active;
        pmix_data_array_t *dptr;

        /* init us - note that the call to "init" includes the return of
         * any job-related info provided by the RM. */
        if (PMIX_SUCCESS != (rc = PMIx_Init(&myproc, NULL, 0))) {
            fprintf(stderr, "Client ns %s rank %d: PMIx_Init failed: %d\n", myproc.nspace, myproc.rank, rc);
            exit(0);
        }
        fprintf(stderr, "Client ns %s rank %d: Running\n", myproc.nspace, myproc.rank);


        /* register our default event handler - again, this isn't strictly
         * required, but is generally good practice */
        active = -1;
        PMIx_Register_event_handler(NULL, 0, NULL, 0,
                                    notification_fn, evhandler_reg_callbk, (void*)&active);
        while (-1 == active) {
            sleep(1);
        }
        if (0 != active) {
            fprintf(stderr, "[%s:%d] Default handler registration failed\n", myproc.nspace, myproc.rank);
            exit(active);
        }

        /* job-related info is found in our nspace, assigned to the
         * wildcard rank as it doesn't relate to a specific rank. Setup
         * a name to retrieve such values */
        PMIX_PROC_CONSTRUCT(&proc);
        (void)strncpy(proc.nspace, myproc.nspace, PMIX_MAX_NSLEN);
        proc.rank = PMIX_RANK_WILDCARD;

        /* get our universe size */
        if (PMIX_SUCCESS != (rc = PMIx_Get(&proc, PMIX_UNIV_SIZE, NULL, 0, &val))) {
            fprintf(stderr, "Client ns %s rank %d: PMIx_Get universe size failed: %d\n", myproc.nspace, myproc.rank, rc);
            goto done;
        }
        nprocs = val->data.uint32;
        PMIX_VALUE_RELEASE(val);
        fprintf(stderr, "Client %s:%d universe size %d\n", myproc.nspace, myproc.rank, nprocs);

        /* inform the RM that we are preemptible, and that our checkpoint methods are
         * "signal" on SIGUSR2 and event on PMIX_JCTRL_CHECKPOINT */
        PMIX_INFO_CREATE(info, 2);
        flag = true;
        PMIX_INFO_LOAD(&info[0], PMIX_JOB_CTRL_PREEMPTIBLE, (void*)&flag, PMIX_BOOL);
        /* can't use "load" to load a pmix_data_array_t */
        (void)strncpy(info[1].key, PMIX_JOB_CTRL_CHECKPOINT_METHOD, PMIX_MAX_KEYLEN);
        info[1].value.type = PMIX_DATA_ARRAY;
        dptr = (pmix_data_array_t*)malloc(sizeof(pmix_data_array_t));
        info[1].value.data.darray = dptr;
        dptr->type = PMIX_INFO;
        dptr->size = 2;
        PMIX_INFO_CREATE(dptr->array, dptr->size);
        rc = SIGUSR2;
        iptr = (pmix_info_t*)dptr->array;
        PMIX_INFO_LOAD(&iptr[0], PMIX_JOB_CTRL_CHECKPOINT_SIGNAL, &rc, PMIX_INT);
        rc = PMIX_JCTRL_CHECKPOINT;
        PMIX_INFO_LOAD(&iptr[1], PMIX_JOB_CTRL_CHECKPOINT_EVENT, &rc, PMIX_STATUS);

        /* since this is informational and not a requested operation, the target parameter
         * doesn't mean anything and can be ignored */
        active = -1;
        if (PMIX_SUCCESS != (rc = PMIx_Job_control_nb(NULL, 0, info, 2, infocbfunc, (void*)&active))) {
            fprintf(stderr, "Client ns %s rank %d: PMIx_Job_control_nb failed: %d\n", myproc.nspace, myproc.rank, rc);
            goto done;
        }
        while (-1 == active) {
            sleep(1);
        }
        PMIX_INFO_FREE(info, 2);
        if (0 != active) {
            fprintf(stderr, "Client ns %s rank %d: PMIx_Job_control_nb failed: %d\n", myproc.nspace, myproc.rank, rc);
            exit(active);
        }

        /* now request that this process be monitored using heartbeats */
        PMIX_INFO_CREATE(iptr, 1);
        PMIX_INFO_LOAD(&iptr[0], PMIX_MONITOR_HEARTBEAT, NULL, PMIX_POINTER);

        PMIX_INFO_CREATE(info, 3);
        PMIX_INFO_LOAD(&info[0], PMIX_MONITOR_ID, "MONITOR1", PMIX_STRING);
        n = 5;  // require a heartbeat every 5 seconds
        PMIX_INFO_LOAD(&info[1], PMIX_MONITOR_HEARTBEAT_TIME, &n, PMIX_UINT32);
        n = 2;  // two heartbeats can be missed before declaring us "stalled"
        PMIX_INFO_LOAD(&info[2], PMIX_MONITOR_HEARTBEAT_DROPS, &n, PMIX_UINT32);

        /* make the request */
        active = -1;
        if (PMIX_SUCCESS != (rc = PMIx_Process_monitor_nb(iptr, PMIX_MONITOR_HEARTBEAT_ALERT,
                                                          info, 3, infocbfunc, (void*)&active))) {
            fprintf(stderr, "Client ns %s rank %d: PMIx_Process_monitor_nb failed: %d\n", myproc.nspace, myproc.rank, rc);
            goto done;
        }
        while (-1 == active) {
            sleep(1);
        }
        PMIX_INFO_FREE(iptr, 1);
        PMIX_INFO_FREE(info, 3);
        if (0 != active) {
            fprintf(stderr, "Client ns %s rank %d: PMIx_Process_monitor_nb failed: %d\n", myproc.nspace, myproc.rank, rc);
            exit(active);
        }

        /* send a heartbeat */
        PMIx_Heartbeat();

        /* call fence to synchronize with our peers - no need to
         * collect any info as we didn't "put" anything */
        PMIX_INFO_CREATE(info, 1);
        flag = false;
        PMIX_INFO_LOAD(info, PMIX_COLLECT_DATA, &flag, PMIX_BOOL);
        if (PMIX_SUCCESS != (rc = PMIx_Fence(&proc, 1, info, 1))) {
            fprintf(stderr, "Client ns %s rank %d: PMIx_Fence failed: %d\n", myproc.nspace, myproc.rank, rc);
            goto done;
        }
        PMIX_INFO_FREE(info, 1);


      done:
        /* finalize us */
        fprintf(stderr, "Client ns %s rank %d: Finalizing\n", myproc.nspace, myproc.rank);
        if (PMIX_SUCCESS != (rc = PMIx_Finalize(NULL, 0))) {
            fprintf(stderr, "Client ns %s rank %d:PMIx_Finalize failed: %d\n", myproc.nspace, myproc.rank, rc);
        } else {
            fprintf(stderr, "Client ns %s rank %d:PMIx_Finalize successfully completed\n", myproc.nspace, myproc.rank);
        }
        fflush(stderr);
        return(0);
    }

Protoype Implementation
-----------------------

The PMIx library implementation is covered in the [Implement the
PMIx\_Job\_control\_nb support](https://github.com/pmix/pmix/pull/334)
pull request. The prototype was introduced into Open MPI as part of
[this PR](https://github.com/open-mpi/ompi/pull/3218).

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

