---
layout: page
title: What Are RMs Required to Provide?
---

Launching a new job can be accomplished much more scalably if the host
resource manager provides each application process with a set of
information required for initial wireup support. This includes:

#### Application-level Information

-   JobID: unique namespace assigned to identify processes belonging to
    this job
-   Offset: starting global rank of this job. Rarely used, but may be of
    greater interest in the future.
-   Universe size: number of slots allocated to this session
-   Job size: number of processes in this specific application
-   Local size: number of processes in this application on this node
-   Node size: Total number of application processes (spanning all
    namespaces) on this node
-   Max procs: largest number of allowed processes for this application
-   ClusterID: string identifier/name of the cluster the job is running
    on – used when connecting jobs on different clusters

#### Mapping Information

-   List of nodes hosting processes in this job. Typically expressed as
    a regular expression. For convenience, PMIx provides the
    PMIx\_generate\_regex function that will generate a regular
    expression for this purpose when given an array of node names.
    Clients can subsequently obtain information from the client library
    (which will parse the regular expression) using the
    PMIx\_Resolve\_nodes function.
-   Map of process ranks to nodes. Typically expressed as a regular
    expression. For convenience, PMIx provides the PMIx\_generate\_ppn
    function that will generate the regular expression when given an
    array of process ranks. Clients can subsequently obtain information
    from the client library (which will parse the regular expression)
    using the PMIx\_Resolve\_peers function

#### Node-level Information

-   Node ID: integer identifier of this node
-   Hostname: the name the resource manager is using for this host.
    Usually is just the output of the hostname command.
-   Local peers: comma-delimited list of ranks from this application
    that share the local node
-   Local cpusets: comma-delimited list of cpuset bindings for the local
    peers
-   Local leader: rank of the lowest-ranked peer on this node
-   Architecture – integer representation of the datatype architecture
-   Node topology – the HWLOC topology of the local node
-   Top-level temporary directory assigned to this allocated session on
    this node
-   Temporary directory assigned to this namespace under the top-level
    session temporary directory

#### Peer-level Information

The following list of information should be provided for each peer in
the application:

-   Rank: an integer rank of the process within the application
-   Appnum: the number of the application to which this process belongs,
    starting with zero. Specifically addresses multi-application jobs.
-   Application leader: the lowest global rank of a peer in this
    specific application. Will always be zero except for
    multi-application jobs
-   Global rank: integer rank of the process within the overall job.
    Will always equal the process’ rank except in multi-application jobs
-   Application rank: integer rank of the process within its own
    application
-   Local rank: integer rank of the process amongst its peers on the
    node where it is executing
-   Node rank: integer rank of the process across all processes on the
    node where it is executing
-   Node ID: the integer identifier of the node where this process is
    executing
-   URI: contact information for the process
-   Cpuset: the cpuset this process to which this process is bound
-   Spawned – a boolean flag indicating if this process was launched via
    a dynamic spawn request
-   Temporary directory assigned to this process under the namespace
    temporary directory

