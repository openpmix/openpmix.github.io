---
layout: default
title: Modify Behavior of PMIX_Get
---

RFC0009
=======

Title
-----

Modify the behavior of PMIx\_Get

Abstract
--------

This RFC simplifies and extends the processing of PMIx\_Get requests:

-   reserving the PMIx namespace key and enforcing tighter rules on the
    rank value used to store/retrieve values

-   When requesting info about a process in another job, ensuring that a
    copy of the job-level info for that job is included in the reply so
    that subsequent requests can be locally satisfied

Labels
------

\[BEHAVIOR\]

Action
------

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

Initially, PMIx was fairly loose regarding the rank provided when
executing the PMIx\_Get function. The library would check for the
requested key in two locations:

-   the job-level data provided at time of PMIx\_Init. This data could
    be marked with either PMIX\_RANK\_WILDCARD, or with a specific rank
    value. Thus, the check was made against both the wildcard and the
    specified rank (if other than wildcard).

-   the data "published" by the application itself via the PMIx\_Put
    function.

Thus, a request for a data item resulted in up to three separate hash
table lookups, thereby impacting scalable launch times. This RFC places
restrictions on the rank and key values that allow the "get" operation
to predictably complete with only a single lookup.

The restrictions enacted by this RFC are:

-   keys beginning with "pmix" are solely controlled by the PMIx
    community – i.e., the "pmix" namespace is reserved. All PMIx
    namespace keys will be stored in the job-level data according to the
    following rule:

    -   data pertaining to process-level (e.g. PMIX\_LOCAL\_RANK)
        information must be marked with the corresponding rank.

    -   data that differs by process (e.g., PMIX\_APP\_NUM,
        PMIX\_LOCAL\_SIZE) due to the location of the process or its
        membership within an application must be marked with the
        corresponding rank.

    -   data pertaining to job-level information (e.g.,
        PMIX\_UNIV\_SIZE) will be marked with the PMIX\_RANK\_WILDCARD
        rank.

-   data published by an application via the PMIx\_Put function must
    have a key that lies outside the reserved namespace – i.e., the key
    cannot begin with "pmix"

In addition to enforcing these restrictions, this RFC extends the
PMIx\_Get behavior to ensure that a request for information from a
process in another namespace will return the job-level info for that
namespace in addition to any info published by that process via
PMIx\_Put. This allows any subsequent request for job-level info to be
locally satisfied without an additional communication.

Protoype Implementation
-----------------------

The PMIx library implementation is covered in the [Simplify the
PMIx\_Get processing](https://github.com/pmix/master/pull/114) pull
request. The prototype has been tested against Open MPI and is currently
committed into the master repo of that project.

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

