---
layout: default
title: Basic Tools Interaction Mechanism
---

RFC0001
=======

Amended and extended by [RFC0010: Extension of Tool Interaction Support](https://github.com/pmix/RFCs/blob/master/RFC0010.md)

Title
-----

Provide a mechanism by which tools can interact with a local PMIx server
that has opted to accept such connections.

Abstract
--------

Tools may want to connect to PMIx to query the resource manager for
information such as job status and system state, or to request that jobs
be spawned or an allocation be created. This RFC proposes a method by
which a PMIx server can declare itself available for such services, and
a tool can rendezvous with that server to initiate the interaction.

*NOTE: The host resource manager is responsible for validating the
tool’s connection request, and ensuring proper authorizations for tool
requests.*

Labels
------

\[EXTENSION\]

Action
------

\[APPROVED\]

Copyright Notice
----------------

Copyright (c) 2016 Intel, Inc. All rights reserved. Copyright (c) 2016
IBM Corporation. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

The primary purpose of PMIx is to provide a mechanism by which
applications can interact with their host resource manager (RM).
However, there are times when non-application processes (e.g.,
command-line tools) may also wish to communicate with the host RM.
Historically, such tools were custom-written for each specific RM due to
the customized and/or proprietary nature of the RM interfaces.

The advent of PMIx offers the possibility for creating portable tools
capable of querying multiple RMs without modification. Possible
use-cases include:

-   querying the status of scheduling queues, estimated allocation time
    for various resource options

-   job submission and allocation requests

-   querying of job status for executing applications

The key to supporting such uses lies in providing a mechanism by which a
tool can connect to a local PMIx server. Application processes are able
to connect because their local RM daemon provides them with the
necessary contact information upon execution. A command-line tool,
however, isn’t spawned by the RM daemon, and therefore lacks the
information required for rendezvous with the PMIx server.

This RFC involves two extensions to the code base:

-   **Extended by
    [RFC0010](https://github.com/pmix/RFCs/blob/master/RFC0010.md)**
    addition of a rendezvous mechanism for tools to connect to a local
    PMIx server. The host RM can direct the local PMIx server to accept
    tool connections by providing the *PMIX\_SERVER\_TOOL\_SUPPORT* info
    key to the PMIx\_server\_init function call. This directs the PMIx
    server to establish a separate Unix domain socket for tool
    connections, using a well-known file name of pmix..tool. placed in
    the temporary directory location as specified by either the TEMPDIR,
    TEMP, and TMP environmental variables.

When a tool calls *PMIx\_tool\_init*, the PMIx library will search the
temporary directory for files matching the defined name template. If
only one file is found, then the tool uses that as the rendezvous point
and initiates the connection. If multiple files are found, either due to
the presence of multiple PMIx servers or stale files, then the PMIx
library will return an error as it cannot determine which server to use
without further input from the caller. Callers can stipulate the server
by providing the pid of the target server using the
*PMIX\_SERVER\_PIDINFO* key in the call to init.

Once the connection has been made, the tool has access to all the PMIx
client interfaces, subject to constraints imposed by the host RM.

-   **Amended by
    [RFC0010](https://github.com/pmix/RFCs/blob/master/RFC0010.md)**
    addition of a *PMIx\_Query\_info* API by which the caller can
    request system-level information from the host RM. Note that the
    host RM itself may not have all the information being requested –
    e.g., the fabric manager may need to be consulted regarding
    fabric-related requests. However, all requests for information are
    relayed to the host RM for handling.

The query API is not expected to be used for retrieving information that
was published via either the *PMIx\_Put* or *PMIx\_Publish* functions.
Instead, the new API targets information that relates to the overall
system vs any specific allocation or application. Examples include:

-   *PMIX\_QUERY\_NAMESPACES* – retrieve a comma-delimited list of
    nspaces for all currently executing jobs
-   *PMIX\_QUERY\_JOB\_STATUS* – retrieve the status of the specified
    currently executing job
-   \_PMIX\_QUERY\_QUEUE\_LIST – retrieve a comma-delimited list of
    scheduler queues
-   *PMIX\_QUERY\_QUEUE\_STATUS* – retrieve the status of the specified
    scheduler queue

Requests for specified information require the use of the
*pmix\_info\_array\_t* entry in the *pmix\_info\_t* object. For example,
a request to retrieve the status of a specified list of executing jobs
might look like the following:

    pmix_info_t info, *array; size_t n;

    PMIX_INFO_CONSTRUCT(&info);
    (void)strncpy(info.key, PMIX_QUERY_JOB_STATUS, PMIX_MAX_KEYLEN);
    info.value.type = PMIX_INFO_ARRAY; // now create the array we will use to pass the jobs we want to know about
    array = &info.value.data.array;
    PMIX_INFO_CREATE(array->array, 3);
    array->size = 3;
    for (n=0; n < 3; n++) {
        (void)strncpy(array->array[n].key, , PMIX_MAX_KEYLEN);
    }
    PMIx_Query_info(&info, 1);

The PMIx server will pass this request to the host RM, which will parse
the input and provide the status of each given job in the corresponding
*pmix\_value\_t* field in that job’s array element.

NOTE: The host resource manager is responsible for validating the tool’s
connection request, and ensuring proper authorizations for tool
requests. The PMIx server library will provide the host RM with the
effective UID and GID of the tool process as reported by standard system
queries of the socket (e.g., using getpeereid).

Protoype Implementation
-----------------------

The PMIx library implementation is covered in the [Tool Connection to
PMIx Server](https://github.com/pmix/master/pull/68) pull request. The
prototype has been tested against Open MPI as referenced in the [Add
support for PMIx tool connections and
queries](https://github.com/open-mpi/ompi/pull/1801) pull request.

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

Austen Lauria  
IBM Corporation  
Github: austenlauria

