---
layout: default
title: Datastore Abstraction Framework
---

RFC0008
=======

Title
-----

DataStore Abstraction Framework

Abstract
--------

PMIx stores two types of data: (a) data posted by application processes
(typically for exchange amongst their peers), and (b) data posted for
lookup by others (typically used for rendezvous purposes). The former
type is supported by the put/get operations, and the data is stored on
each node in a shared memory area to facilitate access by local clients
with minimal footprint. This proposal provides a framework capable of
supporting multiple storage implementations (thru a common abstraction
interface) for the latter type of data.

Labels
------

-   \[EXTENSION\] – adds a new PMIx definition

Action
------

\[IN PROGRESS\]

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

Requirements include:

-   reliable – data cannot be lost
-   scalable – for both publish and lookup
-   key-value oriented, with string keys and arbitrary data for the
    value
-   support heterogeneous environments

A detailed description of the proposed change. The length and degree of
detail should be commensurate with the magnitude of the change. This is
not intended to be burdensome, nor are there any awards for verbosity –
but clear communication will avoid repeated requests for alterations.
The description should indicate what is being modified, both
functionally and by file name.

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

