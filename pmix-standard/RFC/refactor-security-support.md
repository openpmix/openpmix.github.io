---
layout: page
title: Refactor Security Support
---

RFC0011
=======

Title
-----

Refactor existing security support into a new PSEC framework

Abstract
--------

This RFC refactors the existing security support code into the new MCA
infrastructure, creating a PSEC framework containing initial native and
munge plugins.

Labels
------

-   \[ORGANIZATION\]

Action
------

\[APPROVED\]

Copyright Notice
----------------

Copyright (c) 2016 Intel, Inc. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

The MCA infrastructure was added to PMIx to support the use of dynamic
plugins. One such use-case provides the ability to easily extend support
for additional security protocols to authenticate connections between
the client and server. This RFC introduces the PSEC framework for that
purpose, moving the existing code from the src/sec directory into two
new plugins ("native" and "munge").

Selection of the plugin to be used by a client is based on options
provided by the server. When the server is called to setup a client’s
environment, it will add an envar called *PMIX\_SECURITY\_MODE*
containing the comma-delimited list of active PSEC plugins on the
server.

Upon initial connection, the client will select its active plugin by
picking the highest priority plugin whose name is contained in the list
provided by the server. The client then passes the name of the selected
plugin to the server during the connection handshake procedure, and the
server selects the matching plugin to use with that client.

Legacy clients connect to the server via a separate rendezvous point.
Thus, the server knows that any client connecting via that point will
not provide the updated plugin information. In this case, the server has
no choice but to take the default PSEC plugin, returning an error if the
client is using a different protocol.

Tool connection cannot operate in quite the same manner because the
tool, not having been spawned by the server, has no access to the
server’s list of active plugins. Instead, the tool initiates its
connection to the server and includes its list of available plugins. The
server then picks the highest priority available plugin from that list,
returning an error if no matching plugin is available.

The selected plugins are called whenever security operations need to be
performed. Thus, each server-client pairing can support whatever
security option they uniquely select.

Protoype Implementation
-----------------------

The PMIx library implementation is covered in the [Add the PSEC
framework](https://github.com/pmix/master/pull/137) pull request. The
prototype has been tested against Open MPI as referenced in an upcoming
pull request.

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

