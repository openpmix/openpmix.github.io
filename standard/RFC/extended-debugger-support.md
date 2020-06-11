---
layout: default
title: Extended Debugger Support
---

RFC0023
=======

Amends and extends:  
\* [RFC0010: Extension of Tool Interaction
Support](https://github.com/pmix/RFCs/blob/master/RFC0010.md) \*
[RFC0001: Provide a mechanism by which tools can interact with a local
PMIx server that has opted to accept such
connections](https://github.com/pmix/RFCs/blob/master/RFC0001.md)

Title
-----

Support for Launching Applications Under Debugger Tools

Abstract
--------

Prior RFCs have provided support for several typical use-cases involving
tools interacting with applications and the general system management
stack. One key use-case, however, has not been covered: the case where
an application is actually launched under control of a tool. This RFC
defines support for that mode of operation.

Labels
------

\[EXTENSION\]\[CLIENT-API\]\[SERVER-API\]\[RM-INTERFACE\]\[ATTRIBUTES\]

Action
------

\[IN PROGRESS\]

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

Prior RFCs defined mechanisms and standards for connecting
debuggers/tools to running jobs, and allowing a tool to itself launch a
job, possibly in conjunction with its own daemons. Thus, they dealt with
the following use-cases:

###### Use-case I: attach to an executing application

In this case, the application is started by some other tool – e.g.,
either an "mpiexec" provided by the programming library, or a native
launcher (such as "srun", "aprun", or "qsub") provided by the RM. The
debugger is initiated at some random later time, typically when the
application is detected as having encountered some problem. An example
might look like:

    $ mpiexec -n 3 ./myapp &
    $ dbgr <pid-of-mpirun>

In this mode of operation, the debugger needs to discover the rendezvous
information of the respective launcher and then connect to that PMIx
server in the launcher. PMIx already provides an automatic rendezvous
protocol for this purpose. Once attached, all PMIx APIs are available
for debugger use to obtain information (e.g., the process table of the
application), request launch of debugger daemons, etc. – subject to the
support provided by the launcher.

###### Use-case 2: direct-launch an application using a debugger tool

In this case, the dbgr itself can use the PMIx spawn options to control
the app’s startup, including directing the RM/app as to when to block
and wait for debugger attachment, or stipulating that an interceptor
library be preloaded. However, this means that the user is restricted to
whatever cmd line options the debugger vendor has provided for
operations such as process placement and binding, which places a
significant burden on the debugger vendor. An example might look like
the following:

    $ dbgr -n 3 ./myapp

where the dbgr code would look something like the example provided
[here](../../support/how-to/example-direct-launch-debugger-tool/index.html).
As shown in that example, tool developers are encouraged to query the
host RM for its level of support prior to initiating the spawn request.
Note that the example takes advantage of the [PMIx IO
forwarding](../input-output-forwarding-for-tools/index.html) support to
display output from both the application and debugger daemons, and to
forward user-typed commands to the debugger daemons for execution.

Assuming it is supported, co-launch of debugger daemons in this use-case
is supported by adding a pmix\_app\_t to the PMIx\_Spawn command,
indicating that the resulting processes are debugger daemons by setting
the PMIX\_DEBUGGER\_DAEMONS attribute. This tells the RM that the
processes are not to be counted against allocated limits, and should not
be included in job-level counters (e.g., PMIX\_UNIV\_SIZE) given to the
application (in MPI parlance, the processes spawned by this pmix\_app\_t
are **not** to be included in MPI\_COMM\_WORLD). If co-launch is not
supported, then the tool can launch the debugger daemons using a
separate call to PMIx\_Spawn – however, the PMIX\_DEBUGGER\_DAEMONS
attribute still must be provided.

#### Indirect-launch using a debugger tool

A third use-case that is frequently encountered (but not dealt with by
prior RFCs) involves executing a program under a debugger using an
intermediate launcher such as mpiexec. In other words, the user executes
the application/debugging session using something like the following
command line:

    $ dbgr mpiexec -n 3 ./myapp

This is an important case for users needing to debug their application
from the start of execution, but need/want to use an intermediate
launcher. It is a little tricky, however, as it requires some degree of
coordination between the dbgr tool and the launcher. Ultimately, it is
the launcher that is going to launch the application, and the debugger
must somehow inform it (and the application) that this is being done in
a debug session so that the application knows to “block” until the
debugger attaches to it. There are also potential modifications to the
launch directive required by the debugger (e.g., to preload an
interceptor library, or to use a debugger-provided local fork/exec
agent).

Prior approaches relied on the debugger to modify the launcher’s cmd
line, exploiting that launcher’s cmd line options to create the desired
behavior. This has been problematic for debugger vendors as every
launcher is different, thus requiring the debugger tool to be customized
for each implementation. This RFC is focused on eliminating that burden
by defining a PMIx-based standard mechanism for the coordination.

Given that the launcher appears on the debugger tool’s cmd line, we
assume for the purpose of this use-case that the debugger tool is
responsible for launching the launcher itself. This can be done by
simply executing the launcher via a command line (e.g., using the Posix
“system” function), or the tool may fork/exec it, or may request that it
be started by the RM using the PMIx\_Spawn API.

Regardless of how it is started, the debugger must set
PMIX\_LAUNCHER\_PAUSE\_FOR\_TOOL=1 in the environment of mpiexec or in
the pmix\_info\_t array in the spawn command using the PMIX\_SET\_ENVAR
directive. This instructs mpiexec to pause after initialization so it
can receive further instructions from the debugger. This might include a
request to co-spawn debugger daemons along with the application, or
further directives relating to the startup of the application (e.g., to
LD\_PRELOAD a library, or replace the launcher’s local spawn agent with
one provided by the debugger).

As mpiexec starts up, it calls PMIx\_server\_init to setup its PMIx
server. The server initialization includes writing a server-level
rendezvous file that allows other processes (such as the originating
debugger) to connect to the server. The launcher must then pause,
awaiting further instructions from the debugger.

Armed with the pid (returned by fork/exec or the “system” command) or
the namespace (returned by PMIx\_Spawn) of the executing mpiexec, the
debugger tool utilizes the PMIx\_tool\_connect\_server API to complete
the connection to the mpiexec server. Note that:

-   PMIx does not allow servers to initiate connections – thus, the
    debugger tool must initiate the connection to the launcher’s PMIx
    server.
-   tools can only be connected to one server at a time. Therefore, if
    connected to the system-level server to use PMIx\_Spawn to launch
    mpiexec, the debugger tool will be disconnected from that server and
    connected to the PMIx server in mpiexec

At this point, the debugger can execute any PMIx operation, including:

query mpiexec capabilities; pass directives to configure application
behavior – e.g., specifying the desired pause point where application
processes shall wait for debugger release; request launch of debugger
daemons, providing the appropriate pmix\_app\_t description specify a
replacement fork/exec agent; and define/modify standard environmental
variables for the application Once ready to launch, mpiexec parses its
command line to obtain a description of the desired job. An allocation
of resources may or may not have been made in advance (either by the
user, or by the tool prior to starting mpiexec)- if not, then mpiexec
may itself utilize the PMIx\_Alloc API to obtain one from the
system-level PMIx server. Once resources are available, mpiexec
initiates the launch process by first spawning its daemon network across
the allocation – in the above diagram, this is done via ssh commands.
After the daemons have launched and wired up, mpiexec sends an
application launch command to its daemons, which then start their local
client processes and debugger daemons, providing the latter with all
information required for them to attach to their targets.

#### Phase II: Initial tool-launcher connection

Would the debugger agent always be owned by the same user that submitted
the job?

What parameters would the debugger agent need to be passed?

What environment variables would the debugger agent need set?

Is it sufficient to place the debugger agent in the same cgroup(s) as
the job (without further restricting access to cores)?

When should PBS clean up (kill) debugger agents? When the initial shell
for the job exits?

Should the resources used by the debugger agents be accounted for as
though they were processes of the job itself?

    #define PMIX_SPAWN_LAUNCHER               "pmix.spwn.launcher"          // (bool) app is a user-provided launcher

#### Modifying Launcher Behavior

There are, in general, two distinct methods by which a tool can start an
application under its control:

-   **direct launch**, whereby the tool calls PMIx\_Spawn for the
    application itself (i.e., not using a launcher such as mpiexec
    in-between), thereby asking the RM to directly start the processes.
    In this case, PMIx\_Spawn provides adequate controls for specifying
    the environment of both the application (via the pmix\_app\_t array)
    and the launcher itself (via the job\_info array).
-   **indirect launch**, where PMIx\_Spawn is given *mpiexec* as the cmd
    to execute, which in turn must start the actual application. In this
    case, the tool does not have direct control over the environment of
    the application itself as the application appears solely in the argv
    of *mpiexec*.

Both cases require the ability to pass instructions to the launcher
itself (e.g., replacing fork/exec) that are not covered by envars. This
RFC proposes the following behavior-related attributes:

    /* Spawn-related Attributes */
    #define PMIX_SPAWN_LOCAL_FORK_AGENT       "pmix.spwn.lcl.frk.agnt"      // (char*) path to executable to be used (e.g., in place of fork/exec)

Additional attributes related to the actual launch process (e.g., a
method by which the tool can provide directives to the launcher prior to
actually starting the application) are described in a companion RFC:
[Support for Launching Applications Under Debugger
Tools](https://github.com/pmix/RFCs/pull/23)

Protoype Implementation
-----------------------

Provide a reference link to the accompanying Pull Request (PR) against
the PMIx master repository. If the prototype implementation has been
tested against an appropriately modified resource manager and/or client
program, then references to those prototypes should be provided. Note
that approval of any RFC will be far more likely to happen if such
validation has been performed!

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

