---
layout: page
title: Acquisition of Subsystem Launch Information
---

RFC0029
=======

Title
-----

Acquisition of Subsystem Launch Information

Abstract
--------

The PMIx launch procedure includes a stage whereby various subsystems
(e.g., fabric) can provide a "blob" to the starter program that is to be
delivered to the PMIx server on each compute node. The blob can comprise
a wide range of information, including propagation of environmental
variables and fabric endpoint assignments.

Labels
------

\[EXTENSION\]\[SERVER-API\]

Action
------

\[ACCEPTED\]

Copyright Notice
----------------

Copyright 2018 Intel, Inc. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

Applications frequently utilize environmental params (or "envars") to
"tune" behavior of their various subsystems. In addition, subsystems
themselves can identify global information (e.g., rendezvous addresses)
prior to launch, thereby avoiding costly data exchange after launch.
This RFC provides a mechanism by which such information can be collected
and provided to the starter prior to application launch, and then
delivered to application processes for use upon execution.

The expected execution path is as follows:

-   the starter (and/or its subsystems) may call PMIx to register envar
    patterns it would like to be locally collected for distribution with
    the specified nspace. Obviously, the starter could do the collection
    itself – however, the PMIx support is provided for those starters
    that include (potentially proprietary) plugins whereby the starter
    main code may not have full knowledge of all envars to be collected.

-   the starter calls PMIx to obtain the complete launch information
    "blob" to be included in the launch message sent to the compute
    nodes, providing the PMIx server with a . PMIx will package all
    contributions into a single "blob" for this purpose.

-   the starter transmits the launch command to the compute nodes. The
    compute node daemons extract the PMIx launch information "blob" and
    pass it to their local PMIx server for processing

-   the PMIx server extracts the individual subsystem contributions from
    the provided "blob" and passes them to its respective plugin for
    local processing prior to spawning local client processes. In the
    case of envars, the PMIx server will include the provided values in
    the list of envars returned by the *PMIx\_server\_setup\_fork*
    function.

Three new APIs are proposed for this purpose. The first provides a
mechanism by which a starter program can identify envars to be forwarded
in support of the application that are to be harvested by its locally
embedded PMIx server.

    /* Register environmental variables to be propagated with the launch.
     *
     * The PMIx server shall search the local environment for all envars matching the provided
     * pattern, and include any such envars in the launch information "blob" returned by a
     * subsequent call to PMIx_server_setup_application.
     *
     * @param *pattern Semicolon-delimited string patterns describing the envars to be harvested
     * and included in the launch message. Each pattern can contain a single
     * envar, or can consist of a mini-regex. Two regex characters are supported:
     *     - an asterisk '*' to indicate a wildcard for the remainder of the string
     *     - a question mark '?' to indicate a single-character wildcard in the given location
     * Note that the pattern only describes the parameter name and does not
     * apply to the value of the parameter
     *
     * @param directives[] An (optional) array of pmix_info_t structs containing
     * modifying directives for the request. This can include a directive specifying
     * a regex of envars to be excluded from forwarding.
     *
     * @param ndirs Number of structs in the directives array
     *
     * @retval PMIX_SUCCESS The request was successful
     *
     * @retval PMIX_ERROR(s) An appropriate error will be returned if the
     * request cannot be processed. This can include "not supported", "out
     * of memory", or "bad parameter" to indicate an unrecognized pattern string.
     */
    PMIX_EXPORT pmix_status_t PMIx_Forward_envars(const char nspace[],
                                                  const char *pattern,
                                                  pmix_info_t directives[], size_t ndirs);

Multiple calls to PMIx\_Forward\_envars will result in aggregation of
the harvested envars. Forwarded envars will be set in the environment of
each client process prior to start of execution.

Use of this API is relatively straightforward in the case of a starter
program provided by a given programming library (e.g., "mpiexec" from an
MPI implementation) as the starter has a priori knowledge of the envars
used by its internal subsystems. It can therefore inform PMIx of its
needs by calling the above API (or allowing its various subsystems to do
so on their own behalf). However, a generic starter program (e.g.,
"srun" or "aprun") from a given resource manager does not have this
advantage. The list of string patterns in such cases (or when the
application itself requires propagation of envars) can be provided by
the user using the *PMIX\_MCA\_forward\_envars* parameter via one of the
MCA mechanisms (file, environment, etc.).

The second API allows the starter to request a "blob" from the local
PMIx server that contains all information to be forwarded to the
application.

    /* define a callback function for the setup_application API. The
     * returned blob is "owned" by the PMIx server and will be released
     * upon call to cbfunc */
    typedef void (*pmix_setup_application_cbfunc_t)(pmix_status_t status,
                                                    pmix_byte_object_t *blob,
                                                    void *provided_cbdata,
                                                    pmix_op_cbfunc_t cbfunc, void *cbdata);


    /* Provide a function by which the resource manager can request
     * any application-specific information prior to
     * launch of an application. For example, network libraries may
     * opt to provide security credentials for the application. This
     * is defined as a non-blocking operation in case
     * libraries need to perform some action before responding. The
     * returned data blob will be distributed along with the application
     * and given to the local PMIx server on remote nodes for processing
     *
     * @param nspace The name of the nspace for whom launch information is being requested
     *
     * @param directives[] An (optional) array of pmix_info_t structs containing
     * modifying directives for the request. For example:
     *    - a starter launching a dynamically-requested spawned application might
     *      wish to provide a list of parent nspaces (using the PMIX_PARENT_ID
     *      attribute) whose information is to be aggregated into the returned blob.
     *      This supports, for example, "instant on" access to rendezvous points
     *      between dynamically-spawned applications.
     *    - the node (PMIX_NODE_MAP) and process (PMIX_PROC_MAP) map regex detailing
     *      where the application is being launched so that subsystems can provide
     *      proc/location-specific data (e.g., rendezvous points)
     *
     * @param ndirs Number of structs in the directives array
     *
     * @param cbfunc The callback function to be executed when the blob is complete
     *
     * @param cbdata Pointer to an object to be returned in cbfunc
     *
     * @retval PMIX_SUCCESS The request has been accepted
     *
     * @retval PMIX_ERROR(s) An appropriate error will be returned if the
     * request cannot be processed. This can include "not supported", "out
     * of memory", etc. Note that the callback function will _not_ be executed
     * if an error is returned.
     */
    PMIX_EXPORT pmix_status_t PMIx_server_setup_application(const char nspace[],
                                                            pmix_info_t directives[], size_t ndirs,
                                                            pmix_setup_application_cbfunc_t cbfunc, void *cbdata);

Finally, the third API is to be used by remote RM daemons to deliver the
"blob" returned by PMIx\_server\_setup\_application to the local PMIx
server for processing.

    /* Provide a function by which the local PMIx server can perform
     * any application-specific operations prior to spawning local
     * clients of a given application. For example, a network library
     * might need to setup the local driver for "instant on" addressing.
     *
     * @param nspace The name of the nspace for whom this launch information
     * is intended - this ensures that any envars only go to the relevant clients
     *
     * @param blob Pointer to a blob provided by the PMIx_server_setup_application
     * function.
     *
     * @param directives[] An (optional) array of pmix_info_t structs containing
     * modifying directives for the request.
     *
     * @param ndirs Number of structs in the directives array
     *
     * @param cbfunc The callback function to be executed when the blob is complete
     *
     * @param cbdata Pointer to an object to be returned in cbfunc
     *
     * @retval PMIX_SUCCESS The request has been accepted
     *
     * @retval PMIX_ERROR(s) An appropriate error will be returned if the
     * request cannot be processed. This can include "not supported", "out
     * of memory", etc. Note that the callback function will _not_ be executed
     * if an error is returned.
     */
    PMIX_EXPORT pmix_status_t PMIx_server_setup_local_support(const char nspace[],
                                                              pmix_byte_object_t *blob,
                                                              pmix_info_t directives[], size_t ndirs,
                                                              pmix_op_cbfunc_t cbfunc, void *cbdata);

Protoype Implementation
-----------------------

Two of the APIs in this RFC (PMIx\_server\_setup\_application and
PMIx\_server\_setup\_local\_support) have already appeared in a release
of the PMIx v2.0 reference library as they were committed prior to
establishiment of the RFC process.

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

