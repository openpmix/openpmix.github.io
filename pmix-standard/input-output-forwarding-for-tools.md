---
layout: page
title: Input/Output Forwarding For Tools
---

UNDER CONSTRUCTION
==================

Please note that the forwarding of IO within PMIx is a subject of
current RFC development. Thus, the description on this page should be
considered a “draft” at this time and is provided to help stimulate
discussion.

The term “tool” widely refers to non-computational programs executed by
the user or system administrator on a command line. Tools almost always
interact with either the system management stack (SMS), user
applications, or both to perform administrative and support functions.
For example, a debugger tool might be used to remotely control the
processes of a parallel application, monitoring their behavior on a
step-by-step basis.

Underlying the operation of many tools is a common need to forward stdin
from the tool to targeted processes, and to return stdout/stderr from
those processes for display on the user’s console. Historically, each
tool developer was responsible for creating their own IO forwarding
subsystem. However, with the introduction of PMIx as a standard
mechanism for interacting between applications and the SMS, it has
become possible to relieve tool developers of this burden.

This design guide is intended to:

-   provide tool developers with an overview of the expected behavior of
    the PMIx IO forwarding support;
-   guide resource manager (RM) vendors regarding roles and
    responsibilities expected of the RM to support IO forwarding; and
-   provide insight into the thinking of the PMIx community behind the
    definition of the PMIx IO forwarding APIs

Note that the forwarding of IO via PMIx requires that both the host SMS
and the tool support PMIx, but does *not* impose any similar
requirements on the application itself.

Forwarding Stdout/Stderr
------------------------

![Output Fig](/images/output.png 'Output Fig')

At an appropriate point in its operation (usually during startup), the
tool utilizes the PMIx\_tool\_init function to connect to a PMIx server.
The server can be hosted by an SMS daemon, or could be embedded in a
library-provided starter program such as *mpiexec*. In terms of IO
forwarding, the operations remain the same either way – for purposes of
this discussion, we will assume the server is in an SMS daemon, and that
the application processes were directly launched by the SMS (see diagram
at right).

Once the tool has connected to the target server, it can request that
output from a specified set of processes in a given executing
application be forwarded to it. In addition, requests to forward output
from processes being spawned by the tool can be included in calls to the
PMIx\_Spawn API. Two modes are envisioned:

-   PMIX\_IOF\_COPY – deliver a copy of the output to the tool, letting
    the stream continue to also be delivered to the default location.
    This allows the tool to “tap” into the output stream without
    redirecting it from its current final destination
-   PMIX\_IOF\_REDIRECT – intercept the output stream and deliver to the
    requesting tool instead of its current final destination. This might
    be used, for example, during a debugging procedure to avoid
    “polluting” the application’s results file. The original output
    stream destination is restored upon termination of the tool

Application processes are the children of the local SMS (typically, the
local RM daemon) and not directly related to the PMIx server itself.
Thus, it is the responsibility of the local SMS to collect the child’s
output – usually done by capturing the relevant file descriptors at
fork/exec of the child process – and the PMIx server on the remote nodes
is not involved in this process. Once captured, the host SMS is
responsible for returning the output to the SMS daemon serving the tool.
This typically will be the daemon co-located with the tool, but this
isn’t required.

Once the output reaches the serving SMS daemon, the daemon passes the
output to its embedded PMIx server via the PMIx\_IOF\_push function
whose parameter list includes the identifier of the source process and
the IOF channel of the provided data. The PMIx server will transfer the
data to the tool’s client library, which will in turn output it to the
screen.

When registering to receive output, the tool can specify several
formatting options to be used on the resulting output stream. These
include:

-   PMIX\_IOF\_TAG – output is prefixed with the nspace,rank of the
    source and a string identifying the channel (stdout, stderr, etc.)
-   PMIX\_IOF\_TIMESTAMP – output is marked with the time at which the
    data was received by the tool (note that this will differ from the
    time at which it was actually output by the source)
-   PMIX\_IOF\_XML\_OUTPUT – output is to be formatted in XML

The PMIx client in the tool will format the output stream. Note that
output from multiple processes will often be interleaved due to
variations in arrival time.

Forwarding Stdin
----------------

![Input Fig](/images/input.png 'Input Fig')

The tool is not necessarily a child of the RM as it may have been
started directly from the command line. Thus, provision must be made for
the tool to collect its stdin and pass it to the host RM (via the PMIx
server) for forwarding. Two methods of support for forwarding of stdin
are defined:

-   internal collection by the PMIx tool library itself. This is
    requested via the PMIX\_IOF\_PUSH\_STDIN attribute in the
    PMIx\_IOF\_push call. When this mode is selected, the tool library
    begins collecting all stdin data and internally passing it to the
    local server for distribution to the specified target processes. All
    collected data is sent to the same targets until stdin is closed, or
    a subsequent call to PMIx\_IOF\_push is made that includes the
    PMIX\_IOF\_COMPLETE attribute indicating that forwarding of stdin is
    to be terminated.
-   external collection directly by the PMIx tool code. It is assumed
    that the tool will provide its own code/mechanism for collecting its
    stdin as the tool developers may choose to insert some filtering
    and/or editing of the stream prior to forwarding it. In addition,
    the tool can directly control the targets for the data on a per-call
    basis – i.e., each call to PMIx\_IOF\_push can specify its own set
    of target recipients for that particular “blob” of data. Thus, this
    method provides maximum flexibility, but requires that the tool
    developer provide their own code to capture stdin.

Note that it is the responsibility of the resource manager to forward
data to the host where the target proc(s) are executing, and for the
host daemon on that node to deliver the data to the stdin of target
proc(s) via the typical pipe. Specifically, the PMIx server on the
remote node is not involved in this process. Systems that do not support
forwarding of stdin will return PMIX\_ERR\_NOT\_SUPPORTED in response to
a forwarding request.

**Advice to implementors:** it is recognized that scalable forwarding of
stdin represents a significant challenge. A high quality implementation
will at least handle a “send-to-1” model whereby stdin is forwarded to a
single identified process, and an additional “send-to-all” model where
stdin is forwarded to all processes in the application. Other models
(e.g., forwarding stdin to an arbitrary subset of processes) are left to
the discretion of the implementor.

**Advice to users:** stdin buffering by the RM and/or PMIx library can
be problematic. If the targeted recipient is slow reading data (or
decides never to read data), then the data must be buffered in some
intermediate daemon or the local PMIx server itself. Thus, piping a
large amount of data into stdin can result in a very large memory
footprint in the system management stack. This is further exacerbated
when targeting multiple recipients as the buffering problem, and hence
the resulting memory footprint, is compounded. Best practices,
therefore, typically focus on reading of input files by application
processes as opposed to forwarding of stdin.

