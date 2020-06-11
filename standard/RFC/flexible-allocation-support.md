---
layout: default
title: Flexible Allocation Support
---

RFC0005
=======

Title
-----

APIs for Flexible Allocation Support

Abstract
--------

This RFC adds an API and associated keys to support the request for
allocation of additional resources, and the return of currently
allocated resources to the scheduler.

Labels
------

\[EXTENSION\]\[CLIENT-API\]\[RM-INTERFACE\]

Action
------

\[ACCEPTED\]

Copyright Notice
----------------

Copyright 2017 Intel, Inc. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

Interest in dynamic resource management has increased as new programming
models continue to emerge in the high-performance computing and data
analytics areas. Of primary concern is the enablement of
application-directed resource changes in partnership with the scheduler.
Several broad categories are envisioned, including the ability to:

-   request allocation of additional resources, including memory,
    bandwidth, and compute. This should be accomplished in a
    non-blocking manner so that the application can continue to progress
    while waiting for resources to become available. Note that the new
    allocation will be disjoint from (i.e., not affiliated with) the
    allocation of the requestor – thus the termination of one allocation
    will not impact the other.

-   extend the reservation on currently allocated resources, subject to
    scheduling availability and priorities. This includes extending the
    time limit on current resources, and/or requesting additional
    resources be allocated to the requesting job. Any additional
    allocated resources will be considered as part of the current
    allocation, and thus will be released at the same time.

-   release currently allocated resources that are no longer required.
    This is intended to support partial release of resources since all
    resources are normally released upon termination of the job. The
    identified use-cases include resource variations across discrete
    steps of a workflow, as well as applications that spawn sub-jobs
    and/or dynamically grow/shrink over time

-   "lend" resources back to the scheduler with an expectation of
    getting them back at some later time in the job. This can be a
    proactive operation (e.g., to save on computing costs when resources
    are temporarily not required), or in response to scheduler requests
    in lieue of preemption. A corresponding ability to "reacquire"
    resources previously released is included.

There is one proposed new client-side API, with an accompanying
definition of some new directives:

    typedef uint8_t pmix_alloc_directive_t;

    #define PMIX_ALLOC_NEW          1  // new allocation is being requested. The resulting allocation will be
                                       // disjoint (i.e., not connected in a job sense) from the requesting allocation
    #define PMIX_ALLOC_EXTEND       2  // extend the existing allocation, either in time or as additional resources
    #define PMIX_ALLOC_RELEASE      3  // release part of the existing allocation. Attributes in the accompanying
                                       // pmix\_info\_t array may be used to specify permanent release of the
                                       // identified resources, or "lending" of those resources for some period
                                       // of time.
    #define PMIX_ALLOC_REACQUIRE    4  // reacquire resources that were previously "lent" back to the scheduler
    #define PMIX_ALLOC_CANCEL       5  // cancel an allocation request (as specified by PMIX_ALLOC_ID) that is still in the queue

    pmix_status_t PMIx_Allocation_request_nb(pmix_alloc_directive_t directive,
                                             pmix_info_t *info, size_t ninfo,
                                             pmix_info_cbfunc_t cbfunc, void *cbdata);

The callback function provides a status to indicate whether or not the
request was granted, and to provide some information as to the reason
for any denial. If successful, details on the results of the request
(e.g., the names of nodes allocated per the request, the identifiers of
resources that were reclaimed by the scheduler, or how much additional
time was granted for the current job) will be provided in the array of
*pmix\_info\_t* values. If non-NULL, then the specified release\_fn must
be called when the callback function completes – this will be used to
release any provided *pmix\_info\_t* array.

Implementers are welcome to add directives in their own environments
(starting with the defined *PMIX\_ALLOC\_EXTERNAL* value), or to submit
new values for inclusion in future releases of the standard. Currently
identified attributes (and their associated data type) that can be used
to describe resources and/or steer behavior include:

    /* query attributes */
    #define PMIX_QUERY_ALLOC_STATUS             "pmix.query.alloc"      // (char*) string identifier of the allocation whose status
                                                                        //         is being requested
    /* status code for notification of allocation events */
    #define PMIX_NOTIFY_ALLOC_COMPLETE          (PMIX_ERR_BASE - 15)

    /* attributes for allocation support */
    #define PMIX_ALLOC_ID                       "pmix.alloc.id"         // (char*) provide a string identifier for this allocation request
                                                                        //         which can later be used to query status of the request
    #define PMIX_ALLOC_NUM_NODES                "pmix.alloc.nnodes"     // (uint64_t) number of nodes
    #define PMIX_ALLOC_NODE_LIST                "pmix.alloc.nlist"      // (char*) regex of specific nodes
    #define PMIX_ALLOC_NUM_CPUS                 "pmix.alloc.ncpus"      // (uint64_t) number of cpus
    #define PMIX_ALLOC_NUM_CPU_LIST             "pmix.alloc.ncpulist"   // (char*) regex of #cpus for each node
    #define PMIX_ALLOC_CPU_LIST                 "pmix.alloc.cpulist"    // (char*) regex of specific cpus indicating the cpus involved.
    #define PMIX_ALLOC_MEM_SIZE                 "pmix.alloc.msize"      // (float) number of Mbytes
    #define PMIX_ALLOC_NETWORK                  "pmix.alloc.net"        // (array) array of pmix_info_t describing network resources. If not
                                                                        //         given as part of an info struct that identifies the
                                                                        //         impacted nodes, then the description will be applied
                                                                        //         across all nodes in the requestor's allocation
    #define PMIX_ALLOC_NETWORK_ID               "pmix.alloc.netid"      // (char*) name of network
    #define PMIX_ALLOC_BANDWIDTH                "pmix.alloc.bw"         // (float) Mbits/sec
    #define PMIX_ALLOC_NETWORK_QOS              "pmix.alloc.netqos"     // (char*) quality of service level
    #define PMIX_ALLOC_TIME                     "pmix.alloc.time"       // (uint32_t) time in seconds

Requests can use arrays of attributes to fully describe the request –
each info key might contain the following:

    PMIX_NETWORK -> value: array
                    -> info[0].key = PMIX_NETWORK_ID
                       info[0].value = "eth0"
                    -> info[1].key = PMIX_BANDWIDTH
                       info[1].value = 1.386

indicating a request for 1.386Mbits/sec of bandwidth on the eth0
network, or

    PMIX_CPUS -> value: array
                    -> info[0].key = PMIX_NODE_LIST
                       info[0].value = "node1,node2"
                    -> info[1].key = PMIX_NUM_CPU_LIST
                       info[1].value = "5,3"

to request 5 cpus on node1 and 3 cpus on node2, or simply

    PMIX_NUM_NODES -> value = 12

along with a directive of *PMIX\_ALLOC\_RELEASE* to indicate that 12
nodes are to be released to the scheduler. In this last case, the
expectation is that any 12 nodes, excluding the one where the request is
originating from, can be recovered by the scheduler as the requestor did
not specify a node list.

Each allocation request can specify a user-created "allocation ID"
string. This allows the initiator to issue follow-on requests (e.g., for
status updates via the PMIx\_Query function), or to issue a subsequent
PMIx\_Allocate\_request\_nb call to cancel the request. A request to
cancel allocation requests that does not specify an allocation ID will
result in cancellation of *all* outstanding requests associated with the
requestor.

Note that the "required" flag in the pmix\_info\_t structures provided
in allocation requests can be used to indicate that a request is to be
rejected if the specified resources are not available. Likewise, marking
the attribute as "not required" indicates that the specification is
provisional – i.e., desired, but not required.

Notification requests are complete when the callback function is
executed. However, this will only occur in the process that initiated
the request. Two methods are provided for other processes to learn when
an allocation operation is complete (whether successful or not):

1.  status of the request can be "polled" using the PMIx\_Query\_nb
    function
2.  the process can register for event notification upon completion of
    the allocation operation using the PMIX\_ERR\_ALLOC\_COMPLETE status

In both cases, the process can specify the application request ID in the
qualifiers. The lack of a specific ID will result in a status report or
event notification for all allocation requests associated with the
process.

On the server side, there is also a new callback function that
corresponds to the client-side API:

    typedef pmix_status_t (*pmix_server_alloc_fn_t)(const pmix_proc_t *client,
                                                    pmix_alloc_directive_t directive,
                                                    const pmix_info_t data[], size_t ndata,
                                                    pmix_info_cbfunc_t cbfunc, void *cbdata);

The client’s call to *PMIx\_Allocation\_request* is communicated to the
local PMIx server, which (if the host RM supplies the callback function)
passes the directive and info array to the host. In addition, the server
identifies the requestor to the host so that proper authorizations can
be evaluated. Note that the host RM is responsible for determining and
applying any applicable authorization policies. The PMIx server is
required to maintain the info array until the host RM executes the
provided callback function.

Example
-------

The following code exercises the new API plus queries and events for the
allocation status:

    #include <stdbool.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <time.h>

    #include <pmix.h>

    /* define a structure for collecting returned
     * info from an allocation request */
    typedef struct {
        volatile bool active;
        pmix_info_t *info;
        size_t ninfo;
    } mydata_t;

    static volatile bool waiting_for_allocation = true;

    /* this is a callback function for the PMIx_Query and
     * PMIx_Allocate APIs. The query will callback with a status indicating
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
    static void infocbfunc(pmix_status_t status,
                           pmix_info_t *info, size_t ninfo,
                           void *cbdata,
                           pmix_release_cbfunc_t release_fn,
                           void *release_cbdata)
    {
        mydata_t *mq = (mydata_t*)cbdata;
        size_t n;

        fprintf(stderr, "Allocation request returned %s", PMIx_Error_string(status));

        /* save the returned info - the PMIx library "owns" it
         * and will release it and perform other cleanup actions
         * when release_fn is called */
        if (0 < ninfo) {
            PMIX_INFO_CREATE(mq->info, ninfo);
            mq->ninfo = ninfo;
            for (n=0; n < ninfo; n++) {
                fprintf(stderr, "Transferring %s\n", info[n].key);
                PMIX_INFO_XFER(&mq->info[n], &info[n]);
            }
        }

        /* let the library release the data and cleanup from
         * the operation */
        if (NULL != release_fn) {
            release_fn(release_cbdata);
        }

        /* release the block */
        mq->active = false;
    }

    /* this is an event notification function that we explicitly request
     * be called when the PMIX_ERR_ALLOC_COMPLETE notification is issued.
     * We could catch it in the general event notification function and test
     * the status to see if it was "alloc complete", but it often is simpler
     * to declare a use-specific notification callback point. In this case,
     * we are asking to know when the allocation request completes */
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
        /* flag that the allocation is complete so we can exit */
        waiting_for_allocation = false;
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
            fprintf(stderr, "EVENT HANDLER REGISTRATION FAILED WITH STATUS %d, ref=%lu\n",
                    status, (unsigned long)evhandler_ref);
        }
        *active = status;
    }

    int main(int argc, char **argv)
    {
        pmix_proc_t myproc;
        int rc;
        pmix_value_t value;
        pmix_value_t *val = &value;
        pmix_proc_t proc;
        uint32_t nprocs;
        pmix_info_t *info;
        uint64_t nnodes = 12;
        mydata_t mydata;
        pmix_query_t *query;
        char *myallocation = "MYALLOCATION";
        volatile int active;
        pmix_status_t code = PMIX_ERR_ALLOC_COMPLETE;

        /* init us */
        if (PMIX_SUCCESS != (rc = PMIx_Init(&myproc, NULL, 0))) {
            fprintf(stderr, "Client ns %s rank %d: PMIx_Init failed: %d\n", myproc.nspace, myproc.rank, rc);
            exit(0);
        }
        fprintf(stderr, "Client ns %s rank %d: Running\n", myproc.nspace, myproc.rank);

        /* get our universe size */
        PMIX_PROC_CONSTRUCT(&proc);
        (void)strncpy(proc.nspace, myproc.nspace, PMIX_MAX_NSLEN);
        proc.rank = PMIX_RANK_WILDCARD;
        if (PMIX_SUCCESS != (rc = PMIx_Get(&proc, PMIX_UNIV_SIZE, NULL, 0, &val))) {
            fprintf(stderr, "Client ns %s rank %d: PMIx_Get universe size failed: %d\n", myproc.nspace, myproc.rank, rc);
            goto done;
        }
        nprocs = val->data.uint32;
        PMIX_VALUE_RELEASE(val);
        fprintf(stderr, "Client %s:%d universe size %d\n", myproc.nspace, myproc.rank, nprocs);

        /* initialize the return info struct */
        mydata.info = NULL;
        mydata.ninfo = 0;

        if (0 == myproc.rank) {
            /* try to get an allocation */
            mydata.active = true;
            PMIX_INFO_CREATE(info, 2);
            PMIX_INFO_LOAD(&info[0], PMIX_ALLOC_NUM_NODES, &nnodes, PMIX_UINT64);
            PMIX_INFO_LOAD(&info[0], PMIX_ALLOC_ID, myallocation, PMIX_STRING);
            if (PMIX_SUCCESS != (rc = PMIx_Allocation_request_nb(PMIX_ALLOC_NEW, info, 2, infocbfunc, NULL))) {
                fprintf(stderr, "Client ns %s rank %d: PMIx_Allocation_request_nb failed: %d\n", myproc.nspace, myproc.rank, rc);
                goto done;
            }
            while (mydata.active) {
                usleep(10);
            }
            PMIX_INFO_FREE(info, 2);
            if (NULL != mydata.info) {
                PMIX_INFO_FREE(mydata.info, mydata.ninfo);
            }
        } else if (1 == myproc.rank) {
            /* register a handler specifically for when the allocation
             * operation completes */
            PMIX_INFO_CREATE(info, 1);
            PMIX_INFO_LOAD(&info[0], PMIX_ALLOC_ID, myallocation, PMIX_STRING);
            active = -1;
            PMIx_Register_event_handler(&code, 1, info, 1,
                                        release_fn, evhandler_reg_callbk, (void*)&active);
            while (-1 == active) {
                usleep(10);
            }
            if (0 != active) {
                exit(active);
            }
            PMIX_INFO_FREE(info, 1);
            /* now wait to hear that the request is complete */
            while (waiting_for_allocation) {
                usleep(10);
            }
        } else {
            /* I am not the root rank, so let me wait a little while and then
             * query the status of the allocation request */
            usleep(10);
            PMIX_QUERY_CREATE(query, 1);
            PMIX_ARGV_APPEND(query[0].keys, PMIX_QUERY_ALLOC_STATUS);
            PMIX_INFO_CREATE(query[0].qualifiers, 1);
            PMIX_INFO_LOAD(&query[0].qualifiers[0], PMIX_ALLOC_ID, myallocation, PMIX_STRING);
            mydata.active = true;
            if (PMIX_SUCCESS != (rc = PMIx_Query_info_nb(query, 1, infocbfunc, (void*)&mydata))) {
                fprintf(stderr, "PMIx_Query_info failed: %d\n", rc);
                goto done;
            }
            while (mydata.active) {
                usleep(10);
            }
            PMIX_QUERY_FREE(query, 1);
        }

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
PMIx\_Allocate\_request\_nb
support](https://github.com/pmix/master/pull/314) pull request. The
prototype has been tested in the PMIx Reference Server as part of [this
PR](https://github.com/rhc54/psrvr/pull/4).

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

