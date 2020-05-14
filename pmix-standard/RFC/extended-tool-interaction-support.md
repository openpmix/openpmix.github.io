---
layout: default
title: Extended Tool Interaction Support
---

RFC0010
=======

Amends and extends:

[RFC0001: Provide a mechanism by which tools can interact with a local
PMIx server that has opted to accept such
connections](https://github.com/pmix/RFCs/blob/master/RFC0001.md)

-   Adds support for tool connections to system-level PMIx servers \*
    Removes blocking form of PMIx\_Query client API \* Modifies
    server-to-RM interface
-   Redefines rank value from int to uint32
-   Defines and enforces rank and status data types distinct from
    standard int
-   Adds new user-facing structures
-   Modifies the pmix\_info\_t user-facing structure to differentiate
    *required* vs *optional* directives
-   Adds new PMIx\_Log\_nb API

Title
-----

Extension of Tool Interaction Support

Abstract
--------

An increasingly diverse collection of tools have expressed interest in
connecting to PMIx servers to obtain information on application
processes (placement, status, identification) and queue status, as well
as debugger support. This RFC contains a significant update of the prior
tool support described in
[RFC0001](https://github.com/pmix/RFCs/blob/master/RFC0001.md) that
impacts all three levels of interfaces (client, server, and host
resource manager).

Labels
------

\[EXTENSION\]\[CLIENT-API\]\[SERVER-API\]\[RM-INTERFACE\]

Action
------

\[APPROVED\]

Copyright Notice
----------------

Copyright (c) 2016 Intel, Inc. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

An increasingly diverse collection of tools have expressed interest in
connecting to PMIx servers to obtain information on application
processes (placement, status, identification) and queue status, as well
as debugger support. Supporting this range of activity requires the
following changes to the PMIx library:

-   Add support for tool connections to a specified system-level PMIx
    server. Although not required, environments can choose to launch a
    set of PMIx servers to support a given allocation – these servers
    will (if so instructed) provide a tool rendezvous point that is
    tagged with their pid and typically placed in an allocation-specific
    temporary directory to allow for possible multi-tenancy scenarios.
    However, login and other support nodes may not be utilized in
    allocations, and thus would not host a PMIx server – yet a
    PMIx-based tool operating on such nodes could be used to query
    system status, request job launch, and other system functions.

    Supporting such operations requires that a system-level PMIx
    connection be provided which is not associated with a specific user
    or allocation. A new key has been added to direct the PMIx server to
    expose a rendezvous point specifically for this purpose. Only one
    system-level rendezvous point (not tagged with a pid) is permitted
    per node, and placed in a system-level temporary directory to
    facilitate easier discovery. Keys for specifying the system- and
    allocation-specific temporary directories have been provided.

    As tools may find themselves in an environment where both system and
    allocation level PMIx servers are present, keys have been provided
    to direct the tool connection procedure to select the desired type
    of server (system or allocation). In the absence of direction, the
    tool will first look for a system-level connection, and then seek a
    session-level connection, returning an error if multiple allocation
    server rendezvous points are discovered and the caller failed to
    specify a pid.

-   Redefine the rank value from int to uint32. The expansion of
    requests for information complicated the need to specify the
    processes whose information was being requested. Large arrays of
    values raise questions of scalability, and created a desire for the
    definition of *special* rank values that could convey a particular
    well-defined pattern – e.g., definition of a rank value to represent
    all ranks on a given node. Additional concerns were raised regarding
    future demands on overall application sizes. Thus, the rank type was
    changed from the current *int* to *uint32\_t* and given a dedicated
    typedef in case there are any future changes. Special rank values
    indicating grouping will be taken from the top of this range,
    beginning with PMIX\_RANK\_WILDCARD at UINT32\_MAX-1.

    **NOTE:** "Future proofing" the new definition requires strict
    enforcement of the pmix\_rank\_t type definition within the PMIx
    library code, particularly during use of pack/unpack routines. Thus,
    data provided by the host resource manager (e.g., in the call to
    PMIx\_Register\_nspace) will likewise be subject to these strict
    rules.

-   Add process state definitions for returning the state of a queried
    process. An initial, hardly exhaustive, set of definitions has been
    provided.

    **Note:** This is a "best-fit" approximation of the actual process
    state based on fitting the actual resource manager-defined state to
    the closest corresponding PMIx definition. It is expected that the
    RM community will request refinement of these defined states over
    time to better reflect the actual process state in response to user
    requests.

-   Add three new user-level structures:
    -   pmix\_proc\_info\_t – contains information on a process that is
        consistent with the needs of debuggers. This includes:
        -   pmix\_proc\_t – the namespace and rank of the process
        -   hostname – name of the host where this process is executing
        -   executable\_name – name of the binary being executed
        -   pid – the Unix pid of the process
        -   exit\_code – the returned status from the application, if it
            has terminated
        -   state – the process state as per the above definition

    -   pmix\_query\_t – a structure designed to pass a request for
        information that consists of:
        -   keys – a NULL-terminated array of keys describing the data
            being requested. This can consist of PMIx-standard keys
            and/or RM-specific keys
        -   qualifiers – an array of pmix\_info\_t values that provide
            additional constraints or guidance for the data search
        -   nqual – the number of qualifiers in the array

    -   pmix\_data\_array\_t – used to pass an arbitrary array of data
        to/from the client. Queries for information frequently result in
        multiple answers for a given key. For example, a query for
        PMIX\_QUERY\_PROC\_TABLE will return an array of
        pmix\_proc\_info\_t structures, one for each process in the
        specified namespace. Thus, the returned value for the query will
        contain a single pmix\_info\_t structure containing the
        PMIX\_QUERY\_PROC\_TABLE key, and a value consisting of a
        pmix\_data\_array\_t filled with pmix\_proc\_info\_t structures.
        The pmix\_data\_array\_t structure contains:

        -   type – the type of data in the array
        -   size – number of data elements
        -   array – the array of elements

        **NOTE:** addition of the generalized pmix\_data\_array\_t
        structure resulted in deprecation of the pmix\_info\_array\_t
        definition as being a special case of the more general
        definition

-   Modify the PMIx\_Query\_nb interface to take an array of the new
    query structures. The callback function used to return the results
    of the request will consist of a pmix\_info\_t corresponding to each
    input pmix\_query\_t structure, with the pmix\_value\_t field
    containing either a unique value or a pmix\_data\_array\_t of
    values. New query-related PMIx-standard key definitions have also
    been added.

    For example, a request for the list of peers executing on a node
    (key=PMIX\_LOCAL\_PEERS) requires that one also specify the node
    being referenced – the nodeid would therefore be passed as a
    qualifer. Note that a similar request for the list of peers on
    multiple nodes can be accomplished by providing an array of
    qualifiers that specifies the nodeid of the nodes, as shown below:

        pmix_query_t query;
        uint32_t nodeid; size_t n;

        PMIX_QUERY_CONSTRUCT(&query, 1); // initialize the structure, creating space for 1 key
        query.keys[0] = strdup(PMIX_LOCAL_PROCS); // request the procs running on a node
        PMIX_INFO_CREATE(query.qualifiers, 2); // specify two nodes whose info we want
        nodeid = 5;
        PMIX_LOAD_INFO(&query.qualifiers[0], PMIX_NODEID, &nodeid, PMIX_UINT32);
        nodeid = 7;
        PMIX_LOAD_INFO(&query.qualifiers[1], PMIX_NODEID, &nodeid, PMIX_UINT32);
        PMIx_Query_info_nb(&query, 1, results_cbfunc, &query); // execute the query

    The callback function for this request would receive a single
    pmix\_info\_t structure containing a key of PMIX\_LOCAL\_PROCS and a
    value that contained a pmix\_data\_array\_t of pmix\_proc\_t
    structures, each structure containing the namespace and rank of a
    proc on one of the specified nodes. Note that the results would not
    indicate which node each proc was on – to obtain that level of
    detail, the requestor should have provided two query structures,
    each with a single qualifier specifying the node of interest.

    **NOTE: the blocking form of the PMIx\_Query API has been remove
    from the PMIx standard.** This action was taken due to the
    difference between the pmix\_query\_t input structures and the array
    of pmix\_info\_t structures returned by the query.

    **NOTE:** The *query* interface between the PMIx server library and
    the host RM has been modified to pass the new pmix\_query\_t
    structure.

-   Add a bit-mapped uint32 *directives* field to the pmix\_info\_t. The
    expanded use of pmix\_info\_t structures as directives required
    addition of at least a *required* vs *optional* stipulation.
    Provision for future additional uses was provided by extending the
    field to a uint32\_t size.

-   Replace the enum types for persistence, scope, data range, data
    type, and status with \#define values. This enables extension of the
    PMIx-standard values by 3rd parties to support environment-specific
    capabilities.

    **NOTE:** "Future proofing" these new definitions requires strict
    enforcement of their definitions within the PMIx library code,
    particularly during use of pack/unpack routines. Thus, values passed
    to/from the host resource manager will likewise be subject to these
    strict rules.

-   Add new “pretty-print” support functions for proc state, scope,
    persistence, data range, info directives, and data types. Returning
    of simple integer values can make debugging code difficult by
    requiring constant references to the pmix\_common.h header. The
    provided functions translate the given value to a corresponding,
    user-friendly string suitable for printing.

-   Split the handling of PMIX\_HOSTNAME requests to more clearly
    articulate what is being requested and returned. The PMIX\_HOSTNAME
    key returned a value that depended on the rank of the process in the
    PMIx\_Get request. This proved to be confusing, and therefore the
    definition of the key has been streamlined to support only one
    use-case, and new keys added to handle the other use-cases.

-   Add new PMIx\_Log\_nb API for requesting logging of provided data in
    some global data store or to standard output locations (e.g., stderr
    or syslog), subject to available services from the host environment.
    The PMIx library will incorporate direct support for a "generalized
    data store" in a future release. Keys have been provided by which
    the logging request can direct the data to specific channels on an
    as-available basis. The host RM interface has been extended through
    the addition of a "log" interface by which client requests that are
    not directly supported by the PMIx library can be passed to the host
    RM for handling – e.g., when the logging data is directed to the
    stderr or stdout channels.

Code examples for debugger launch/attach and for a generic PMIx-base
application launch tool have been added to the PMIx library’s "example"
directory to help developers understand the use of these new
capabilities.

Protoype Implementation
-----------------------

The PMIx library implementation is covered in the [Extend the PMIx\_Tool
support](https://github.com/pmix/master/pull/122) pull request. The
prototype has been tested against Open MPI as referenced in an upcoming
pull request.

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

