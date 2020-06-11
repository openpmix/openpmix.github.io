---
layout: default
title: Security Credential Transactions
---

RFC0024
=======

Title
-----

Security Credential Transactions

Abstract
--------

Provide a mechanism by which applications can request a security
credential from the system, and pass a credential back to the system for
validation.

Labels
------

\[EXTENSION\]\[CLIENT-API\]\[RM-INTERFACE\]

Action
------

\[APPROVED\]

Copyright Notice
----------------

Copyright (c) 2017 Intel, Inc. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

Applications and tools often interact with each other in ways that
require verification of the identity of the user making the request, and
access to that user’s relevant authorizations. This is particularly
important when tools connect directly to a system-level PMIx server that
may be operating at a privileged level. A variety of system management
software packages provide this service, but the lack of standardized
interfaces makes portability problematic.

This RFC defines two new PMIx client-side APIs and two corresponding
server interfaces to the host system management stack (SMS) for this
purpose. These are most likely to be used by user-space
applications/tools, but are not restricted to that realm.

#### Obtaining a credential

The API for obtaining a credential is defined as a non-blocking
operation since the host SMS may have to contact a remote credential
service. The definition takes into account the potential that the
returned credential could be sent via some mechanism to another
application that resides in an environment using a different security
mechanism. Thus, provision is made for the system to return additional
information (e.g., the identity of the issuing agent) outside of the
credential itself and visible to the application.

    /* Define a callback function to return a requested security credential.
     * Returned values include:
     *
     * status - PMIX_SUCCESS if a credential could be assigned as requested, or
     *          else an appropriate error code indicating the problem
     *
     * credential - pointer to an allocated pmix_byte_object_t containing the
     *              credential (as a opaque blob) and its size. Ownership of
     *              the credential is transferred to the receiving function - thus,
     *              responsibility for releasing the memory lies outside the
     *              PMIx library.
     *
     * info - an array of pmix_info_t structures provided by the system to pass
     *        any additional information about the credential - e.g., the identity
     *        of the issuing agent. The info array is owned by the PMIx library
     *        and is not to be released or altered by the receiving party. Note that
     *        this array is not related to the pmix_info_t structures possibly
     *        provided in the call to PMIx_Get_credential.
     *
     *        Information provided by the issuing agent can subsequently be used
     *        by the application for a variety of purposes. Examples include:
     *            - checking identified authorizations to determine what
     *              requests/operations are feasible as a means to steering
     *              workflows
     *            - compare the credential type to that of the local SMS for
     *              compatibility
     *
     * ninfo - number of elements in the info array
     *        
     * cbdata - the caller's provided void* object
     *
     * NOTE: the credential is opaque and therefore understandable only by
     *       a service compatible with the issuer.
     */
    typedef void (*pmix_credential_cbfunc_t)(pmix_status_t status,
                                             pmix_byte_object_t *credential,
                                             pmix_info_t info[], size_t ninfo,
                                             void *cbdata);

    /* Request a credential from the PMIx server/SMS.
     * Input values include:
     *
     * info - an array of pmix_info_t structures containing any directives the
     *        caller may wish to pass. Typical usage might include:
     *            PMIX_TIMEOUT - how long to wait (in seconds) for a credential
     *                           before timing out and returning an error
     *            PMIX_CRED_TYPE - a prioritized, comma-delimited list of desired
     *                             credential types for use in environments where
     *                             multiple authentication mechanisms may be
     *                             available
     *
     * ninfo - number of elements in the info array
     *
     * cbfunc - the pmix_credential_cbfunc_t function to be called upon completion
     *          of the request
     *
     * cbdata - pointer to an object to be returned when cbfunc is called
     *
     * Returned values:
     * PMIX_SUCCESS - indicates that the request has been successfully communicated to
     *                the local PMIx server. The response will be coming in the provided
     *                callback function.
     *
     * Any other value indicates an appropriate error condition. The callback function
     * will _not_ be called in such cases.
     */
    pmix_status_t PMIx_Get_credential(const pmix_info_t info[], size_t ninfo,
                                      pmix_credential_cbfunc_t cbfunc, void *cbdata);

Upon receiving a request for credential from a client, or calling the
PMIx\_Get\_Credential API on its own behalf, the PMIx server
implementation shall pass the request to its host SMS using a new
interface. If the interface is not defined, then the server shall
immediately communicate a PMIX\_ERR\_NOT\_SUPPORTED response to the
originating caller through their provided callback function.

    /* Request a credential from the host SMS
     * Input values include:
     *
     * proc - pointer to a pmix_proc_t identifier of the process on whose behalf
     *        the request is being made (i.e., the client originating the request)
     *
     * directives - an array of pmix_info_t structures containing directives pertaining
     *              to the request. This will typically include any pmix_info_t structs
     *              passed by the requesting client, but may also include directives
     *              required by (or available from) the PMIx server implementation - e.g.,
     *              the effective user and group ID's of the requesting process.
     *
     * ndirs - number of pmix_info_t structures in the directives array
     *
     * cbfunc - the pmix_credential_cbfunc_t function to be called upon completion
     *          of the request
     *
     * cbdata - pointer to an object to be returned when cbfunc is called
     *
     * Returned values:
     * PMIX_SUCCESS - indicates that the request is being processed by the host system
     *                management stack. The response will be coming in the provided
     *                callback function.
     *
     * Any other value indicates an appropriate error condition. The callback function
     * will _not_ be called in such cases.
     */
    typedef pmix_status_t (*pmix_server_get_cred_fn_t)(const pmix_proc_t *proc,
                                                       const pmix_info_t directives[], size_t ndirs,
                                                       pmix_credential_cbfunc_t cbfunc, void *cbdata);

#### Validating a credential

The API for validating a credential is again defined as a non-blocking
operation since the host SMS may have to contact a remote credential
service. Provision is made for the system to return additional
information regarding possible authorization limitations beyond simple
authentication.

    /* Define a validation callback function to indicate if a provided
     * credential is valid, and any corresponding information regarding
     * authorizations and other security matters
     * Returned values include:
     *
     * status - PMIX_SUCCESS if the provided credential is valid. An appropriate
     *          error code indicating the issue if the credential is rejected.
     *
     * info - an array of pmix_info_t structures provided by the system to pass
     *        any additional information about the authentication - e.g., the
     *        effective userid and group id of the certificate holder, and any
     *        related authorizations. The info array is owned by the PMIx library
     *        and is not to be released or altered by the receiving party. Note that
     *        this array is not related to the pmix_info_t structures possibly
     *        provided in the call to PMIx_Validate_credential.
     *
     *        The precise contents of the array will depend on the host SMS and
     *        its associated security system. At the minimum, it is expected (but
     *        not required) that the array will contain entries for the PMIX_USERID
     *        and PMIX_GROUPID of the client described in the credential.
     *
     * ninfo - number of elements in the info array
     *
     * cbdata - the caller's provided void* object
     */
    typedef void (*pmix_validation_cbfunc_t)(pmix_status_t status,
                                             pmix_info_t info[], size_t ninfo,
                                             void *cbdata);


    /* Request validation of a credential by the PMIx server/SMS
     * Input values include:
     *
     * cred - pointer to a pmix_byte_object_t containing the credential
     *
     * info - an array of pmix_info_t structures containing any directives the
     *        caller may wish to pass. Typical usage might include:
     *            PMIX_TIMEOUT - how long to wait (in seconds) for validation
     *                           before timing out and returning an error
     *            PMIX_USERID - the expected effective userid of the credential
     *                          to be validated
     *            PMIX_GROUPID - the expected effective group id of the credential
     *                          to be validated
     *
     * ninfo - number of elements in the info array
     *
     * cbfunc - the pmix_validation_cbfunc_t function to be called upon completion
     *          of the request
     *
     * cbdata - pointer to an object to be returned when cbfunc is called
     *
     * Returned values:
     * PMIX_SUCCESS - indicates that the request has been successfully communicated to
     *                the local PMIx server. The response will be coming in the provided
     *                callback function.
     *
     * Any other value indicates an appropriate error condition. The callback function
     * will _not_ be called in such cases.
    pmix_status_t PMIx_Validate_credential(const pmix_byte_object_t *cred,
                                           const pmix_info_t info[], size_t ninfo,
                                           pmix_validation_cbfunc_t cbfunc, void *cbdata);

Upon receiving a request for validation from a client, or calling the
PMIx\_Validate\_credential API on its own behalf, the PMIx server
implementation shall pass the request to its host SMS using a new
interface. If the interface is not defined, then the server shall
immediately communicate a PMIX\_ERR\_NOT\_SUPPORTED response to the
originating caller through their provided callback function.

    /* Request validation of a credential from the host SMS
     * Input values include:
     *
     * proc - pointer to a pmix_proc_t identifier of the process on whose behalf
     *        the request is being made (i.e., the client issuing the request)
     *
     * cred - pointer to a pmix_byte_object_t containing the provided credential
     *
     * directives - an array of pmix_info_t structures containing directives pertaining
     *              to the request. This will typically include any pmix_info_t structs
     *              passed by the requesting client, but may also include directives
     *              used by the PMIx server implementation
     *
     * ndirs - number of pmix_info_t structures in the directives array
     *
     * cbfunc - the pmix_validation_cbfunc_t function to be called upon completion
     *          of the request
     *
     * cbdata - pointer to an object to be returned when cbfunc is called
     *
     * Returned values:
     * PMIX_SUCCESS - indicates that the request is being processed by the host system
     *                management stack. The response will be coming in the provided
     *                callback function.
     *
     * Any other value indicates an appropriate error condition. The callback function
     * will _not_ be called in such cases.
     */
    typedef pmix_status_t (*pmix_server_validate_cred_fn_t)(const pmix_proc_t *proc,
                                                            pmix_byte_object_t *cred,
                                                            const pmix_info_t directives[], size_t ndirs,
                                                            pmix_validation_cbfunc_t cbfunc, void *cbdata);

#### Associated attributes

One new attribute is included in this RFC:

-   PMIX\_CRED\_TYPE: when passed in PMIx\_Get\_credential, a
    prioritized, comma-delimited list of desired credential types for
    use in environments where multiple authentication mechanisms may be
    available. When returned in a callback function, a string identifier
    of the credential type

Several existing attributes can be utilized by the APIs in this RFC,
with the meaning of the value somewhat dependent on the context of its
use:

-   PMIX\_USERID: the effective userid of the client in the credential,
    or of the client making the request

-   PMIX\_GROUPID: the effective group ID of the client in the
    credential, or of the client making the request

-   PMIX\_TIMEOUT: how long (in seconds) to wait for a response before
    timing out the operation

Protoype Implementation
-----------------------

Prototype implementation is available in the PMIx master repo in [Pull
Request 584](https://github.com/pmix/master/pull/584)

Note that the prototype implementation makes a "best effort" attempt to
obtain and/or validate a security credential by first trying to obtain
it from a system management service. If the service is not available,
then the implementation will attempt to fulfill the request using the
internal security components used by PMIx to validate client/tool
connections to the server. As of this writing, that includes (depending
on configuration logic) munge, a native uid/gid-based protocol, and a
"none" component that is only active upon explicit request and is
targeted for debug purposes.

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

