---
layout: default
title: Logging with PMIx
---

![Logging Fig](/images/logging.png 'Logging Fig')

The PMIx\_Log interface is provided to support posting information by
applications and system management subsystem (SMS) elements to
persistent storage. This function is *not* intended for output of
computational results, streaming of raw RAS data, or performant data
operations, but rather on reporting status and saving state information
such as inserting computation progress reports into the application’s
SMS job log. A variety of logging options are available to support
use-cases such as remote monitoring of application progress (e.g., via
email), output of error reports to syslog for post-mortem analysis, and
caching of application completion information for use by subsequent
applications in a workflow. Depending on the choice of output channel,
logged information may be retrieved via the PMIx\_Query interface.

The illustration at the top of the page serves to highlight some of the
capabilities provided by the logging support. Note that the illustration
is not intended to be comprehensive in its coverage as the number of
possible use-cases is too large to capture in a single drawing.
Supported uses include:

-   Writing of messages to syslog, both local (using the
    PMIX\_LOG\_LOCAL\_SYSLOG attribute) or on the syslog of some central
    server designated for this purpose. The PMIx client will send the
    logging request to its local server. If the PMIX\_LOG\_LOCAL\_SYSLOG
    attribute is included in the request, then the PMIx server will
    immediately output the message to the local syslog. If not, or if
    the PMIX\_LOG\_GLOBAL\_SYSLOG attribute is specified, then the PMIx
    server will “upcall” the request to its host RM daemon. It is the
    responsibility of the host RM daemon to identify and transfer the
    provided data to the appropriate location – upon arrival, the RM can
    use the PMIx\_Log function to deliver the data to the local syslog
    on that node, or can write the data to syslog itself. Attributes for
    setting the desired syslog priority are provided – the default is
    set to LOG\_INFO indicating reporting of an informational message
-   Sending notifications via email (or other transports) to a
    designated user. Application users may wish to be notified of
    completion of their application, receive periodic progress reports,
    or be notified of a problem that merits attention. PMIx itself
    includes support for some of the more popular transports – requests
    for unsupported transports are referred to the host RM for
    processing, with an error returned if the requested transport is not
    available in the host environment
-   Outputting tagged log messages to stdout or stderr of the
    application, or a connected tool. Where supported, an alternative
    output stream (possibly directed to a dedicated log file) may be
    specified. Messages may be tagged (via the PMIX\_LOG\_TAG\_OUTPUT
    attribute) as flowing via the PMIx\_Log API to differentiate them
    from the application’s normal output. In addition, messages may be
    time stamped (PMIX\_LOG\_TIMESTAMP\_OUTPUT) or output in XML format
    (PMIX\_LOG\_XML\_OUTPUT)
-   Storing status updates in the job record using the
    PMIX\_LOG\_JOB\_RECORD attribute. Resource managers nearly always
    maintain a record of the jobs they schedule and execute. This
    includes information on the time spent waiting for allocation,
    priority of the request, identity of the requestor, name/path of the
    executable and/or job script, etc. Historically, users have had to
    record status information on their application (e.g., computational
    progress) in files which are subsequently stored in persistent
    storage. PMIx\_Log offers the option (where supported) of injecting
    such status reports directly into the job record, thus providing a
    single, time sequential record of the job’s execution.  
    Note that system libraries can also use this feature to record
    job-affecting events (e.g., network failures) that might have
    impacted the application during its execution, perhaps linking them
    to more detailed information stored in a RAS database.
-   Storing state information in a global key-value datastore. The prior
    use-cases all involve one-way output of data – i.e., the caller can
    *log* the data, but cannot later retrieve it. However, there are
    times when an application, tool, or SMS element may wish to store
    information in a global key-value datastore that can be searched by
    external agents, or be retrieved by the caller itself at some later
    time. For example, an SMS element may wish to store state
    information in a persistent place for retrieval upon recovery from a
    failure. Use of the PMIx\_Publish API might, at first glance, appear
    to meet this need. However, PMIx\_Publish is focused on
    inter/intra-application data exchange – it therefore does not
    guarantee persistence across (for example) an RM failure.  
    Passing the PMIX\_LOG\_GLOBAL\_DATASTORE attribute in a call to
    PMIx\_Log indicates that the provided data is to be stored in a
    persistent datastore. Additional attributes can be used to provide
    direction on the storage strategy – e.g., hot/warm/cold or locality.
    Note that it is advisable to use the *optional* flag for storage
    strategy directives as support for such behaviors is not yet
    commonplace.  
    Once logged, the data is retrievable using the PMIx\_Query API. Note
    that the time required to retrieve the requested data will vary
    depending on storage location – this is *not* intended as a
    performant operation. Attributes to direct the behavior of the query
    (e.g., indicating if the caller should wait for the data to become
    available) are provided.

Note that data can be “logged” without specifying the output channel. In
this case, the PMIx library will default to logging a copy of the data
to each available channel, which are subject to control by MCA parameter
in addition to the usual build/configuration constraints. The caller can
optionally control the logging behavior by providing multiple channel
attributes in order of desired priority, subject to the availability of
the specified channel. For example, an application could ask that data
be emailed to a given user, or logged to a global syslog, or logged to
local syslog by specifying first the PMIX\_LOG\_EMAIL attribute,
followed by the PMIX\_LOG\_GLOBAL\_SYSLOG and the
PMIX\_LOG\_LOCAL\_SYSLOG attributes, with the PMIX\_LOG\_ONCE attribute
being included to indicate that only one log channel should be used. If
PMIX\_LOG\_ONCE is not indicated, then the data will be logged to all
three channels. In this case, the PMIX\_ERR\_PARTIAL\_COMPLETION error
is returned if any channel fails to log as requested, but others
succeed; PMIX\_ERR\_OPERATION\_FAILED is returned if all fail; and
PMIX\_SUCCESS is returned if all succeed. This provides flexibility with
minimal code complexity when operating in multiple environments that
support differing output channels.

Logging attributes can also utilize the “required” flag in the
pmix\_info\_t structure to indicate that the data *must* be logged via
the specified channel. If given, failure to complete the operation on
that channel will result in return of the PMIX\_ERR\_OPERATION\_FAILED
error. Otherwise, use of a given channel is considered “optional” and
errors are reported according to the above rules.

Specifying a prioritized list of logging channels on each call to
PMIx\_Log can impact the performance of the API itself as it requires
the PMIx library to scan available channels to create an ordered list,
and this might in turn require multiple passes over the available
plugins. The PMIx reference library provides an MCA parameter to help
reduce this impact. A user can control the default order of channel
delivery by setting the “plog\_base\_order” MCA parameter to a
comma-delimited, prioritized list of channel names based on the
corresponding attribute by extracting the characters following
“PMIX\_LOG\_”, as follows:

-   PMIX\_LOG\_LOCAL\_SYSLOG – “local\_syslog”
-   PMIX\_LOG\_GLOBAL\_SYSLOG – “global\_syslog”
-   PMIX\_LOG\_EMAIL – “email”

and so on. Marking a given channel in the list as “required” can be done
by adding “:req” to the channel name, as shown in the following example:

    plog_base_order = "local_syslog:req,global_syslog,email"

Parsing of this MCA parameter is case-insensitive, and the parser will
accept any “required” flag that starts with “req” – e.g., “reqd” and
“required”. Similarly, the PMIX\_LOG\_ONCE attribute can be set by
default using the “plog\_base\_log\_once” MCA parameter. Note that this
is specific to the PMIx reference library and is **not** part of the
standard – users are advised to check their local implementation for
similar support.

Channels that are not recognized by the PMIx library will automatically
be directed to the host RM for processing. This allows for
RM-proprietary channel support without committing those channel names to
the PMIx Standard.

Advice to users: the available channel support on a system can be
queried via the PMIx\_Query API should the application developer wish to
tailor their code accordingly – this will always report the channels
directly supported by the PMIx library. However, channels supported by
the host RM will be included only if the RM itself supports such
queries.

Advice to users: The PMIx\_Log API should **never** be used for
streaming data as it is not a “performant” transport and can perturb the
application since it involves the local PMIx server and host RM daemon.

