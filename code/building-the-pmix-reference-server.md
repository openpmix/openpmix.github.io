---
layout: default
title: Building the PMIx Reference Server
---

Debugging vs. Optimized Builds
==============================

If you are building the PMIx Reference RunTime Environment (PRRTE) from a Git checkout, the default build includes a lot of debugging features. This happens automatically when when configure detects the hidden “.git” Git meta directory (that is present in all Git checkouts) in your source tree, and therefore activates a number of developer-only debugging features in the PMIx code base.

By definition, debugging builds will perform much slower than optimized builds of the server. You should **NOT** conduct timing tests or try to run production performance numbers with debugging builds.

If you wish to build an optimized version of the server from a developer’s
checkout, you have two main options:

 - Use a VPATH build. Simply build the reference server from a different
   directory than the source tree — one where the .git subdirectory is not
   present. For example:

   ```
        shell$ git clone git@github.com:pmix/prrte
        shell$ cd prrte
        shell$ ./autogen.pl
        shell$ mkdir build
        shell$ cd build
        shell$ ../configure …
        […lots of output…]
        shell$ make all install
   ```

 - Manually specify configure options to disable all the debugging options.
   You’ll need to carefully examine the output of “./configure –help” to see
   which options to disable. They are all listed, but some are less obvious
   than others (they are not listed here because it is a changing set of flags;
   by Murphy’s Law, listing them here will pretty much guarantee that this file
   will get out of date):

   ```
        shell$ ./configure –disable-debug …
        […lots of output…]
        shell$ make all install 
   ```


Building PRRTE
==============

PRRTE requires three external packages (libevent, hwloc, and PMIx) to be
supplied for it to build and execute. Details on the necessary versions are
provided [here](/code/getting-the-pmix-reference-server).  The
procedure for building a usable configuration is as follows:

 - Configure and build libevent, or install it from rpm (most distributions
   supply it at an acceptable version)

 - Configure and build hwloc, or install it from rpm (most distributions supply
   it at an acceptable version)

 - Configure and build the PMIx library against the libevent and the hwloc
   packages. If these are installed in a standard location, no configuration
   option need be given – otherwise, you will need to configure PMIx with the
   “–with-libevent=path-to-libevent-installation
   –with-hwloc=path-to-hwloc-installation” options. For example, if libevent
   was installed in /home/me/libevent, then you would need to configure PMIx
   “–with-libevent=/home/me/libevent”.

 - Configure and build PRRTE, specifying the location of the PMIx, libevent,
   and hwloc packages. Assuming PMIx was installed to /home/me/pmix, libevent
   was installed to /home/me/libevent, and hwloc was installed to
   /home/me/hwloc, then the configuration line would include the following:

   ```
     --with-pmix=/home/me/pmix --with-libevent=/home/me/libevent --with-hwloc=/home/me/hwloc
   ```


With all packages built and installed, ensure that you have PRRTE’s install location prepended to your PATH and LD_LIBRARY_PATH. Compile any PMIx-based applications using the PRRTE-provided pcc wrapper compiler. Execution of an application is then done as described [here](/support/how-to/running-apps-under-psrvr).


Building Open MPI for use with PRRTE
====================================

Open MPI contains embedded versions of several libraries, including PMIx.
While you may be able to use PRRTE to run Open MPI applications that are linked
against their internal versions of libevent, hwloc, and PMIx, there is a chance
you may run into conflicts. Executing OMPI apps against PRRTE is lightly tested
using OMPI releases prior to OMPI v4.0 and should be considered experimental
until we receive better validation. However, the OMPI master branch includes
the ability to build OMPI against external copies of the common packages and to
execute directly against PMIx. This removes the ORTE runtime from the OMPI
application and provides a cleaner PMIx interface.


Configuring and building Open MPI for this purpose mirrors that for building
PRRTE:

 - Configure and build libevent, or install it from rpm (most distributions
   supply it at an acceptable version)

 - Configure and build hwloc, or install it from rpm (most distributions supply
   it at an acceptable version)

 - Configure and build the PMIx library against the libevent and the hwloc
   packages. If these are installed in a standard location, no configuration
   option need be given – otherwise, you will need to configure PMIx with the
   “–with-libevent=path-to-libevent-installation
   –with-hwloc=path-to-hwloc-installation” options. For example, if libevent
   was installed in /home/me/libevent, then you would need to configure PMIx
   “–with-libevent=/home/me/libevent”.

 - Configure and build Open MPI, specifying the location of the PMIx, libevent,
   and hwloc packages and adding a directive to directly use PMIx. Assuming
   PMIx was installed to /home/me/pmix, libevent was installed to
   /home/me/libevent, and hwloc was installed to /home/me/hwloc, then the
   configuration line would include the following:

   ```
     --with-pmix=/home/me/pmix --with-libevent=/home/me/libevent --with-hwloc=/home/me/hwloc --with-ompi-pmix-rte
   ```

Although the OMPI application is not linked against PRRTE libraries, use of the
external PMIx, libevent, and hwloc libraries is highly recommended to ensure
proper operation. Note that testing of OMPI against PRRTE is performed using
the recommended configuration, and therefore alternative configurations should
be considered experimental until validated.


