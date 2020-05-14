---
layout: page
title: Running Applications with the PMIx Reference RunTime Environment (PRRTE)
---

Starting PRRTE
--------------

The PMIx Reference RunTime Environment (PRRTE) is started by a simple
execution of the *prte* command. The server does not have an internal
scheduler, and thus must be given an allocation of resources for its
use. This can be done by obtaining an allocation in either of two ways:

-   If you are operating in a managed environment (i.e., under the
    control of a resource manager such as Slurm or PBSPro), then you
    must first obtain an allocation before starting PRRTE. The *prte*
    executable knows how to automatically pickup the allocation for most
    available RMs, and so nothing need be added to the cmd line. The
    PRRTE package will usually identify the presence of the managed
    environment and configure itself accordingly – if the environment
    was not installed in a standard location, then you may need to point
    the configure code to it with an appropriate configure option.
-   If you are operating in an unmanaged environment, then you need to
    provide either a hostfile (sometimes called a “machinefile”) that
    specifies the hosts to be used, or a -host list of hosts to be used.
    -   for **-hostfile filename**, the file consists of a single
        line/host that starts with the name of the host. You can
        optionally add a “slots=N” to indicate the number of process
        that can be assigned to the host. If this is not provided, then
        *psrvr* will automatically detect the number of cores on each
        node and set the slots to that number
    -   In the **-host** case, be aware that each listed host will be
        assigned only a single slot for a process – this can be changed
        by adding the “:N” modifier to the host name to indicate the
        number of processes that can be assigned to that host. For
        example, the cmd line:  
        `$ prte -host foo:13,bar:21`  
        will launch PRRTE on host foo (assigning 13 slots for processes
        on that node) and on bar (assigning 21 slots on that node).

*prte* will launch a daemon on each node to create a distributed virtual
machine, and will print “DVM ready” when complete. At this point, the
server is ready to accept commands and execute applications.

Multiple users can each launch their own PRRTE across the same nodes –
this is often helpful on unmanaged development clusters. Each daemon
(plus *prte* itself) includes a PMIx server that will “drop” a local
rendezvous point by which tools such as *prun* can automatically connect
to it. These are placed in locations that include both the nodename and
the user id in their path to avoid conflict. *prun* will automatically
find the PRRTE instance associated with the user when executing
applications.

Note that daemons can also be started with the –system-server option to
simulate the situation where a PMIx-enabled RM resides on the system,
with (perhaps multiple) PMIx-enabled jobs executing beneath it – note
that only one daemon can be so designated per node.

The server does not automatically place itself into the background – you
can direct it to do so using the standard methods, if you so choose. The
*prte* command supports a number of options – you are welcome to use
“–help” to investigate them.

When you are done, the server can be terminated with the *prun
–terminate* command.

Running non-MPI Applications
----------------------------

Running applications using PRRTE is relatively simple. It starts with
prepending the install location for PRRTE to your PATH and
LD\_LIBRARY\_PATH environmental variables. This ensures that you will
correctly access PRRTE’s tools and libraries.

Non-MPI applications that utilize PMIx can be compiled using the *pcc*
wrapper compiler. PRRTE automatically builds all dependencies into it,
including pointing the compiler to the installed PMIx headers and
libraries. You can see the final command line issued by the wrapper
compiler using the “–showme” option:

    $ pcc --showme
    gcc -I/home/common/pmix/build/psrv/include/openmpi -I/home/common/local/include -I/home/common/pmix/build/psrv/include -pthread -L/home/common/local/lib -L/home/common/local/lib64 -Wl,-rpath -Wl,/home/common/local/lib -Wl,-rpath -Wl,/home/common/local/lib64 -Wl,-rpath -Wl,/home/common/pmix/build/psrv/lib -Wl,--enable-new-dtags -lpmix -L/home/common/pmix/build/psrv/lib -lpsrvropen-pal

Executing an application requires that PRRTE first be started as per the
above directions. Once the server is ready, applications can be executed
via the *prun* command. As with *prte*, *prun* supports a number of
options – you are welcome to use “–help” to investigate them. Most
importantly, the “–terminate” option is used to order PRRTE to stop,
terminate its daemons, cleanup any temporary files, and exit.

Running MPI Applications
------------------------

PRRTE is quite capable of executing any PMIx-based MPI applications.
Doing so with Open MPI, however, requires a little care when configuring
the two code bases as they share common symbols – PRRTE is itself a fork
of the Open MPI master branch that has been tailored to operate as a
standalone system. The points of contact are the PMIx library itself,
the libevent library, and the hwloc library that are used by both code
bases. Accordingly, it is required that both OMPI and PRRTE code bases
be configured against a common copy of these packages. For instructions
on how to properly do this, see
[here](/code/building-the-pmix-reference-server).

We recommend that non-OMPI MPI packages also build against the common
PMIx package being used by PRRTE. Again, this isn’t required, although
the PMIx version being used by the MPI package must at least be at
version 2.1.1.

With the packages all built and installed, ensure that you have both the
PRRTE and MPI install locations prepended to your PATH and
LD\_LIBRARY\_PATH. Compile any MPI applications using their
corresponding wrapper compiler, and any non-MPI PMIx-based applications
using the PRRTE-provided *pcc* wrapper compiler. Execution of an
application is then done as described above – there is nothing special
required (e.g., command-line options) for an MPI application.

