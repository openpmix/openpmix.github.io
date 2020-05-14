---
layout: default
title: Envar Directives for Applications and Launchers
---

RFC0022
=======

Title
-----

Environmental Parameter Directives for Applications and Launchers

Abstract
--------

It is sometimes desirable or required that standard environmental
variables (e.g., PATH, LD\_LIBRARY\_PATH, LD\_PRELOAD) be modified prior
to executing an application binary or a starter such as mpiexec – this
is particularly true when tools/debuggers are used to start the
application. This RFC defines new attributes to support these needs.

Labels
------

\[EXTENSION\]\[ATTRIBUTE\]

Action
------

\[ACCEPTED\]

Copyright Notice
----------------

Copyright 2017-2018 Intel, Inc. All rights reserved. Copyright 2018 Arm
Limited. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

It is sometimes desirable or required that standard environmental
variables (e.g., PATH, LD\_LIBRARY\_PATH, LD\_PRELOAD) be modified prior
to executing an application binary or a starter such as mpiexec – this
is particularly true when tools/debuggers are used to start the
application. This RFC defines new attributes to support these needs.

Passing directives to a launcher as well as the associated application
to be launched is constrained by the syntax of the PMIx\_Spawn command –
for clarity in the following discussion, it is shown below:

    /* Spawn a new job. The assigned namespace of the spawned applications
     * is returned in the nspace parameter - a _NULL_ value in that
     * location indicates that the caller doesn't wish to have the
     * namespace returned. The nspace array must be at least of size
     * PMIX_MAX_NSLEN+1. Behavior of individual resource managers
     * may differ, but it is expected that failure of any application
     * process to start will result in termination/cleanup of _all_
     * processes in the newly spawned job and return of an error
     * code to the caller.
     *
     * By default, the spawned processes will be PMIx "connected" to
     * the parent process upon successful launch (see PMIx_Connect
     * description for details). Note that this only means that the
     * parent process (a) will be given a copy of the  new job's
     * information so it can query job-level info without
     * incurring any communication penalties, and (b) will receive
     * notification of errors from process in the child job.
     *
     * Job-level directives can be specified in the job_info array. This
     * can include:
     *
     * (a) PMIX_NON_PMI - processes in the spawned job will
     *     not be calling PMIx_Init
     *
     * (b) PMIX_TIMEOUT - declare the spawn as having failed if the launched
     *     procs do not call PMIx_Init within the specified time
     *
     * (c) PMIX_NOTIFY_COMPLETION - notify the parent process when the
     *     child job terminates, either normally or with error
     */
    PMIX_EXPORT pmix_status_t PMIx_Spawn(const pmix_info_t job_info[], size_t ninfo,
                                         const pmix_app_t apps[], size_t napps,
                                         char nspace[]);

In this definition, the job\_info array includes directives passed to
the launcher to direct its behavior. The pmix\_app\_t array contains one
or more of the following structures:

    /****    PMIX APP STRUCT    ****/
    typedef struct pmix_app {
        char *cmd;
        char **argv;
        char **env;
        char *cwd;
        int maxprocs;
        pmix_info_t *info;
        size_t ninfo;
    } pmix_app_t;

The argv array contains the command line arguments of the application
itself, while the env array contains environmental variables to be set
prior to execution of application processes.

#### Modifying Environmental Variables

It is sometimes desirable or required that standard environmental
variables (e.g., PATH, LD\_LIBRARY\_PATH, LD\_PRELOAD) be modified prior
to executing an application binary or a starter such as mpiexec – this
is particularly true when tools/debuggers are used to start the
application. This RFC proposes the definition of a new PMIx structure
and associated attributes for specifying such operations:

    /* Provide a structure for specifying environment variable modifications
     * Standard environment variables (e.g., PATH, LD_LIBRARY_PATH, and LD_PRELOAD)
     * take multiple arguments separated by delimiters. Unfortunately, the delimiters
     * depend upon the variable itself - some use semi-colons, some colons, etc. Thus,
     * the operation requires not only the name of the variable to be modified and
     * the value to be inserted, but also the separator to be used when composing
     * the aggregate value
     */
    typedef struct {
        char *envar;
        char *value;
        char separator;
    } pmix_envar_t;

    /* environmental variable operation attributes */
    #define PMIX_SET_ENVAR          "pmix.envar.set"          // (pmix_envar_t*) set the envar to the given value,
                                                              //                 overwriting any pre-existing one
    #define PMIX_ADD_ENVAR          "pmix.envar.add"          // (pmix_envar_t*) add envar, but do not overwrite any existing one
    #define PMIX_UNSET_ENVAR        "pmix.envar.unset"        // (char*) unset the envar, if present
    #define PMIX_PREPEND_ENVAR      "pmix.envar.prepnd"       // (pmix_envar_t*) prepend the given value to the
                                                              //                 specified envar using the separator
                                                              //                 character, creating the envar if it doesn't already exist
    #define PMIX_APPEND_ENVAR       "pmix.envar.appnd"        // (pmix_envar_t*) append the given value to the specified
                                                              //                 envar using the separator character,
                                                              //                 creating the envar if it doesn't already exist

Using these definitions, the environment of the launcher itself can be
changed by including envar directives in the job\_info array – the
resulting code might look like this:

    pmix_envar_t foo = {
        "FOO_APPLES",
        "myvalue",
        ':'
    };
    pmix_info_t info;

    PMIX_INFO_CONSTRUCT(&info);
    PMIX_INFO_LOAD(&info, PMIX_PREPEND_ENVAR, &foo, PMIX_ENVAR);
    PMIx_Spawn(&info, 1, &app, 1, nspace);
    PMIX_INFO_DESTRUCT(&info);

This directs the RM to modify the FOO\_APPLES environmental variable in
the launcher’s environment, prepending "myvalue" to it separated by a
colon from any following values in the envar’s value, prior to executing
the launcher. Similar directives to modify the environmnent of the
application can be included in the *info* array of each application
description.

#### Impact on Resource Managers and Launchers

Resource managers and launchers must scan for relevant directives,
modifying environmental parameters as directed. Directives are to be
processed in the order in which they were given, starting with job-level
directives (applied to each app) followed by app-level directives.

Protoype Implementation
-----------------------

Prototype implementation is available in the master branch of the PMIx
Reference Server repo in [Pull Request
33](https://github.com/pmix/pmix-reference-server/pull/33) and in the
PMIx master branch in [Pull Request
672](https://github.com/pmix/pmix/pull/672)

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

Dirk Schubert  
Arm, Inc.  
Github: dirk-schubert-arm

