---
layout: page
title: IO Forwarding for Tools and Debuggers
---

RFC0025
=======

Extends:  
\* [RFC0010: Extension of Tool Interaction
Support](https://github.com/pmix/RFCs/blob/master/RFC0010.md) \*
[RFC0001: Provide a mechanism by which tools can interact with a local
PMIx server that has opted to accept such
connections](https://github.com/pmix/RFCs/blob/master/RFC0001.md)

Title
-----

IO Forwarding for Tools and Debuggers

Abstract
--------

This RFC extends support for all tools by adding the ability for the RM
to forward output from applications to a tool, and to forward stdin from
the tool to one or more application processes.

Labels
------

-   \[EXTENSION\]\[CLIENT-API\]\[SERVER-API\]\[RM-INTERFACE\]

Action
------

\[SUBMITTED\]

Copyright Notice
----------------

Copyright (c) 2017-2018 Intel, Inc. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

This RFC extends support for tools and debuggers by adding the ability
for the RM to forward output from applications to a tool, and to forward
stdin from the tool to one or more application processes. Enabling this
requires the addition of several new attributes and APIs covering the
cases where an application is being spawned using the PMIx\_Spawn API
versus where the tool is connecting to an already-running application.

First, we define a new data type used to identify IO channels referenced
by a given directive:

    /* define a set of bit-mask flags for specifying IO
     * forwarding channels. These can be OR'd together
     * to reference multiple channels */
    typedef uint16_t pmix_iof_channel_t;
    #define PMIX_FWD_NO_CHANNELS        0x0000
    #define PMIX_FWD_STDIN_CHANNEL      0x0001
    #define PMIX_FWD_STDOUT_CHANNEL     0x0002
    #define PMIX_FWD_STDERR_CHANNEL     0x0004
    #define PMIX_FWD_STDDIAG_CHANNEL    0x0008
    #define PMIX_FWD_ALL_CHANNELS       0x00ff

Significant room is left for future extensions. As stated in the
enclosed comment, these channels can be combined to reference multiple
channels with a single directive – e.g., to forward stdout and stderr,
the caller would pass a pmix\_iof\_t value of
`PMIX_FWD_STDOUT_CHANNEL | PMIX_FWD_STDERR_CHANNEL`.

There is a natural race condition that occurs in the case where a tool
is spawning an application via the PMIx\_Spawn API. The registration API
requires specification of the source processes, but the caller won’t
know the nspace of the spawned processes until PMIx\_Spawn returns –
which occurs after the processes have been spawned. When the caller
includes a forwarding directive in the PMIx\_Spawn call, therefore, the
server shall default to locally caching all forwarded IO pending
registration of an associated callback function by the client. Note that
a "chatty" application could lead to a cache overload – thus, servers
are not required to guarantee complete caching of forwarded IO.

Specific attributes defined for IOF support include:

    /* IO Forwarding Attributes */
    #define PMIX_IOF_CACHE_SIZE        "pmix.iof.csize"       // (uint32_t) requested size of the server cache in bytes for each specified channel.
                                                              //            By default, the server is allowed (but not required) to drop
                                                              //            all bytes received beyond the max size
    #define PMIX_IOF_DROP_OLDEST       "pmix.iof.old"         // (bool) in an overflow situation, drop the oldest bytes to make room in the cache
    #define PMIX_IOF_DROP_NEWEST       "pmix.iof.new"         // (bool) in an overflow situation, drop any new bytes received until room becomes
                                                              //        available in the cache (default)
    #define PMIX_IOF_BUFFERING_SIZE    "pmix.iof.bsize"       // (uint32_t) basically controls grouping of IO on the specified channel(s) to
                                                              //            avoid being called every time a bit of IO arrives. The library
                                                              //            will execute the callback whenever the specified number of bytes
                                                              //            becomes available. Any remaining buffered data will be "flushed"
                                                              //            upon call to deregister the respective channel
    #define PMIX_IOF_BUFFERING_TIME    "pmix.iof.btime"       // (uint32_t) max time in seconds to buffer IO before delivering it. Used in conjunction
                                                              //            with buffering size, this prevents IO from being held indefinitely
                                                              //            while waiting for another payload to arrive
    #define PMIX_IOF_COMPLETE          "pmix.iof.cmp"         // (bool) indicates whether or not the specified IO channel has been closed
                                                              //        by the source
    #define PMIX_IOF_PUSH_STDIN        "pmix.iof.stdin"       // (pmix_proc_t*) Used by a tool to request that the PMIx library collect
                                                              //                the tool's stdin and forward it to the indicated proc - the
                                                              //                PMIX_RANK_WILDCARD value indicates that all procs in the
                                                              //                provided nspace are to receive the data

Note that these attributes can be provided during PMIx\_server\_init to
serve as default values for any subsequent registration calls, as part
of the job-level directives included in a PMIx\_Spawn call, or passed
during registration to override any default values.

#### Forwarding of Output

This RFC adds the following client-facing APIs for output forwarding
support:

    /* Define a callback function for delivering forwarded IO to a process
     * This function will be called whenever data becomes available, or a
     * specified buffering size and/or time has been met. The function
     * will be passed the following values:
     *
     * iofhdlr - the returned registration number of the handler being invoked.
     *           This is required when deregistering the handler.
     *
     * channel - a bitmask identifying the channel the data arrived on
     *
     * source - the nspace/rank of the process that generated the data
     *
     * payload - pointer to an array containing the data. Note that
     *           multiple strings and/or binary data may be included,
     *           and that the array may _not_ be NULL terminated
     *
     * size - the number of bytes in the payload array
     *
     * info - an optional array of info provided by the source containing
     *        metadata about the payload. This could include PMIX_IOF_COMPLETE
     *
     * ninfo - number of elements in the optional info array
     */
     typedef void (*pmix_iof_cbfunc_t)(size_t iofhdlr,
                                       pmix_iof_channel_t channel,
                                       pmix_proc_t *source,
                                       char *payload, size_t size,
                                       pmix_info_t info[], size_t ninfo);


    /* Register to receive output forwarded from a remote process.
     *
     * procs - array of identifiers for sources whose IO is being
     *         requested. Wildcard rank indicates that all procs
     *         in the specified nspace are included in the request
     *
     * nprocs - number of identifiers in the procs array
     *
     * directives - optional array of attributes to control the
     *              behavior of the request. For example, this
     *              might include directives on buffering IO
     *              before delivery, and/or directives to include
     *              or exclude any backlogged data
     *
     * ndirs - number of elements in the directives array
     *
     * channel - bitmask of IO channels included in the request.
     *           NOTE: STDIN is not supported as it will always
     *           be delivered to the stdin file descriptor
     *
     * cbfunc - function to be called when relevant IO is received
     *
     * regcbfunc - since registration is async, this is the
     *             function to be called when registration is
     *             completed. The function itself will return
     *             a non-success error if the registration cannot
     *             be submitted - in this case, the regcbfunc
     *             will _not_ be called.
     *
     * cbdata - pointer to object to be returned in regcbfunc
     */
    PMIX_EXPORT pmix_status_t PMIx_IOF_pull(const pmix_proc_t procs[], size_t nprocs,
                                                const pmix_info_t directives[], size_t ndirs,
                                                pmix_iof_channel_t channel, pmix_iof_cbfunc_t cbfunc,
                                                pmix_hdlr_reg_cbfunc_t regcbfunc, void *regcbdata);

    /* Deregister from output forwarded from a remote process.
     *
     * iofhdlr - the registration number returned from the
     *           call to PMIx_IOF_pull
     *
     * directives - optional array of attributes to control the
     *              behavior of the request. For example, this
     *              might include directives regarding what to
     *              do with any data currently in the IO buffer
     *              for this process
     *
     * cbfunc - function to be called when deregistration has
     *          been completed. Note that any IO to be flushed
     *          may continue to be received after deregistration
     *          has completed.
     *
     * cbdata - pointer to object to be returned in cbfunc
     */
    PMIX_EXPORT pmix_status_t PMIx_IOF_deregister(size_t iofhdlr,
                                                  const pmix_info_t directives[], size_t ndirs,
                                                  pmix_op_cbfunc_t cbfunc, void *cbdata);

Requests for IO forwarding are relayed to the PMIx server for
processing. The PMIx server is required to first check to see if the new
IO request matches or overlaps with any prior requests from other local
clients – only new requests (either for a new source or for additional
channels from the subject of a prior request) shall be relayed to the
host RM using the following new server-module callback function:

    /* Request the specified IO channels be forwarded from the given array of procs.
     * The function shall return PMIX_SUCCESS once the host RM accepts the request for
     * processing, or a PMIx error code if the request itself isn't correct or supported.
     * The callback function shall be called when the request has been processed,
     * returning either PMIX_SUCCESS to indicate that IO shall be forwarded as requested,
     * or some appropriate error code if the request has been denied.
     *
     * NOTE: STDIN is not supported in this call! The forwarding of stdin is a "push"
     * process - procs cannot request that it be "pulled" from some other source
     *
     * procs - array of process identifiers whose IO is being requested.
     *
     * nprocs - size of the procs array
     *
     * directives - array of key-value attributes further defining the request. This
     *              might include directives on buffering and security credentials for
     *              access to protected channels
     *
     * ndirs - size of the directives array
     *
     * channels - bitmask identifying the channels to be forwarded
     *
     * cbfunc - callback function when the IO forwarding has been setup
     *
     * cbdata - object to be returned in cbfunc
     *
     * This call serves as a registration with the host RM for the given IO channels from
     * the specified procs - the host RM is expected to ensure that this local PMIx server
     * is on the distribution list for the channel/proc combination
     */
    typedef pmix_status_t (*pmix_server_iof_fn_t)(const pmix_proc_t procs[], size_t nprocs,
                                                  const pmix_info_t directives[], size_t ndirs,
                                                  pmix_iof_channel_t channels,
                                                  pmix_op_cbfunc_t cbfunc, void *cbdata);

Upon receiving indication of success from the host RM, the server then
adds the requestor to the distribution list for the indicated IO and
returns success to the requesting client. Requests for overlapping
services immediately return success. Any error return from the host RM
is relayed to the requestor and the requestor is not added to the
distribution list. It is assumed that the host RM, or the relevant
starter, is responsible for collecting any data from an application’s
stdout, stderr, and other channels as the application processes are
direct children of that system.

Once forwarded IO reaches the destination node, the host RM passes the
data to the PMIx server for transmission to one or more clients (as per
registration) via the following API:

    /* Provide a function by which the host RM can pass forwarded IO
     * to the local PMIx server for distribution to its clients. The
     * PMIx server is responsible for determining which of its clients
     * have actually registered for the provided data
     *
     * Parameters include:
     *
     * source - the process that provided the data being forwarded
     *
     * channel - the IOF channel (stdin, stdout, etc.)
     *
     * bo - a byte object containing the data
     *
     * info - an optional array of metadata describing the data, including
     *        attributes such as PMIX_IOF_COMPLETE to indicate that the
     *        source channel has been closed
     *
     * ninfo - number of elements in the info array
     *
     * cbfunc - a callback function to be executed once the provided data
     *          is no longer required. The host RM is required to retain
     *          the byte object until the callback is executed, or a
     *          non-success status is returned by the function
     *
     * cbdata - object pointer to be returned in the callback function
     */
    PMIX_EXPORT pmix_status_t PMIx_server_IOF_deliver(const pmix_proc_t *source,
                                                      pmix_iof_channel_t channel,
                                                      const pmix_byte_object_t *bo,
                                                      const pmix_info_t info[], size_t ninfo,
                                                      pmix_op_cbfunc_t cbfunc, void *cbdata);

Upon receipt of data, the PMIx client library shall execute the callback
function for all matching registrations.

#### Forwarding Input

The tool is not necessarily a child of the RM as it may have been
started directly from the command line. Thus, provision must be made for
the tool to collect its stdin and pass it to the host RM (via the PMIx
server) for forwarding. Two methods of support for forwarding of stdin
are defined in this RFC:

1.  internal collection by the PMIx tool library itself. This is
    requested via the PMIX\_IOF\_PUSH\_STDIN attribute in the
    PMIx\_IOF\_push call. When this mode is selected, the tool library
    begins collecting all stdin data and internally passing it to the
    local server for distribution to the specified target processes. All
    collected data is sent to the same targets until stdin is closed, or
    a subsequent call to PMIx\_IOF\_push is made that includes the
    PMIX\_IOF\_COMPLETE attribute indicating that forwarding of stdin is
    to be terminated.

2.  external collection directly by the PMIx tool code. It is assumed
    that the tool will provide its own code/mechanism for collecting its
    stdin as the tool developers may choose to insert some filtering
    and/or editing of the stream prior to forwarding it. In addition,
    the tool can directly control the targets for the data on a per-call
    basis – i.e., each call to PMIx\_IOF\_push can specify its own set
    of target recipients for that particular "blob" of data. Thus, this
    method provides maximum flexibility, but requires that the tool
    developer provide their own code to capture stdin.

The following API is provided for the tool to use when requesting the
forwarding of stdin to a set of target processes:

    /* Push data collected locally (typically from stdin) to
     * target recipients.
     *
     * targets - array of process identifiers to which the data is to be delivered. Note
     *           that a WILDCARD rank indicates that all procs in the given nspace are
     *           to receive a copy of the data
     *
     * ntargets - number of procs in the targets array
     *
     * directives - optional array of attributes to control the
     *              behavior of the request. For example, this
     *              might include directives on buffering IO
     *              before delivery, and/or directives to include
     *              or exclude any backlogged data
     *
     * ndirs - number of elements in the directives array
     *
     * bo - pointer to a byte object containing the stdin data
     *
     * cbfunc - callback function when the data has been forwarded
     *
     * cbdata - object to be returned in cbfunc
     */
    PMIX_EXPORT pmix_status_t PMIx_IOF_push(const pmix_proc_t targets[], size_t ntargets,
                                            pmix_byte_object_t *bo,
                                            const pmix_info_t directives[], size_t ndirs,
                                            pmix_op_cbfunc_t cbfunc, void *cbdata);

Similarly, the PMIx server requires a server-module callback function by
which it can relay the stdin to the host RM for distribution:

    /* Passes stdin to the host RM for transmission to specified recipients. The host RM is
     * responsible for forwarding the data to all PMIx servers that host the specified
     * target.
     *
     * source - pointer to the identifier of the process whose stdin is being provided
     *
     * targets - array of process identifiers to which the data is to be delivered. Note
     *           that a WILDCARD rank indicates that all procs in the given nspace are
     *           to receive a copy of the data
     *
     * ntargets - number of procs in the targets array
     *
     * directives - array of key-value attributes further defining the request. This
     *              might include directives on buffering and security credentials for
     *              access to protected channels
     *
     * ndirs - size of the directives array
     *
     * bo - pointer to a byte object containing the stdin data
     *
     * cbfunc - callback function when the data has been forwarded
     *
     * cbdata - object to be returned in cbfunc
     *
     */

    typedef pmix_status_t (*pmix_server_stdin_fn_t)(const pmix_proc_t *source,
                                                    const pmix_proc_t targets[], size_t ntargets,
                                                    const pmix_info_t directives[], size_t ndirs,
                                                    const pmix_byte_object_t *bo,
                                                    pmix_op_cbfunc_t cbfunc, void *cbdata);

Systems that do not support forwarding of stdin may simply provide a
NULL for this function, or return PMIX\_ERR\_NOT\_SUPPORTED. In either
case, the PMIx server will return that error to the caller.

Advice to implementors: it is recognized that scalable forwarding of
stdin represents a significant challenge. A high quality implementation
will at least handle a "send-to-1" model whereby stdin is forwarded to a
single identified process, and an additional "send-to-all" model where
stdin is forwarded to all processes in the application. Other models
(e.g., forwarding stdin to an arbitrary subset of processes) are left to
the discretion of the implementor.

Advice to users: stdin buffering by the RM and/or PMIx library can be
problematic. If the targeted recipient is slow reading data (or decides
never to read data), then the data must be buffered in some intermediate
daemon or the local PMIx server itself. Thus, piping a large amount of
data into stdin can result in a very large memory footprint in the
system management stack. This is further exacerbated when targeting
multiple recipients as the buffering problem, and hence the resulting
memory footprint, is compounded. Best practices, therefore, typically
focus on reading of input files by application processes as opposed to
forwarding of stdin.

Protoype Implementation
-----------------------

The PMIx library implementation is covered in the [Implement the PMIx
IOF support](https://github.com/pmix/pmix/pull/334) pull request. The
prototype was integrated into the PMIx Reference Server
[here](https://github.com/pmix/pmix-reference-server/pull/32)

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

