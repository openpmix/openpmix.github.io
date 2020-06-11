---
layout: default
title: Fabric Manager
---

UNDER CONSTRUCTION
==================

Please note that the role of the fabric manager within PMIx is a subject
of current RFC development. Thus, the description on this page should be
considered a “draft” at this time and is provided to help stimulate
discussion.

Fabric Manager: Roles and Expectations
--------------------------------------

![RFC0028 Fig](/images/rfc0028.png 'RFC0028 Fig')

The fabric manager (FM) has several areas of interaction with PMIx,
providing support for operations spanning the scheduler to the resource
manager (RM), debuggers, and applications. Some of these represent new
capabilities, while others are alternative (possibly more abstracted)
methods for current interactions. In the PMIx reference library, support
for each fabric type is provided via a fabric-specific plugin. Thus, the
fabric vendors are free to provide whatever level of support they deem
of value to their customers for the identified operations.

#### System Startup – Inventory

Schedulers generally require knowledge of the fabric topology as part of
their scheduling procedure to support optimized communication between
processes on different nodes. Current methods utilize files, read by the
scheduler when it starts, to communicate this information. However, the
format of the files tends to be both scheduler and fabric vendor
specific, thereby making it more difficult to maintain as cluster
configurations evolve (e.g., as a cluster reconfigures its network
topology, or vendors offer new fabrics).

PMIx defines two modes for supporting inventory collection:

-   Fabric manager query. If the FM supports a global report of
    resources, then the PMIx server hosted by the scheduler can obtain
    the report via the PMIx\_Query\_nb API. This is the preferred method
    for obtaining inventory information as it supports dynamic requests
    – e.g., triggered by notification of a network change – and directly
    provides information on inter-switch connectivity
-   Rollup of information from individual daemons at boot. This
    procedure involves direct discovery of NICs on individual nodes,
    with the resulting information passed in a scalable manner back to
    the scheduler. To aid in implementation, PMIx provides an API to
    request that the PMIx server execute the discovery and report back
    the information to the host RM daemon. This requires that PMIx be
    configured with the necessary third-party libraries (e.g., HWLOC) to
    enable discovery. Given that switches are not likely to have RM
    daemons on them, this method also requires an alternative method
    (e.g., file) for providing information on the switch/connectivity
    map.

Regardless of which mechanism is used, the final inventory needs to
include both a topology description of switch connectivity, and a
description of the NICs on each node. The latter must include at least
all fabric-related contact information (e.g., GID/LID) as well as the
network plane to which the NIC is attached. Additional information on
NIC capabilities (e.g., firmware version, memory size) is desirable, but
not required.

Inventory collection is expected to be a rare event – at system startup
and upon command from a system administrator. Inventory updates are
expected to involve a smaller operation involving only the changed
information. For example, replacement of a node would generate an event
to notify the scheduler with an inventory update without invoking the
global inventory operation.

#### Launch Support

Once an allocation has been made, the FM is involved in two steps of the
application launch procedure. Each of these will occur at least once per
application. Optimizations (e.g., caching of local NIC addressing info
on compute nodes) are left to the discretion of the PMIx plugin
implementor for each specific fabric.

##### Pre-Launch Configuration

Prior to starting the application, the RM may need to pass configuration
information for the job to the FM (e.g., defining/setting QoS levels).
The precise pre-launch settings will depend upon the abilities of the RM
as well as the supported options of the FM. In order to coordinate this
operation, the FM must support an ability for the RM to query (via the
PMIx\_Query\_nb API) its levels of support (e.g., available QoS levels).
This should include obtaining a list of configurable options, and any
predefined set points.

##### “Instant-On” Support

Allocation of resources typically occurs when the scheduler is notified
of job completion and just prior to initiation of the epilog portion of
the prior job. However, many schedulers also utilize anticipatory
scheduling to identify one or more jobs that will be run under different
termination scenarios, and the need to aggregate resources for larger
jobs often results in at least some portion of the allocation becoming
available on a rolling basis. Thus, there frequently is some amount of
time available for pre-conditioning of the allocation prior to start of
a newly scheduled job.

RMs can take advantage of this time to pass both the allocation and job
description to subsystems such as the fabric manager via the appropriate
PMIx API, receiving back a “blob” containing all information each
subsystem has determined will be required by its local resources within
the allocation to support the described job. Values returned by the FM
must be marked to identify which are to be given directly to the local
resource (e.g., network driver) on each node, and which are to be passed
to application processes as environmental variables that are recognized
by the resource when initialized by that specific process. For example,
some networks may “preload” the local network library with the location
of all processes in that application, thus allowing the library to
compute the required address information for any process, and/or include
a security token to protect inter-process communications.

Once the initialization blob has been obtained, the RM passes it to its
remote daemons on the allocated nodes as part of the launch message.
Prior to spawning any local processes, each RM daemon utilizes a PMIx
interface to deliver the configuration information to the local
resources. This allows the resources to prepare any internal state
tables for the job, an operation which may require elevated privileges
and therefore cannot be performed by the application processes
themselves. Upon completion of this “instant-on” initialization,
processes have all information required to communicate with their peers
– no further peer-to-peer exchange of information is required.

Accomplishing this procedure requires that the FM and associated network
driver provide support for:

-   host address resolution. Historically, each application process
    would independently discover the locally available NICs and
    determine their addressing information (e.g., TCP addresses or
    GID/LID pairs) and “broadcast” that information to its peers. While
    it is sometimes possible to resolve NIC addresses given a hostname,
    failure to provide addressing information up front can lead to
    non-scalable hostname resolution demands on the SMS resolving agent,
    thereby necessitating the all-to-all broadcast. Removing this
    exchange is accomplished by having the fabric manager provide any
    required addressing information for all nodes in the allocation so
    the information can be included in the initial allocation setup
    message.
-   pre-launch assignment of rendezvous endpoints (e.g., a socket or
    queue pair index) to each process for initiating peer-to-peer
    communications. This does not preclude the dynamic assignment of
    additional endpoints (e.g., multiple queue pairs for enhanced
    bandwidth), but instead provides a means by which the two peers can
    initially contact each other to further establish their
    communication channel. Note that there is no restriction preventing
    the two peers from simply using the provided endpoint for regular
    communications if they so choose.
-   unexpected messages (i.e. messages received prior to process
    registration with the receiving NIC). Since a process is given all
    required information to communicate with any peer upon startup, it
    is possible that a process could immediately attempt to send a
    message to a remote peer that has not yet been started. Network
    libraries currently can lose messages and/or return an error on
    communications addressed to a process that is not yet known to the
    receiving library. Thus, current parallel programming libraries
    typically include an out-of-band barrier operation just prior to
    enabling communications to ensure that all processes have been
    instantiated and have registered with their local NICs. This
    requirement can be eliminated if sufficient retry logic and buffer
    space is included in the network library and/or NIC hardware.
    Avoiding aggressive retries may be desirable – e.g., the receiving
    NIC could return a specific error code indicating that the intended
    recipient is not known to the NIC, thus instructing the sending NIC
    to introduce some slight (possibly randomized) delay prior to
    retrying – to mitigate unnecessary network congestion during
    startup. Current measurements, however, indicate that the time
    difference between startup of processes on even an exascale machine
    would be in the tenth-of-a-second range, and non-benchmark
    applications typically do not immediately send to their peers –
    therefore, the value of taking extraordinary measures remains to be
    seen.

When a connection is to be formed (most libraries do that lazily
nowadays), the library may be able to simply send the message (if the
network driver is preloaded with connection information), or can get the
remote port/plane assignment for the target proc by simply calling
PMIx\_Get to retrieve the info from the shared memory region and
transferring it to the network driver via an appropriate interface.

#### Event Notification

PMIx provides a mechanism by which various system management subsystems
can notify applications and other subsystems of events that might
require their attention. This can include failures (broadly defined as
anything that impacts the ability of that subsystem to perform as
expected) or warnings of impending issues (e.g., a temperature excursion
that could lead to shutdown of a resource). Events are generated on an
asynchronous basis – i.e., the various subsystems are not expected to
“poll” each other to obtain reports of events – and are transferred by
PMIx to the RM for distribution to applications that have requested
notification through the PMIx event registration interface. The FM is
expected to provide notification of fabric-related events, including
changes in routing (e.g., due to traffic or link failures) and node
replacement.

As the FM is the source of these events, the impact on the FM is
dictated solely by the frequency of events to report.

#### Application/Debugger Support

Applications, tools, and debuggers all would benefit from access to
FM-based information. These are expected to be relatively infrequent,
except perhaps during a dedicated debugging session when more frequent
requests on network loading might be appropriate. Two areas of support
have been identified (note that more will undoubtedly arise over time):

##### Traffic Reports

\* Debuggers currently have limited, if any, access to network
information. Given appropriate query support, a debugger could display
an application layout from a network (as opposed to compute node)
viewpoint, showing the user how the application is wired together across
the fabric. In addition, traffic reports in support of debugging
operations would aid in the identification of “hot spots” during
execution.

In general, debugger queries should be infrequent except for the traffic
reporting scenario. Reducing the burden on the FM in this latter
use-case might require adoption of a distributed notification
architecture – e.g., allowing the debugger to register for “traffic
report” events, and enabling individual switches to generate them.

##### Application Optimization

\* Application developers have indicated interest in an ability to query
the current network topology of their application, request QoS changes
or splitting their network resource allocation into multiple QoS
“channels”, etc. These will be infrequent.

