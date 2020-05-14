---
layout: default
title: Query Time Remaining in Allocation
---

RFC0013
=======

The RFC number will be provided upon submission.

Title
-----

Provide a mechanism by which an application can query the resource
manager to obtain the time remaining in its allocation.

Abstract
--------

Inspired by [libyogrt](https://github.com/LLNL/libyogrt), this proposes
a standard interface to enable an application to query the resource
manager for the remaining time in its allocation. Such information is
useful in order for an application to shut down gracefully before its
allocation ends.

Labels
------

\[EXTENSION\]

Action
------

\[APPROVED\]

Copyright Notice
----------------

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

Time-shared systems impose maximum run times when assigning jobs to
resource allocations. To shut down gracefully, e.g., to write a
checkpoint before termination, it is necessary for an application to
periodically query the resource manager for the time remaining in its
allocation. This is especially true on systems for which allocation
times may be shortened or lengthened from the original time limit. Many
resource managers provide APIs to dynamically obtain this information,
but each API is specific to the resource manager, for example:

-   SLURM – slurm\_get\_rem\_time()
-   MOAB – MCCJobGetRemainingTime()

This proposal defines a new PMIx key and semantics to provide a uniform
interface to obtain the time remaining in a job allocation. The
semantics defined here are inspired by experiences from the development
and use of "Your One Get Remaining Time Library"
[libyogrt](https://github.com/LLNL/libyogrt).

The following PMIx key is defined in pmix\_common.h:

    #define PMIX_TIME_REMAINING    "pmix.time.remaining"   // (uint32_t) get number of seconds remaining in allocation

This key can be used with the PMIx\_Query interface to obtain the number
of seconds remaining in the current job allocation. The following
example illustrates usage of this key:

    static uint32_t seconds_remaining;

    static void cbfunc(pmix_status_t status, pmix_info_t *info, size_t ninfo,
                       void *cbdata, pmix_release_cbfunc_t release_fn, void *release_cbdata)
    {
        volatile bool *waiting = (volatile bool*)cbdata;
        /* read time_remaining */
        seconds_remaining = info->value.data.uint32;

        if (NULL != release_fn) {
            release_fn(release_cbdata);
        }
        *waiting = false;
    }

    int main(int argc, char **argv)
    {
      volatile bool waiting;
      /* init us */
      pmix_proc_t myproc;

      if (PMIX_SUCCESS != (rc = PMIx_Init(&myproc))) {
          fprintf(stderr, "Client ns %s rank %d: PMIx_Init failed: %d\n", myproc.nspace, myproc.rank, rc);
          exit(0);
      }
      fprintf(stderr, "Client ns %s rank %d: Running\n", myproc.nspace, myproc.rank);

      /* just query with one rank, we will bcast result to others */
      if (myproc.rank == 0) {
        /* query time remaining */
        pmix_query_t *q;
        size_t nq = 1;
        PMIX_QUERY_CREATE(q, nq);
        PMIX_ARGV_APPEND(q[0].keys, PMIX_TIME_REMAINING);

        waiting = true;
        PMIx_Query_info_nb(q, nq, cbfunc, (void*)&waiting);
        while (waiting) {
          usleep(10);
        }

        /* seconds_remaining now has time left in allocation */
      }

      PMIx_Finalize(NULL, 0);
      return 0;
    }

Protoype Implementation
-----------------------

Available in PMIx master repo in [Pull Request
277](https://github.com/pmix/master/pull/277)

Author(s)
---------

Adam Moody  
Lawrence Livermore National Laboratory  
Github: adammoody

