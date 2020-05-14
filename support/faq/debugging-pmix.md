---
layout: default
title: Debugging PMIx
---

The granularity of debugging output from PMIx depends greatly on the
version being used. In all cases, maximum output is available when PMIx
is configured with –enable-debug, though installations built that way
should not be used in general production or performance testing as it
does impact the performance of the library.

**Debugging PMIx v1.x**
The early releases of PMIx have only one debugging option, though there
are different levels available for it. Debugging output is controlled
via the PMIX\_DEBUG environmental parameter using a range of 0-100. A
value of 2 will provide a degree of tracing through the code base
(though this wasn’t rigidly enforced), while higher values will trigger
more detailed output from inside the infrastructure itself.

**Debugging PMIx v2.x**
Beginning with the v2.0 release, PMIx switched to a plugin-based
architecture using the [Modular Component
Architecture](http://www.aosabook.org/en/openmpi.html) (MCA) plugin
manager developed by Jeff Squyres et al at Indiana University in the
early 2000s. MCA is specifically designed to provide generalized plugin
support in high-performance environments, with low overhead and minimal
latency impact. In PMIx, MCA is used to define general abstraction
interfaces (known as “frameworks”) that capture a certain range of
functionality – e.g., a framework for handling buffer-based pack/unpack
operations, or one that supports security protocols. Within each
framework, multiple components (or “plugins”) can be provided, each with
its own implementation of the framework’s abstraction interfaces.

Debugging output in an MCA environment is controlled at the individual
framework level using MCA parameters. For example, one can debug the
buffer operations (contained in the “bfrops” framework) by setting the
PMIX\_MCA\_bfrops\_base\_verbose parameter. Parameters can be set in a
system-level default file (located in the installation directory as
etc/pmix-mca-params.conf), a user-level default file
($HOME/.pmix/mca-params.conf), or on the command line of a supporting
tool (e.g., as “-pmca bfrops\_base\_verbose 5” on the PMIx Reference
Server’s “prun” command line).

Beginning with the upcoming v2.1 release, the “pinfo” tool can be used
to report the available parameters, their current value, and where they
were set. **IMPORTANT NOTE:** there is a “pinfo” executable in the
standard Linux distribution. Please ensure that you have the PMIx
install-prefix/bin location at the front of your $PATH environmental
variable, or specify the absolute path to the PMIx “pinfo” command.

Unfortunately, this tool is not available in the PMIx v2.0 release
series. In this case, one can only refer to the source code itself –
each framework is defined as its own subdirectory in the src/mca
directory. Of these, the ones of primary interest to users would be the
“ptl” (client-server communications), “psec” (security handshake for
establishing client-server connections), and “psensor” (local monitors
for detecting stalled applications).

Debugging non-plugin code remains under the control of PMIX\_DEBUG.

**Debugging PMIx Master (v3.x)**
The PMIx master (currently scheduled for release as v3.x) offers an
expanded granularity for debugging output by further splitting the
PMIX\_DEBUG option to introduce function-specific parameters for both
the client and server non-plugin code. Controls include:

-   pmix\_server\_get\_verbose: server-side PMIx\_Get operations
-   pmix\_server\_connect\_verbose: server-side PMIx\_Connect/Disconnect
    operations
-   pmix\_server\_fence\_verbose: server-side PMIx\_Fence operations
-   pmix\_server\_pub\_verbose: server-side
    PMIx\_Publish/Unpublish/Lookup operations
-   pmix\_server\_spawn\_verbose: server-side PMIx\_Spawn operations
-   pmix\_server\_event\_verbose: server-side event notification
    operations
-   pmix\_server\_base\_verbose: basic server infrastructure operations
-   pmix\_client\_get\_verbose: client-side PMIx\_Get operations
-   pmix\_client\_connect\_verbose: client-side PMIx\_Connect/Disconnect
    operations
-   pmix\_client\_fence\_verbose: client-side PMIx\_Fence operations
-   pmix\_client\_pub\_verbose: client-side
    PMIx\_Publish/Unpublish/Lookup operations
-   pmix\_client\_spawn\_verbose: client-side PMIx\_Spawn operations
-   pmix\_client\_event\_verbose: client-side event notification
    operations
-   pmix\_client\_base\_verbose: basic client infrastructure operations

There remain a very few places where PMIX\_DEBUG is used. We are
actively working to eliminate those, but some additional output may be
available via that parameter in the interim.

