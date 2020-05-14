---
layout: default
title: PMIx Support for Storage Systems
---

RFC0021
=======

Title
-----

PMIx Support for Storage Systems

Abstract
--------

Exascale systems expect to access information that resides in an array
of storage media, ranging from offline archives to streaming data flows.
This "tiered storage" architecture presents a challenge to application
developers and system managers striving to achieve high system
efficiency and performance. Multiple vendor-specific packages have been
developed, each with its own unique API and associated data structures.
However, this results in a corresponding loss in application portability
and increased cost of customer migration across procurements.

These API and attribute definitions are based on recognition that
gaining multi-vendor agreement on common interfaces and data structures
is a difficult and long-term objective. Thus, this RFC proposes a more
flexible approach that allows vendor independence by defining an
abstraction layer for passing storage-related requests and directives
based on PMIx APIs and data structures.

Labels
------

\[EXTENSION\]\[CLIENT-API\]\[SERVER-API\]\[RM-INTERFACE\]

Action
------

\[IN PROGRESS\]

Copyright Notice
----------------

Copyright 2017 Intel, Inc. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

Protoype Implementation
-----------------------

Provide a reference link to the accompanying Pull Request (PR) against
the PMIx master repository. If the prototype implementation has been
tested against an appropriately modified resource manager and/or client
program, then references to those prototypes should be provided. Note
that approval of any RFC will be far more likely to happen if such
validation has been performed!

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

