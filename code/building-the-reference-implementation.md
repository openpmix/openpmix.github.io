---
layout: default
title: Building the Reference Implementation
---

Debugging vs. Optimized Builds
==============================

If you are building PMIx from a Git checkout, the default build includes a
lot of debugging features. This happens automatically when when configure
detects the hidden “.git” Git meta directory (that is present in all Git
checkouts) in your source tree, and therefore activates a number of
developer-only debugging features in the PMIx code base.

By definition, debugging builds will perform much slower than optimized
builds of PMIx. You should **NOT** conduct timing tests or try to run
production performance numbers with debugging builds.

If you wish to build an optimized version of PMIx from a developer’s
checkout, you have two main options:

 - Use a VPATH build. Simply build PMIx from a different directory than the
   source tree — one where the .git subdirectory is not present. For
   example:

    ```
        shell$ git clone https://github.com/pmix/pmix master
        shell$ cd master
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
   than others (they are not listed here because it is a changing set of
   flags; by Murphy’s Law, listing them here will pretty much guarantee that
   this file will get out of date):

    ```
        shell$ ./configure –disable-debug …
        […lots of output…]
        shell$ make all install
    ```

