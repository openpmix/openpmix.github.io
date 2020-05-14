---
layout: default
title: Slurm Support
---

Slurm support for PMIx was first included in v16.05 based on the PMIx
v1.2 release. It has since been updated to support the PMIx v2.x series,
as per the following table:

<span id="compat">**Slurm/PMIx Compatibility Matrix**</span>

-   Slurm 16.05+ supports only the PMIx v1.x series, starting with
    v1.2.0. These Slurm versions specifically do **not** support PMIx
    v2.x and above
-   Slurm 17.11.0+ supports both PMIx v1.2+ and v2.x.

Distributions provide separate RPMs for Slurm’s PMIx support. If
installing from source, note that an appropriate version of PMIx must be
installed prior to building Slurm! More details are provided
[below](#building).

The following discussion assumes that you are using a version of Slurm
that supports PMIx.

**Backward Compatibility**

PMIx can be used in one of two ways: either directly via PMIx APIs, or
via the backward compatibility interfaces that support the PMI-1 and
PMI-2 APIs. When backward compatibility is enabled at configure (which
is the default), PMIx provides both libpmi and libpmi2 libraries that
contain the respective APIs and a copy of the PMIx library – each API is
translated into its PMIx equivalent. This was done at the request of
users whose apps/libs were hardcoded to dlopen “libpmi” or “libpmi2”.
Unfortunately, Slurm also includes plugins for those versions of PMI,
and the PMI-1 plugin is built by default (the PMI-2 plugin must be
manually built and installed). Thus, there is a potential installation
conflict between the Slurm and PMIx versions of libpmi and libpmi2.

We recommend installing Slurm and PMIx in different (non-default)
locations to avoid the conflict. Alternatively, the distributions are
modifying their packaging plan to move the PMI support for Slurm into a
separate libpmi-slurm rpm, and doing the same with the PMI-1 and PMI-2
support from PMIx (the precise naming of these packages can be
distro-dependent). These rpm’s will then be setup to generate a conflict
if someone attempts to install both of them in the same location. Note
that this will **not** resolve the problem if, for example, Slurm is
installed via rpm but PMIx is installed from source as no conflict check
is made.

Further complicating the situation is the inherent incompatibility of
the Slurm vs PMIx PMI-1 and PMI-2 implementations. If you build your
application and link it against “libpmi2”, and that library is actually
the one from PMIx, then it won’t work with Slurm’s PMI-2 plugin because
the communication protocols are completely different. The same is true
for the PMI-1 plugin. Thus, it is necessary that the PMIx plugin be
invoked even when utilizing either PMI-1 or PMI-2 interfaces via the
PMIx backward compatibility feature.

There are a couple of reasons why you might want to use the PMIx
backward compatibility in place of the native Slurm plugins. First,
installing and using the PMIx libraries provides access to the PMIx APIs
even if your underlying library doesn’t use them. This allows your
application code to, for example, take advantage of event notification,
allocation request support, and other PMIx features – all of which are
directly accessible to the application.

Second, there are some launch performance enhancements implemented in
the more recent PMIx plugin (starting with Slurm 17.11) which will be
utilized even through the backward compatible PMI-1 or PMI-2 interfaces,
but are not available if using the Slurm PMI plugins. These are
explained further [below](#ucx).

So if you want to use PMIx backward compatibility, you need to:

1.  link against either libpmix or the libpmi\[2\] libraries exported by
    PMIx. Note that if you are using PMI-1 or PMI-2 and both the Slurm
    and PMIx libpmi\[2\] are installed, then you must ensure that the
    path to the PMIx libpmi\[2\] versions is first in your
    LD\_LIBRARY\_PATH to avoid loading the incorrect library; and
2.  specify –mpi=pmix on the srun cmd line (regardless of whether or not
    your application or its underlying library uses the PMI-1 or PMI-2
    APIs).

Most of the standard PMI2 calls are covered by the backward
compatibility libraries, so things like MPICH should work out-of-the-box
(and tests confirm it does). However, MVAPICH2 added a PMI2 extension
call to the Slurm PMI2 library that they use and PMIx doesn’t cover (as
there really isn’t an easy equivalent, and they called it PMIX\_foo
which causes a naming conflict). Thus, MVAPICH2 users wanting to use the
PMIx backward compatibility library must be careful to build MVAPICH2
against the PMIx PMI-2 header and *not* the one from Slurm.

<span id="building">**Building from Source**</span>

Building Slurm with PMIx support from source is fairly simple to do. It
begins with installing an appropriate PMIx release as per the above
[table](#compat). Instructions for
[obtaining](/code/getting-the-reference-implementation)
and
[installing](/code/building-the-reference-implementation)
PMIx are provided elsewhere.

If PMIx was installed to a standard location (i.e., with a prefix of
/usr or /usr/local), then Slurm will find it and build the PMIx plugin
by default. Otherwise, Slurm should be configured with the
*–with-pmix=path-to-where-pmix-was-installed* option. The PMIx plugin
will be built and installed under the Slurm location.

Starting with Slurm 17.11, it is possible to build against multiple PMIx
versions. For example, building against both PMIx versions 1.2 and 2.1
can be done by specifying *–with-pmix=path-to-1.2:path-to-2.1* on the
Slurm configure line. When submitting a job, the desired version can
then be selected using either the *–mpi=pmix\_v1* or *–mpi=pmix\_v2*
command line options for “srun”. If the non-version-specific *–mpi=pmix*
is given, then the highest installed PMIx version will be used.

**Executing Applications**  
Executing an application using the Slurm PMIx plugin (whether via the
native PMIx or the backward compatibility APIs) requires that one add
*–mpi=pmix* (or a version-specific directive) to the srun command line.
Alternatively, a system administrator can designate the desired PMIx
plugin as the default in the slurm.conf file.

<span id="ucx">**Using the UCX Extension**</span>

Starting with the Slurm 17.11 release, the PMIx plugin was extended to
support several new features:

-   Direct point-to-point connections (Direct-connect) for Out-Of-Band
    (OOB) communications. Prior to 17.11, Slurm was using its own
    internal RPC mechanism that is very convenient but has some
    performance-related issues. According to our measurements, this new
    feature significantly improves Slurm/PMIx performance in the
    *direct-modex* case [presented at the Slurm booth during
    Supercomputing 2017](https://slurm.schedmd.com/SC17/Mellanox_Slurm_pmix_UCX_backend_v4.pdf).
    By default this mode is turned on and uses a TCP-based
    implementation.
-   If Slurm is configured to use the [UCX](http://www.openucx.org/)
    communication framework via the *–with-ucx=path-to-UCX-installation*
    option, the PMIx plugin will use a UCX-based implementation of the
    Direct-connect transport to provide an even greater performance
    boost on InfiniBand-based clusters.
-   “Early-wireup” option to pre-connect Slurm step daemons before an
    application starts using the OOB channel (i.e., prior to calling PMI
    or PMIx interfaces).

As the SC’17 presentation shows, the new features demonstrated good
results on a small scale. Further validation at larger scales is
underway.

All the new features are controllable at runtime on a per-jobstep basis
using the following environmental variables (envars):

-   Direct-connect is enabled or not using
    *SLURM\_PMIX\_DIRECT\_CONN={true|false}*. By default, TCP-based
    Direct-connect is used if Slurm wasn’t configured with UCX.
-   If UCX support was included during configuration, its use can be
    controlled through the *SLURM\_PMIX\_DIRECT\_CONN\_UCX={true|false}*
    envar. This envar is ignored if UCX support wasn’t included.
-   the Early-wireup option pre-connects the UCX-based communication
    tree in parallel with application initialization to enable UCX from
    the very first OOB communication. This feature is turned off by
    default, but can be controlled using the
    *SLURM\_PMIX\_DIRECT\_CONN\_EARLY={true | false}* envar.
-   You may also want to specify UCX network device (i.e.
    UCX\_NET\_DEVICES=mlx5\_0:1) and the transport (UCX\_TLS=dc). For
    now it is recommended to use DC as a transport (full RC support will
    be implemented in an upcoming Slurm release). Currently, you have to
    set the global envar (like UCX\_TLS) which also impacts device
    selection in the application and its library, but we plan to
    introduce prefixed envars (like UCX\_SLURM\_TLS and
    UCX\_SLURM\_NET\_DEVICES) in an upcoming Slurm release for finer
    grained control over communication resource usage.

The [SC’17 presentation](https://slurm.schedmd.com/SC17/Mellanox_Slurm_pmix_UCX_backend_v4.pdf)
includes two backup slides explaining how to enable point-to-point and
collectives micro-benchmarks integrated into the PMIx plugin to get some
basic reference number for the performance on your system.

