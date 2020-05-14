---
layout: default
title: Getting the PMIx Reference Server
---

Getting the Code
================

The PMIx Reference RunTime Environment (PRRTE) Git repository (where most
active development is done) is hosted at
[GitHub](https://github.com/pmix/prrte). At this time, the PMIx team has not
issued any stable point releases of PRRTE. However, this is expected to begin
fairly soon. Meantime, there are many useful new features (and bug fixes) on
the master branch of the repository, and users sometimes find it advantageous
to work from that branch.

Be aware, however, that the head of the development code tree is not guaranteed
to be stable. We try very hard to not commit things that are broken, but this
is an active development tree — bugs happen. When you find any bugs (and you
undoubtedly will), please report them on the
[issues](https://github.com/pmix/prrte/issues) list. The PMIx community
provides public read-only access to the PRRTE Git repository, but please feel
free to post pull requests – they are always welcome!

You will need a Git client to obtain the code. We recommend getting the latest
version available. If you do not have the command git in your path, you will
likely need to download and install [Git](http://git-scm.org/).

Github provides a simple button for obtaining the clone command. Clone either
the master any of the release branches. For example (as of Jan 2018), to clone
the main development repository via HTTPS:

```
    shell$ git clone https://github.com/pmix/prrte
    Cloning into ‘prrte’…
    remote: Counting objects: 394300, done.
    remote: Compressing objects: 100% (61/61), done.
    remote: Total 394300 (delta 35), reused 31 (delta 18), pack-reused 394221
    Receiving objects: 100% (394300/394300), 109.61 MiB | 921.00 KiB/s, done.
    Resolving deltas: 100% (322492/322492), done.
    Checking connectivity… done.
    shell$
```

Note that Git is natively capable of using many forms of web proxies. If your
network setup requires the user of a web proxy, [consult the Git documentation
for more details](http://git-scm.com/).

After obtaining a successful Git clone, the following tools (and associated
minimum versions) are required for developers to compile PRRTE from its
repository sources:

 - [GNU m4](ftp://ftp.gnu.org/gnu/m4) – version 1.4.17
 - [GNU autoconf](ftp://ftp.gnu.org/gnu/autoconf) – version 2.69
 - [GNU automake](ftp://ftp.gnu.org/gnu/automake) – version 1.15
 - [GNU libtool](ftp://ftp.gnu.org/gnu/libtool) – version 2.4.6
 - [Flex](ftp://ftp.gnu.org/non-gnu/flex) – version 2.5.35



Critical Note
=============

As of May 29, 2018, PRRTE no longer carries embedded copies of libevent, HWLOC,
or PMIx. All three are required for PRRTE to build and operate. Most
distributions carry libevent and hwloc packages, and PRRTE is fairly flexible
on its version requirements. However, PMIx is not yet as widespread in its
availability, and you may find it necessary to download and build it yourself.

Supported versions are shown below. For convenience, we include a link to the project’s web site in case you need (or choose) to install it directly:

 - [libevent](https://https//libevent.org) – version 2.0.21, 2.0.22, or 2.1.8
 - [hwloc](https://www.open-mpi.org/projects/hwloc/) – version 2.0.1 or 1.11.x
 - [PMIx](https://github.com/pmix/pmix/) – version 2.1.1 or later (github
   master recommended)

Notes
=====

Autotools notes:

 - Other version combinations may work, but are untested and unsupported. In
   particular, developers tend to use higher versions of Autotools for
   master/development work, and they usually work fine.
 - Although it should probably be assumed, you’ll also need a C/C++ compiler.
 - The [HACKING](https://github.com/pmix/prrte/blob/master/HACKING) file in the
   top-level directory of the checkout details how to install the tools listed
   above and the steps required to build a developer checkout of PRRTE. It
   always contains the most current information on how to build a developer’s
   copy of it.

NOTE: by default, when configuring and building PRRTE from a developer
checkout, all debugging code is enabled. This results in a significant run-time
performance penalty. There are several options for building an optimized PRRTE;
see the HACKING file for more details.

NOTE: Most Linux distributions and OS X install Flex by default (and this is
sufficient). Other operating systems may provide `lex`, but this **is not**
sufficient — `flex` is required.

[Preparing Autotools](/code/building-autotools)

[Building PRRTE](/code/building-the-pmix-reference-server)

