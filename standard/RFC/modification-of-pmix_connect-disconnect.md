---
layout: default
title: Modification of PMIX_Connect/Disconnect
---

RFC0003
=======

Title
-----

Modification of the PMIx\_Connect and PMIx\_Disconnect functions to
support new proposed programming model behavior

Abstract
--------

New programming models, and changes to existing programming models, are
emerging that desire the ability to more flexibly connect and disconnect
processes from groups. This proposed change will:

-   modify two existing client-side APIs (PMIx\_Connect and
    PMIx\_Disconnect) plus their corresponding resource manager
    interfaces

-   add several new info keys

-   modify the PMIx server library to track the nspaces of connected
    groups

Labels
------

\[MODIFICATION\]\[BEHAVIOR\]\[CLIENT-API\]\[RM-INTERFACE\]

Action
------

\[APPROVED\]

Copyright Notice
----------------

Copyright (c) 2016-2017 Intel, Inc. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

The current connect and disconnect APIs reflect the needs of
bulk-synchronous programming models such as today’s MPI. Both require
that the operation be executed as a collective, with all specified
processes participating in the operation prior to it being declared
complete. In addition, the standard requires that the host resource
manager (RM) treat the specified processes as a new "group" when
considering notifications, termination, and other operations.

Since the original definition was released, users and RM developers have
noted that the PMIx\_Connect operation fails to return a new nspace
corresponding to the "group" that was just created. Creating a new
nspace for the group would allow users to perform group operations
(e.g., PMIx\_Fence and PMIx\_Notify\_event). RM’s need to create some
kind of identifier for the group for tracking purposes anyway – it would
be beneficial if that could be passed down to the caller. This would
also assist the RM when processing the PMIx\_Disconnect request as the
caller could just specify the new nspace.

In addition, programming libraries have continued to evolve towards more
of an asynchronous model where processes regularly aggregate into groups
that subsequently dissolve after completing some set of operations.
These new approaches would benefit from an ability to notify other
processes of a desire to aggregate, and to allow the aggregation process
itself to take place asynchronously.

Accordingly, this RFC proposes to modify the current
PMIx\_Connect\[\_nb\], PMIx\_Disconnect\[\_nb\], and their associated
server-RM interfaces to accommodate the requests. It is recognized that
this causes a backward-compatibility issue. However, only one library
currently uses these interfaces (and they are accessed via an
abstraction layer that can hide the changes) – thus, the disruption
should be minimal provided these changes can be adopted and implemented
before other libraries adopt them.

Some additional info keys are provided for the revised operations:

-   PMIX\_CONNECT\_NOTIFY\_EACH: generate a local event notification
    using the PMIX\_PROC\_HAS\_CONNECTED event each time a process
    connects, and the PMIX\_PROC\_HAS\_DISCONNECTED event each time a
    process disconnects. The PMIx server is responsible for generating
    these events.

-   PMIX\_CONNECT\_NOTIFY\_REQ: notify each of the indicated procs that
    they are requested to connect using the PMIX\_CONNECT\_REQUESTED
    event. The PMIx server is responsible for generating this event.

-   PMIX\_CONNECT\_OPTIONAL: participation is optional – do not return
    error if procs terminate without having connected. This is the joint
    responsibility of the host RM (to notify if remote procs terminate
    early) and the PMIx server.

-   PMIX\_CONNECT\_EARLY\_TERM\_ALLOWED: do not generate an error if a
    process terminates without disconnecting. The host RM and PMIx
    server are responsible for adjusting completion requirements on any
    ongoing or future collectives for this nspace.

-   PMIX\_CONNECT\_XCHG\_ONLY: ensure that all participating processes
    have a copy of the job-level info from each nspace, but do not
    assign a new nspace and rank

Note that any single process *can* be simultaneously engaged in multiple
connect operations. For scalability, PMIx does not use a collective to
assign an identifier to the connect operation. Instead, it is expected
that the provided array of process IDs will serve to identify a specific
PMIx\_Connect operation. Ordering of processes within the array is
disregarded. PMIX\_RANK\_WILDCARD can be used to indicate the
participation of all processes within that nspace.

It is possible that multiple PMIx\_Connect operations could operate in
parallel involving the same processes. Examples might include calls
stemming from different threads, or from different libraries included by
the application. Accordingly, the following attribute is defined to
allow the application to provide its own operation identifier:

-   PMIX\_CONNECT\_ID: an application-provided string identifier for a
    PMIx\_Connect operation.

This identifier will be used in addition to the array of participating
process identifiers as a means of uniquely identifying multiple parallel
operations. Note that *all* partitipants are required to call
PMIx\_Connect with the same PMIX\_CONNECT\_ID attribute value.

It is also possible that connect operations could span processes on
multiple clusters, each controlled by an independent resource manager
instance. In such cases, the nspace is no longer guaranteed to be unique
across clusters, thereby leading to potential confusion in the process
identifiers. Accordingly, this RFC defines a method for resolving the
potential nspace overlap by modifying the nspace value for a given
process identifier to include a "cluster identifier" – a string name for
the cluster that is provided by the host RM via the PMIX\_CLUSTER\_ID
attribute. In the case where a process is known to exist on a remote
cluster, the cluster identifier shall be prepended to the nspace,
separated by a colon (‘:’). A macro is provided to assist in assembling
and parsing the combined identifer.

Of course, specifying the cluster identifier and nspace assigned to an
application potentially executing on a remote cluster requires that one
first determine that this is the case and obtain the required identifier
values. PMIx and the host RM do not provide a direct mechanism for
resolving this question. Instead, applications are directed to the
PMIx\_Publish and PMIx\_Lookup functions for executing an appropriate
rendezvous protocol between the applications.

Thus, the procedure for executing a connect that involves processes on
multiple clusters and includes the possibility that more than one
identical collection of processes could be executing the operation in
parallel might look like the following (in this example, the call is
being made on cluster A and involves processes also located on cluster
B):

    pmix_info_t *info;
    pmix_proc_t proc, procs[2];
    pmix_value_t *val;
    char *myclusterid, *clusterB;
    char myid[PMIX_MAX_NSLEN+1], remote_nspace[PMIX_MAX_NSLEN+1], newnspace[PMIX_MAX_NSLEN+1];
    pmix_pdata_t pdata;
    pmix_rank_t newrank;

    /* get my cluster ID */
    PMIX_PROC_LOAD(&proc, mynspace, PMIX_RANK_WILDCARD);
    PMIx_Get(&proc, PMIX_CLUSTER_ID, NULL, 0, &val);
    myclusterid = strdup(val->data.string);
    PMIX_VALUE_RELEASE(val);

    /* construct an ID for me that includes my nspace and cluster ID */
    PMIX_MULTICLUSTER_NSPACE_CONSTRUCT(myid, myclusterid, mynspace);

    /* publish that value using a key that my remote partner knows */
    PMIX_INFO_CREATE(info, 2);
    PMIX_INFO_LOAD(&info[0], "myrendezvouskey", myid, PMIX_STRING);
    PMIX_INFO_LOAD(&info[1], PMIX_RANGE, PMIX_RANGE_GLOBAL, PMIX_DATA_RANGE);
    PMIx_Publish(info, 2);
    PMIX_INFO_FREE(info, 2);

    /*  lookup the corresponding ID published by my remote partner */
    PMIX_PDATA_CONSTRUCT(&pdata);
    pdata.key = strdup("remoterendezvouskey");
    PMIx_Lookup(&pdata, 1);
    remoteid = strdup(pdata->value.data.string);
    PMIX_PDATA_DESTRUCT(&pdata);

    /* construct the process identifier array - for this example, we assume all processes
     * in each nspace are participating */
    PMIX_PROC_LOAD(&procs[0], myid, PMIX_RANK_WILDCARD);
    PMIX_PROC_LOAD(&procs[0], remoteid, PMIX_RANK_WILDCARD);

    /* pass a unique identifier for this operation */
    PMIX_INFO_CONSTRUCT(&info)
    PMIX_INFO_LOAD(&info, PMIX_CONNECT_ID, "myconnect", PMIX_STRING);

    /* connect the two groups of processes */
    PMIx_Connect(procs, 2, info, ninfo, newnspace, &newrank);
    PMIX_INFO_DESTRUCT(&info);

    /* cleanup */
    free(myclusterid);
    free(remoteid);

The following APIs are included in this RFC.

#### PMIx\_Connect

Record the specified processes as "connected". Both blocking and
non-blocking versions are provided. This means that the resource manager
should treat the failure of any process in the specified group as a
reportable event, and take appropriate action. Note that different
resource managers may respond to failures in different manners.

Unless the PMIX\_CONNECT\_XCHG\_ONLY attribute is provided, the host RM
will assign a unique nspace to the resulting process group. The new
nspace must be provided when disconnecting from the group. All processes
are required to disconnect from the nspace prior to terminating unless
the PMIX\_CONNECT\_EARLY\_TERM\_ALLOWED directive is provided.

As in the case of the fence operation, the info array can be used to
pass user-level directives regarding the algorithm to be used for the
collective operation involved in the "connect", timeout constraints, and
other options available from the host RM.

The server is required to return any job-level info for the connecting
processes that they might not already have – i.e., if the connect
request involves processes from different nspaces, then each process
shall receive the job-level info from those nspaces other than their
own.

The blocking form of this call must provide a character array of size
PMIX\_MAX\_NSLEN+1 for the assigned nspace of the resulting group, and a
pointer to an pmix\_rank\_t location where the new rank of this process
in the assigned nspace can be returned. Calls will return once the
specified operation is complete (i.e., all participants have called
PMIx\_Connect).

    PMIX_EXPORT pmix_status_t PMIx_Connect(const pmix_proc_t procs[], size_t nprocs,
                                           const pmix_info_t info[], size_t ninfo,
                                           char nspace[], pmix_rank_t *newrank);

The callback function for the non-blocking form of the PMIx\_Connect
operation will be called once the operation is complete. By default, any
participant that fails to call "connect" prior to terminating will cause
the operation to return a "failed" status to all other participants –
this can be modified by including the PMIX\_CONNECT\_OPTIONAL directive.

    /* define a callback function for calls to PMIx_Connect_nb - the function
     * will be called upon completion of the command. The status will indicate
     * whether or not the connect operation succeeded. The nspace will contain
     * the new identity assigned by the host RM to the specified group of
     * processes, and the rank will be the rank of this process within that new
     * group. Note that the returned nspace value may be
     * released by the library upon return from the callback function, so
     * the receiver must copy it if it needs to be retained */
    typedef void (*pmix_connect_cbfunc_t)(pmix_status_t status,
                                          char nspace[], int rank,
                                          void *cbdata);

    PMIX_EXPORT pmix_status_t PMIx_Connect_nb(const pmix_proc_t procs[], size_t nprocs,
                                              const pmix_info_t info[], size_t ninfo,
                                              pmix_connect_cbfunc_t cbfunc, void *cbdata);

#### PMIx\_Disconnect

Disconnect this process from a specified nspace. An error will be
returned if the specified nspace is not recognized. The info array is
used as above.

Processes that terminate while connected to other processes will
generate a "termination error" event that will be reported to any
process in the connected group that has registered for such events.
Calls to "disconnect" that include the PMIX\_CONNECT\_NOTIFY\_EACH info
key will cause other processes in the nspace to receive an event
notification of the disconnect, if they are registered for such events.

    PMIX_EXPORT pmix_status_t PMIx_Disconnect(const char nspace[],
                                              const pmix_info_t info[], size_t ninfo);

    PMIX_EXPORT pmix_status_t PMIx_Disconnect_nb(const char nspace[],
                                                 const pmix_info_t info[], size_t ninfo,
                                                 pmix_op_cbfunc_t cbfunc, void *cbdata);

#### RM-Interface: Connect

Record the specified processes as "connected". This means that:

-   the resource manager should treat the specified group as a group
    when reporting events.

-   processes can address the group by the newly assigned nspace when
    passing requests

-   the server (in partnership with the host RM) shall provide a copy of
    job-level info to each process for any nspace that process does not
    yet know about

As in the case of the fence operation, the info array can be used to
pass user-level directives regarding the algorithm to be used for the
collective operation involved in the "connect", timeout constraints, and
other options available from the host RM.

The callback function will be called once the operation is complete. By
default, any participant that fails to call "connect" prior to
terminating will cause the operation to return a "failed" status to all
other participants.

    typedef pmix_status_t (*pmix_server_connect_fn_t)(const pmix_proc_t procs[], size_t nprocs,
                                                      const pmix_info_t info[], size_t ninfo,
                                                      pmix_connect_cbfunc_t cbfunc, void *cbdata);

#### RM-Interface: Disconnect

Disconnect this process from a specified nspace. An error will be
returned if the specified nspace is not recognized. The info array is
used as above.

Processes that terminate while connected to other processes will
generate a "termination error" event that will (in the absence of any
provided directive) be reported to any process in the connected group
that has registered for such events. Calls to "disconnect" that include
the PMIX\_CONNECT\_NOTIFY\_EACH info key will cause other processes in
the nspace to receive an event notification of the disconnect, if they
are registered for such events.

    typedef pmix_status_t (*pmix_server_disconnect_fn_t)(const char nspace[],
                                                         const pmix_info_t info[], size_t ninfo,
                                                         pmix_op_cbfunc_t cbfunc, void *cbdata);

Protoype Implementation
-----------------------

The PMIx library implementation is covered in the [Modification of connect/disconnect API](https://github.com/pmix/pmix/pull/69) pull
request.

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

