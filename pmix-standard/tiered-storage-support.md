---
layout: page
title: Tiered Storage Support
---

UNDER CONSTRUCTION
==================

Please note that tiered storage support is a subject of current RFC
development. Thus, the description on this page should be considered a
“draft” at this time and is provided to help stimulate discussion.

Next-generation systems are designed to access information that resides
in an array of storage media, ranging from offline archives to streaming
data flows. This *tiered storage* architecture presents a challenge to
application developers and system managers striving to achieve high
system efficiency and performance. Multiple vendor-specific solutions
have been proposed, each with its own unique API and associated data
structures. However, this results in a corresponding loss in application
portability and increased cost of customer migration across
procurements. Likewise, it would be burdensome for scheduler/work load
manager (WLM) vendors to directly interface to storage managers from
numerous vendors. Accordingly, the PMIx Storage working group seeks to
define a flexible solution that allows vendor independence by defining
an abstraction layer based on PMIx APIs and data structures in
accordance with the PMIx standard architecture:

-   requests from tools and/or applications will flow to their
    associated PMIx server, which will “upcall” them to their respective
    host SMS daemon – i.e., we retain the principle that applications
    and tools *do not* directly interact with SMS elements
-   the host daemon may (if it chooses) directly implement support for
    the request by coding its own interface to the storage manager.
    Alternatively, the host daemon may call the corresponding PMIx API
    which will utilize an appropriate PMIx plugin to integrate with the
    active storage manager in that environment
-   it is the responsibility of the host SMS and/or storage manager to
    determine and enforce user authorizations for the requested
    operation

The current effort focuses on two distinct stages: application startup
time and run-time control for workflow steering. Underpinning the effort
are several key premises:

-   Cluster storage systems will increasingly utilize a tiered
    architecture composed of some combination of persistent storage and
    distributed cache
-   Persistent storage will generally be constrained to parallel file
    systems, typically composed of rotating storage organized into a
    disk array and attached to the cluster through one or more IO
    servers
-   Caches will be instantiated at a number of locations, including IO
    servers (currently denoted as “burst buffers”), network switches,
    compute cabinets, and compute nodes. Caches will typically be
    composed of non-volatile random-access memory (NVRAM), or some
    comparable moderate-speed media
-   Storage bits flow in all directions – from persistent storage to
    caches to compute nodes, between caches, from compute nodes to
    cache, and from compute nodes to persistent storage (possibly
    transiting one or more caches)
-   Data movement will occur in response to multiple stimuli, including
    faults, scheduler directives (e.g., pre-positioning data and/or
    binaries), and dynamic workflow directives from applications
    themselves

### Application Startup

Application startup is significantly impacted by the time required to
instantiate the executable and its dependent libraries on all of the
active compute nodes. Understanding the time needed by the storage
system to obtain access to the necessary bits on storage media and
relocate them to the compute nodes is therefore essential to efficient
use of the system’s resources.

![Discovery Fig](/images/discovery.png 'Discovery Fig')

The startup process can be separated into two phases. The first phase,
shown at right, centers around identification of the bits required for
execution of the application. Obviously, user specification of binaries
and dependencies (both data and libraries) at time of job submittal
offers the most accurate approach to this problem. However, users often
cannot (or will not) provide a complete list of dependencies, especially
when using third-party dynamically linked libraries.

In order to support these situations, PMIx provides an API by which the
Work Load Manager (WLM) can obtain a list of libraries and files
required by the submitted job using some combination of:

-   PMIx standardized script-level directives from the user, with the
    PMIx library parsing the job script to harvest the directives;
-   WLM defined script-level directives, which the WLM will parse and
    provide to PMIx as a list of identified dependencies; and
-   automatic detection of links to dynamic libraries by binaries (e.g.,
    via the standard Posix *ldd* tool and/or integration to a library
    such as [XALT](https://github.com/Fahey-McLay/xalt))

Once the dependencies have been identified, the WLM can query the
storage manager to obtain an estimate of the time required to acquire
executables, libraries, and data files specified by the scheduler, and
position them to locations specified by the scheduler, using the results
in its scheduling algorithm. This allows, for example, the time to
retrieve data from cold storage (e.g., an offline tape archive) to be
factored into the schedule.

![Prestage Fig](/images/prestage.png 'Prestage Fig')

The second phase of the startup process, shown at right, begins when the
time window for job execution approaches – i.e., when the WLM
anticipates the allocation will be given. At this point, the WLM alerts
the storage manager to the upcoming allocation, passing the storage
manager a list of files to be retrieved and locations where those files
are to be cached. The precise timing of the caching operation is a
function of the system management stack (SMS) environment. For example,
some systems may initiate pre-staging while an existing job is executing
its epilog, allowing the operation to continue in parallel with running
the prolog for the new allocation. Others may choose to execute only
during the prolog phase, or to make pre-staging contingent upon
allocation of cache storage resources. The role of PMIx in this phase
remains the same: to provide an API by which the WLM can direct the
storage manager to move bits to their target destinations. A
corresponding PMIx event has been defined by which the storage manager
can alert the WLM when the bits have been cached into position.

Note that the WLM is *not required* to support these features – they are
offered solely as an optional method for optimizing launch performance.

### Run-Time Control

Run-time control over storage options – including the ability for
applications to influence location, relocation, and storage strategies
(e.g., striping across multiple locations, hot/warm/cold storage) of
checkpoints and other data – is likewise of importance, particularly for
dynamically-steered workflows. In this case, storage directives can be
issued by both the application itself, and by tools executed by the user
on (for example) a login node while the application is executing.
Likewise, a mechanism is needed by which the SMS can alert the
application to impending changes in resource availability, data
movement, and other changes that might impact execution.

![Runtime Control Fig](/images/runtimecontrol.png 'Runtime Control Fig')

PMIx supports run-time storage control by providing:

-   the PMIx\_Alloc API to request allocation of storage resources. This
    includes attributes to specify the lifetime of the requested
    allocation (hard time limit, life of the current job or job step,
    etc.), minimum and desired allocation size, storage strategy for the
    allocation (e.g., whether the resources are to be considered
    hot/warm/cold, migration policies for stored data between levels),
    and prioritized set of desired locations and/or location attributes
    (e.g., persistence, replication strategy). Note that
    tools/applications that call the API to request resources will have
    those requests communicated to the WLM via the local PMIx server. At
    that point, the WLM decides on scheduling control – it could (for
    example) use the PMIx\_Query\_nb function to query the storage
    manager regarding availability and then schedule the resources
    itself, or it could use the PMIx\_Alloc function to request that the
    storage manager schedule the resources
-   attributes to be used with the PMIx\_Query\_nb API to obtain
    information on available storage, including directory mount points,
    capacity (both raw and available), and speed (both read and write)
-   APIs and attributes for passing storage strategy directives to the
    SMS from tool and applications
-   attributes allowing applications to query (via the existing
    PMIx\_Query\_nb API) supported storage directives, and the default
    (or currently set) location and storage strategy in place
-   APIs and attributes by which tools/applications can direct the
    asynchronous movement of data across storage tiers
-   PMIx events indicating when application-directed asynchronous
    storage operations have started/completed

A couple of key issues remain under discussion:

-   requests for data movement across tiers/locations may complete after
    requesting process has terminated, thus necessitating definition of
    a mechanism to update completion state in a given location and/or
    notification
-   when looking at scheduling, we may want/need to migrate data closer
    to where computation will occur. It isn’t entirely clear who (WLM,
    storage manager?) should make that decision, and it may be that an
    API/mechanism by which storage and scheduler can negotiate the
    question needs to be defined

Similar to the launch support, WLMs are *not required* to support
run-time storage control – however, they *are required* to at least
return a “not supported” error in response to requests for unsupported
services. Providing a NULL function pointer in the server callback
function structure is considered equivalent to providing the “not
supported” response.

