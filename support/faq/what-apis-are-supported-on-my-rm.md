---
layout: page
title: What APIs and Attributes are Supported on my RM?
---

As PMIx does not require that a particular environment (or even PMIx
implementation) support all APIs and/or associated attributes, it can
sometimes be difficult to determine the available support on a given
system. This is particularly worrisome when porting applications and
containers across environments, and users have requested that some
API-based mechanism be made available for querying the local level of
support.

The PMIx\_Query API provides a mechanism for meeting this need. On
systems that support it, applications can request a list of supported
APIs and attributes for each API from the client PMIx library, the PMIx
server, and the host environment.

More details to come.

