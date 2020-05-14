---
layout: default
title: Support for Network Interactions
---

RFC0012
=======

Title
-----

Add APIs and internal support for RM-network library interactions

Abstract
--------

Add a network support framework and appropriate APIs so that the RM can:

    * precondition an application (e.g., adding a security token to the
      app's environment) prior to launch

    * setup the local network driver to support an application (e.g., for
      "instant on" address resolution) prior to spawning the local processes

    * pass directives in the environment of client processes prior to forking

    * cleanup after each child process terminates

    * cleanup after all local children for a given application have
      terminated

Labels
------

\[EXTENSION\]\[SERVER-API\]

Action
------

\[APPROVED\]

Copyright Notice
----------------

Copyright 2016 Intel, Inc. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

Part of the "Instant On" initiative relies on establishing a partnership
between the resource manager (RM) and the networking library that allows
the combination to fully setup the messaging environment prior to spawn
of an application’s processes. Completing this procedure enables
applications to communicate without discovery and exchange of network
endpoint information.

There are two new APIs required to enable this support:

1.  Preconditioning the application for network operations. This
    typically involves obtaining a security token that must be used by
    each application process when communicating to another process in
    the same job. Some network libraries generate this token
    algorithmically, while others may need to obtain a token from a
    central server. Precondition values are typically passed to
    application processes as environmental variables that are recognized
    by the network library when initialized by the process. Thus, the
    *PMIx\_server\_setup\_application* API takes the application’s
    nspace (plus whatever pmix\_info\_t directives the RM chooses to
    provide), and returns an array of *pmix\_info\_t* structures. The
    return is done via a callback function so the API will not block
    should the library need to obtain the token from a remote server.

The structures may consist of any combination of key-value pairs, and
the RM shall:

-   if the key consists of *PMIX\_SET\_ENVAR*, then the provided string
    shall be included in the environment of each spawned application
    process in this nspace. Each environmental variable shall be
    provided in a separate *pmix\_info\_t* structure.

-   if the key consists of *PMIX\_UNSET\_ENVAR*, then the environment of
    the application shall be searched, and the provided envar removed if
    present. Each environmental variable shall be provided in a separate
    *pmix\_info\_t* structure.

-   all other key-values shall be included in the job-level info proved
    at process start.

Note: this API is not network-specific. Thus, as other precondition data
is identified in the future, internal support can be extended to ensure
all precondition data is included without changing this API.

The expected flow of operation is that the workload manager will call
*PMIx\_server\_setup\_application* from its head node (or system
management node) once for each job to be launched. The returned
information will then be included in the launch message containing the
job description sent to each compute node. The compute node PMIx server
will subsequently include the information in its call to
*PMIx*Server\_register\_nspace\_ so that the local client processes will
receive it.

1.  Preparing the local network driver to support an application’s
    processes that are being spawned on that node. The "Instant On"
    initiative requires that a process know how to communicate to each
    other at startup. One method of accomplishing this is to "preload"
    the local network library with the location of all processes in that
    application, thus allowing the library to compute the required
    address information for any process. The
    *PMIx\_server\_setup\_local\_support* API is called by the RM prior
    to fork/exec of any local process from the given application. This
    is defined as a non-blocking call to allow for operations that might
    not immediately complete. The RM is not allowed to fork/exec any
    local process from the specified application until the provided
    callback function has been executed.

Note: some components executed by the
*PMIx\_server\_setup\_local\_support* call may require elevated (e.g.,
*root*) privileges.

Note: this API is not network-specific. Thus, as other setup operations
are identified in the future, internal support can be extended to ensure
all setup is accomplished without changing this API.

Several other operations are also required by this RFC, but are not done
as part of exposed APIs – i.e., they are simple additions to internal
procedures. These include:

-   Passing network-specific environmental variables to the process at
    startup. A call into the *PNET* framework has been added to the
    *PMIx\_server\_setup\_fork* function for this purpose.

-   Cleanup of network library information at child process termination.
    A call into the *PNET* framework has been added to the PMIx server
    library upon detection of termination.

-   Cleanup of network library information upon termination of all local
    child processes from a given application. A call into the *PNET*
    framework has been added to the PMIx server library for this
    purpose.

Protoype Implementation
-----------------------

The PMIx library implementation is covered in the [Add network support
APIs](https://github.com/pmix/master/pull/222) pull request.

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

