---
title: Code
permalink: /code/
---



PMIx Reference Implementation
=============================
 - TODO: Coverity Scan Build Status

The very breadth of PMIx’s scope can present a challenge to adoption by SMS
vendors and programming library developers. Accordingly, the PMIx community
has developed and released a PMIx “reference implementation” containing a
complete implementation of the PMIx standard, each release being tied
directly to a corresponding revision level of the standard.

The reference implementation itself is not part of the PMIx standard, nor is
its use in any way required. Any implementation that supports the defined
APIs is perfectly acceptable, and some environments may choose to pursue
that route. The reference code is provided solely for the following
purposes:
 - Validation of the standard. No proposed change and/or extension to the
   standard is accepted without an accompanying prototype implementation in
   the reference library. This ensures that the proposal has undergone at
   least some minimal level of scrutiny and testing before being considered.
 - Ease of adoption. The PMIx reference library is designed to be
   particularly easy for resource managers (and the SMS in general) to
   adopt, thus facilitating a rapid uptake into that community for
   application portability. Both client and server libraries are included,
   along with reference examples of client usage and server-side
   integration. A list of supported environments and versions is provided
   [here](FIXME:etc) – please check regularly as the list is changing!

The reference implementation targets support for the Linux operating system.
A reasonable effort is made to support all major, modern Linux
distributions; however, validation is limited to the most recent 2-3
releases of RedHat Enterprise Linux (RHEL), Fedora, CentOS, and SUSE Linux
Enterprise Server (SLES). In addition, development support is maintained for
Mac OSX. Production support for vendor-specific operating systems is
included as provided by the vendor.

More information on obtaining and building the reference implementation is
available [here](/code/getting-the-reference-implementation).



PMIx Reference RunTime Environment (PRRTE)
==========================================
 - TODO: Coverity Scan Build Status

Similarly, the PMIx community has released a “Reference RunTime Environment”
— i.e., a runtime environment containing the reference implementation and
capable of operating within a host SMS. The reference RTE therefore provides
an easy way of exploring PMIx capabilities and testing PMIx-based
applications outside of a PMIx-enabled environment.

More information on obtaining and building the PMIx Reference RTE is
available [here](/code/getting-the-pmix-reference-server)



Developer’s Telecon
===================

The PMIx developers meet weekly on Thursdays at noon US Pacific to discuss
the standard, implementation issues, and release roadmap. The meeting is
open to all interested parties. Meeting information is available
[here](https://recaptcha.open-mpi.org/pmix-recaptcha/).



Working Group Meetings
======================

 - The OpenMP/MPI Working Group is currently taking a break while
   researchers investigate best paths forward. The results of the initial
   work was captured in an RFC that updated the PMIx v3 Standard


