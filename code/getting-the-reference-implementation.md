---
layout: default
title: Getting the Reference Implementation
---



Getting the Code
================

The PMIx Reference Implementation Git repository (where most active
development is done) is hosted at [GitHub](https://github.com/openpmix/openpmix).
Because the PMIx Team tries very hard to release stable and
as-bug-free-as-possible distributions, we tend to take a long time between
major releases. However, there are many useful new features (and bug fixes)
on the master branch of the repository, and users sometimes find it
advantageous to work from that branch. Additionally, for those who are
actually develop with the internals of PMIx, Git access gives the most
up-to-date versions rather than the periodic tarball access. As such, the
PMIx community provides public read-only access to the PMIx Git repository.

Be aware, however, that the head of the development code tree is **not**
guaranteed to be stable. We try very hard to not commit things that are
broken, but this is an active development tree — bugs happen. This is
actually another major reason that this tree has been made available: peer
review. If you find any bugs, please report them on the
[issues](https://github.com/openpmix/openpmix/issues) list. You are welcome to
either clone the PMIx repository, or download one of the release tarballs or
source RPM.

If you intend to work from the repository (either on the master or a release
branch), you will need a Git client to obtain the code. We recommend getting
the latest version available. If you do not have the command `git` in your
path, you will likely need to download and install [Git](http://git-scm.org/).

In addition to the code itself, the repository contains a series of Git tags
indicating where releases were made (see
[Releases](https://github.com/openpmix/openpmix/releases)) that contain the release
tarballs and source RPM. However, GitHub orders those tags according to the date
when they were created, **not** according to their release series. Thus, the
"latest release" marker is placed on the tag that was most recently created and
not on the actual current software release.

Accordingly, we **strongly** recommend that you obtain the tarball or source rpm
from the website's [Download][https://openpmix.github.io/code/downloads] location.

Github provides a simple button for obtaining the clone command. Clone
either the master any of the release branches. For example (as of Nov 2015),
to clone the main development repository via HTTPS:

```shell
    shell$ git clone https://github.com/openpmix/openpmix
    Cloning into ‘pmix’…
    remote: Counting objects: 5319, done.
    remote: Compressing objects: 100% (27/27), done.
    remote: Total 5319 (delta 5), reused 0 (delta 0), pack-reused 5291
    Receiving objects: 100% (5319/5319), 2.03 MiB | 600.00 KiB/s, done.
    Resolving deltas: 100% (3958/3958), done.
    Checking connectivity… done.
    shell$
```

Note that Git is natively capable of using many forms of web proxies. If
your network setup requires the user of a web proxy, [consult the Git
documentation for more details](http://git-scm.com/).

After obtaining a successful Git clone, the following tools (and associated
minimum versions) are required for developers to compile PMIx from its
repository sources (users who download PMIx tarballs **do not** need these tools
– they are only required for developers working on the internals of PMIx
itself):
 - [GNU m4](ftp://ftp.gnu.org/gnu/m4) – version 1.4.17
 - [GNU autoconf](ftp://ftp.gnu.org/gnu/autoconf) – version 2.69
 - [GNU automake](ftp://ftp.gnu.org/gnu/automake) – version 1.15
 - [GNU libtool](ftp://ftp.gnu.org/gnu/libtool) – version 2.4.6
 - [Flex](ftp://ftp.gnu.org/non-gnu/flex) – version 2.5.35

Autotools notes:
 - Other version combinations may work, but are untested and unsupported. In
   particular, developers tend to use higher versions of Autotools for
   master/development work, and they usually work fine.
 - Although it should probably be assumed, you’ll also need a C/C++
   compiler.
 - The [HACKING](https://github.com/pmix/pmix/blob/master/HACKING) file in
   the top-level directory of the PMIx checkout details how to install the
   tools listed above and the steps required to build a developer checkout
   of PMIx. It always contains the most current information on how to build
   a developer’s copy of PMIx.

NOTE: by default, when configuring and building PMIx from a developer
checkout, *all* debugging code is enabled. This results in a significant
run-time performance penalty. There are several options for building an
optimized PMIx reference library; see the HACKING file for more details.

NOTE: Most Linux distributions and OS X install Flex by default (and this is
sufficient). Other operating systems may provide `lex`, but this **is not**
sufficient — `flex` is required.

[Preparing Autotools](/code/building-autotools)

[Building the library](/code/building-the-reference-implementation)

