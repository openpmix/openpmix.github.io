---
layout: page
title: Which Environments Include Support for PMIx?
---

While we make every effort to keep this list current, it is entirely
possible that an environment has recently added PMIx support that we
missed and/or don’t know about. We welcome suggests/comments on
coverage!

Programming Libraries
---------------------

#### MPI

-   [Open MPI](https://www.open-mpi.org/): all versions starting with
    v2.x, as shown below. Note that Open MPI updates its embedded PMIx
    (staying within the PMIx major release) during the course of a
    series. For example, Open MPI v3.0.0 might include a copy of PMIx
    v2.0.0 while Open MPI v3.1.0 might include PMIx v2.1.1.

    -   Open MPI v2.x: PMIx v1.2
    -   Open MPI v3.x: PMIx v2.x
    -   Open MPI v4.x: PMIx v3.x

    Open MPI’s internal runtime environment (ORTE) fully supports the
    embedded PMIx version of each release and can therefore launch and
    support compatible PMIx-enabled applications (see an explanation of
    cross-version compatibility
    [here](../how-does-pmix-work-with-containers/index.html)).

-   [Spectrum MPI](https://www.ibm.com/us-en/marketplace/spectrum-mpi):
    All versions of Spectrum MPI, based on Open MPI, support PMIx, as
    shown below (\* indicates that the release included additional PMIx
    modifications that were later upstreamed):
    -   Spectrum MPI 10.1.0.0 : PMIx 1.1.2\*
    -   Spectrum MPI 10.2.0.0 : PMIx 2.0.3
    -   Spectrum MPI 10.2.0.10 : PMIx 2.2.0
    -   Spectrum MPI 10.3.0.0 : PMIx 3.1.2\*

-   Fujitsu MPI: Further details pending. Last known supported version
    was PMIx v2.2

-   MPICH: Support for PMIx was added in MPICH version 3.3 using the ch4
    device configuration. Support is tested regularly against PMIx v2.1.
    Example configurations include:
    -   \`–with-device=ch4:ofi \[–with-libfabric=path/to/install\]
        –with-pmi=pmix \[–with-pmix=path/to/install\] –with-pm=no\`
    -   \`–with-device=ch4:ucx \[–with-ucx=path/to/install\]
        –with-pmi=pmix \[–with-pmix=path/to/install\] –with-pm=no\`

-   HPE-MPI: Further details pending.

-   Mellanox HPC-X MPI: [HPC-X MPI](http://www.mellanox.com/page/products_dyn?product_family=195&mtag=hpcx_mpi)
    is based on Open MPI and derives its PMIx portability
    characteristics from that code base. The following versions of PMIx
    are supported by HPC-X:
    -   HPC-X v1.9: PMIx v1.2
    -   HPC-X v2.0: PMIx v2.x
    -   HPC-X v2.1: PMIx v2.x
    -   HPC-X v2.3: PMIx v2.x
    -   HPC-X v2.4: PMIx v3.x

#### OpenSHMEM

-   Reference(Stonybrook): Further details pending. Last known supported
    PMIx version was v3.x
-   Mellanox: [HPC-X OpenSHMEM](http://www.mellanox.com/page/products_dyn?product_family=133&mtag=scalableshmem)
    is based on the Open MPI OpenSHMEM implementation. See the HPC-X MPI
    section for PMIx support details.
-   Sandia: [SOS](https://github.com/Sandia-OpenSHMEM/SOS) supports PMIx
    starting with the v1.3.4 and v1.4.x releases. All PMIx versions
    above v2.1.0 are supported
-   Oak Ridge Extreme-scale OpenSHMEM (OREO): Further details pending.
    Currently validated against the PMIx v2.0.3 release

Resource Managers
-----------------

-   Slurm ([SchedMD](https://www.schedmd.com/)): Slurm has support for
    the PMIx standard in a form of a plugin. This allows Slurm to launch
    PMIx clients using the “srun” launcher if the proper PMIx plugin is
    specified through an “–mpi” parameter as shown below:

    > $ srun -N 4 –mpi=pmix ./some-mpi-app

    Slurm/PMIx compatibility has been validated for the following
    combinations:

    -   Slurm v16.05: PMIx v1.x
    -   Slurm v17.11: PMIx v1.x, v2.x
    -   Slurm v18.08: PMIx v1.x, v2.x, v3.x

    In order to support PMIx, Slurm has to be configured with it using
    “–with-pmix” parameter of the configure script shipped with Slurm
    distribution. It is possible to specify multiple versions of PMIx
    simultaneously:

    > $ ./configure
    > –with-pmix=&lt;path-to-pmix-vX&gt;\[:&lt;path-to-pmix-vY&gt;\[:&lt;path-to-pmix-vZ&gt;\]\]
    > …

    Only the PMIx versions supported by particular Slurm distribution
    can be used. In this case the plugin names will have a version
    suffix, i.e. “pmix\_v1”, “pmix\_v2”, “pmix\_v3”, etc. as shown
    below:

    > $ srun -N 4 –mpi=pmix\_v1 ./some-mpi-app \# To launch with PMIx
    > v1.x based plugin
    > $ srun -N 4 –mpi=pmix\_v2 ./some-mpi-app \# To launch the same
    > application with PMIx v2.x

    The list of supported “mpi” plugins on the particular system can be
    found using the srun command, where the “pmix” name is an alias to
    the most recent PMIx version available:

    > $ srun –mpi=list
    >
    > > srun: MPI types are...
    > > srun: none
    > > srun: pmix\_v3
    > > srun: pmix\_v2
    > > srun: pmix\_v1
    > > srun: pmi2
    > > srun: openmpi
    > > srun: pmix

-   [Job Step Manager (IBM)](https://www.ibm.com/support/knowledgecenter/en/SSWRJV_10.1.0/jsm/10.3/base/jsm_kickoff.html)
    All versions of the IBM Job Step Manager (JSM) support PMIx, as
    shown below (\* indicates that the release included additional PMIx
    modifications that were later upstreamed):
    -   JSM 10.1.0.0 : PMIx 1.1.2\*
    -   JSM 10.2.0.0 : PMIx 2.0.3
    -   JSM 10.2.0.10 : PMIx 2.2.0
    -   JSM 10.3.0.0 : PMIx 3.1.2\*:

-   Fujitsu: Further details pending. Last known supported version was
    PMIx v2.2

-   [ParaStation Management](https://github.com/ParaStation/psmgmt): an
    RMS developed by ParTec Cluster Competence Center GmbH as part of
    the ParaStation Modulo tool suite. The suite includes its own
    MPICH-based MPI implem,entation, a cluster provisioning and
    management system, a node sanity management framework, and a
    Trac-based ticket manager. More information on supported PMIx
    versions will be forthcoming.

-   [PBSPro](https://www.pbspro.org/) (Altair): Upcoming release will
    target support for traditional wireup interfaces (Put, Commit,
    Fence, Get), including support for “instant on” operations where
    available from the network vendor. Long-term plan is to support the
    full PMIx functional range.

RunTime Environments
--------------------

-   [PMIx Reference RunTime Environment (PRRTE)](https://github.com/pmix/prrte): a runtime environment based
    on the PMIx Reference Implementation (PRI) and capable of operating
    within a host SMS. PRRTE provides an easy way of exploring PMIx
    capabilities and testing PMIx-based applications outside of a
    PMIx-enabled environment by providing a “shim” between the
    application and the host environment that includes full support for
    the PRI. The intent of PRRTE is not to replace any existing
    production environment, but rather to enable developers to work on
    systems that do not yet feature a PMIx-enabled host SMS or one that
    lacks a PMIx feature of interest. PRRTE has been validated to
    support all PMIx versions at or above v2.0.0.

