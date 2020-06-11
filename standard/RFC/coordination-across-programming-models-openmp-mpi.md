---
layout: default
title: Coordination Across Programming Models (OpenMP/MPI)
---

RFC0017
=======

Summary of RFC impacts:

-   imposes new requirements on implementations each time PMIx\_Init is
    called

-   always inspect any provided info array to see if model-related
    directives have been provided

-   generate the corresponding event should those model-related
    directives be present

-   conflicting directives (i.e., duplicate keys that contain different
    values) shall result in return of an error. Duplicate keys that
    contain the same value shall be ignored.

-   adds several new attributes and status codes

Title
-----

Coordination Across Programming Models (OpenMP/MPI)

Abstract
--------

Hybrid applications (i.e., applications that utilize more than one
programming model, such as an MPI application that also uses OpenMP) are
growing in popularity, especially as chips with increasingly large
numbers of cores and processors proliferate. This RFC offers a potential
solution to the problem by providing a pathway for programming models to
coordinate their actions.

Labels
------

\[EXTENSION\]

Action
------

\[ACCEPTED\]

Copyright Notice
----------------

Copyright 2017-2018 Intel, Inc. All rights reserved

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

Hybrid applications (i.e., applications that utilize more than one
programming model, such as an MPI application that also uses OpenMP) are
growing in popularity, especially as chips with increasingly large
numbers of cores and processors proliferate. Unfortunately, the various
models currently operate under the assumption that they alone control
execution. This leads to conflicts in hybrid applications – for example,
when each model attempts to independently bind a thread to a different
location.

This RFC offers a potential solution to the problem by providing a
pathway for programming models to coordinate their actions. As defined
by the PMIx OpenMP/MPI working group, the general objectives of this
effort are to:

-   provide a mechanism by which each library can determine that the
    other library is in operation. It was noted that OpenMP is looking
    for envars to indicate that MPI is active, but this isn’t terribly
    reliable as MPI envars change over time and with releases. Also, the
    fact that an envar is present doesn’t mean that MPI\_Init was called
    since RMs routinely set envars "just in case" the application needs
    them.

-   allow libraries to share knowledge of each other’s resources and
    intended resource utilization. For example, OMP would benefit from
    knowing if the MPI layer is using pthreads. Likewise, the MPI layer
    might be able to take advantage of the OMP worker thread pool if it
    knew it existed

-   give users the ability to experiment as the community really doesn’t
    know the "best practices" for hybrid applications at this point. We
    shouldn’t design interfaces that are rigid to current practices as
    these may not prove to be the best long-term.

This approach requires, of course, that each programming model call
PMIx\_Init in order to access the PMIx support functions. For the
purposes of the remainder of the discussion in this RFC, it is assumed
that each programming model will in fact call PMIx\_Init to ensure that
the PMIx support is available. Multiple calls to PMIx\_Init from within
a single process, including calls from multiple threads, is supported by
the PMIx standard and its convenience library – with the only
requirement being that the same number of calls be made to
PMIx\_Finalize prior to termination.

#### Identifying Active Programming Models

Informing each programming model that another model is actively in use
is a little problematic as there is no "standard" method by which
programming models initiate themselves. For example, MPI has the
standard "MPI\_Init" function that must be called to initialize the
library – providing a "hook" within that function to notify others that
it has been called. However, OpenMP does not have an explicit call to
"init" and is instead initialized on first use. The use of envars has
similar problems, as explained above, and has therefore been rejected as
a potential solution.

Likewise, requiring users to declare their intended programming models
prior to execution seemed overly burdensome and unlikely to meet general
user acceptance. Indeed, in cases of users executing packaged
applications (i.e., applications they did not write themselves),
explicit knowledge of the programming models employed by the application
may not be available to the user. Thus, a dynamic way of determining the
active programming models would be desirable.

Given that the ordering of calls to PMIx\_Init between the models is
unknowable and the difference in initialization methods, the
identification method must allow for some form of asynchronous
notification that a programming model has declared itself to be active.
We cannot rely on "knowing" that information when a model’s library
initializes itself. Thus, the following extension is proposed for
attributes passed to PMIx\_Init:

    /* identification attributes */
    #define PMIX_PROGRAMMING_MODEL              "pmix.pgm.model"        // (char*) programming model being initialized (e.g., "MPI" or "OpenMP")
    #define PMIX_MODEL_LIBRARY_NAME             "pmix.mdl.name"         // (char*) programming model implementation ID (e.g., "OpenMPI" or "MPICH")
    #define PMIX_MODEL_LIBRARY_VERSION          "pmix.mdl.vrs"          // (char*) programming model version string (e.g., "2.1.1")
    #define PMIX_THREADING_MODEL                "pmix.threads"          // (char*) threading model used (e.g., "pthreads")

In addition, models shall register for a PMIx event that will notify
them of initializations by other programming models. Note that PMIx
events are cached, and so registrations that are performed after another
model has already initialized will still trigger notification. The
registration will utilize a new status code specifically defined for
this purpose:

    /* status codes */
    #define PMIX_MODEL_DECLARED      (PMIX_ERR_OP_BASE - 17)

Therefore, an example of the use of this code within a programming model
might look like the following:

    #include <pmix.h>

    /* this is an event notification function that we explicitly request
     * be called when the PMIX_MODEL_DECLARED notification is issued.
     * We could catch it in the general event notification function and test
     * the status to see if it was PMIX_MODEL_DECLARED, but it often is simpler
     * to declare a use-specific notification callback point. In this case,
     * we are asking to know when another programming model declared itself */
    static void release_fn(size_t evhdlr_registration_id,
                           pmix_status_t status,
                           const pmix_proc_t *source,
                           pmix_info_t info[], size_t ninfo,
                           pmix_info_t results[], size_t nresults,
                           pmix_event_notification_cbfunc_fn_t cbfunc,
                           void *cbdata)
    {
        /* tell the event handler state machine that we are the last step */
        if (NULL != cbfunc) {
            cbfunc(PMIX_EVENT_ACTION_COMPLETE, NULL, 0, NULL, NULL, cbdata);
        }
        /* do whatever we want/need to do to coordinate */
    }

    /* event handler registration is done asynchronously because it
     * may involve the PMIx server registering with the host RM for
     * external events. So we provide a callback function that returns
     * the status of the request (success or an error), plus a numerical index
     * to the registered event. The index is used later on to deregister
     * an event handler - if we don't explicitly deregister it, then the
     * PMIx server will do so when it see us exit */
    static void evhandler_reg_callbk(pmix_status_t status,
                                     size_t evhandler_ref,
                                     void *cbdata)
    {
        volatile int *active = (volatile int*)cbdata;

        if (PMIX_SUCCESS != status) {
            fprintf(stderr, "EVENT HANDLER REGISTRATION FAILED WITH STATUS %d, ref=%lu\n",
                    status, (unsigned long)evhandler_ref);
        }
        *active = status;
    }

    int main(int argc, char **argv)
    {
        pmix_proc_t myproc;
        pmix_status_t rc;
        pmix_info_t *info;
        char *mymodel = "MPI";
        char *mymodelname = "FooMPI";
        char *myversion = "1.0.0";
        volatile int active;
        pmix_status_t code = PMIX_MODEL_DECLARED;

        /* setup to declare our programming model */
        PMIX_INFO_CREATE(info, 4);
        PMIX_INFO_LOAD(&info[0], PMIX_PROGRAMMING_MODEL, mymodel, PMIX_STRING);
        PMIX_INFO_LOAD(&info[1], PMIX_MODEL_LIBRARY_NAME, mymodelname, PMIX_STRING);
        PMIX_INFO_LOAD(&info[2], PMIX_MODEL_LIBRARY_VERSION, myversion, PMIX_STRING);
        PMIX_INFO_LOAD(&info[3], PMIX_THREADING_MODEL, "pthread", PMIX_STRING);

        /* initialize us */
        if (PMIX_SUCCESS != (rc = PMIx_Init(&myproc, info, 4))) {
            fprintf(stderr, "Client ns %s rank %d: PMIx_Init failed: %d\n", myproc.nspace, myproc.rank, rc);
            exit(0);
        }
        PMIX_INFO_FREE(info, 4);
        fprintf(stderr, "Client ns %s rank %d: Running\n", myproc.nspace, myproc.rank);

        /* register a handler specifically for notifying us if
         * other programming models declare themselves */
        active = -1;
        PMIx_Register_event_handler(&code, 1, NULL, 0,
                                    release_fn, evhandler_reg_callbk, (void*)&active);
        while (-1 == active) {
            usleep(10);
        }
        if (0 != active) {
            exit(active);
        }

        /* do whatever else */
    }

Since the PMIx library is shared within the process, it will therefore
be common to both programming libraries. Thus, the calls into PMIx\_Init
by each programming model will enter the same code space. PMIx
implementations are required to support such use-cases, but generally do
so strictly via reference count – i.e., after the first call to
PMIx\_Init, the arguments to subsequent calls are no longer examined.
Therefore, this RFC includes a new requirement on PMIx implementations
that they:

-   always inspect any provided info array during PMIx\_Init to see if
    model-related directives have been provided, and
-   generate the corresponding event should those model-related
    directives be present

This does raise an issue, however, that was not addressed in prior PMIx
architecture discussions regarding multiple calls to PMIx\_Init. Since
the question of what to do with arguments to subsequent calls was
ignored, the decision of how to resolve conflicting and/or overlapping
directives between calls was left open to the implementation. Although
there is no ambiguity in the treatment of the specific directives
contained in this RFC, the fact that PMIx\_Init now requires that the
arguments always be inspected raises the question of dealing with the
broader issue.

There is no way by which a PMIx implementation can "guess" the choice
between conflicting requests. Accordingly, this RFC imposes a new
requirement on PMIx implementations that:

-   directives passed to each invocation of PMIx\_Init must be cached.
    Subsequent calls to PMIx\_Init must check for conflicting directives
    (i.e., duplicate keys that contain different values) – these shall
    result in return of an error. Duplicate keys that contain the same
    value shall be ignored.

Note also that a registered PMIx event handler will be called from
within the PMIx progress thread – and *not* the thread context that
originally registered for it.

#### Dynamic Changes

Programming models can change their characteristics and/or resource
requirements on-the-fly. Alerting other active models will be supported
via the PMIx event notification system. Appropriate codes that can be
used to register for such events will expand over time, but this RFC
provides an initial set of codes and attributes for this purpose:

    /* status codes */
    #define PMIX_MODEL_RESOURCES                (PMIX_ERR_OP_BASE - 21)     // model resource usage has changed
    #define PMIX_OPENMP_PARALLEL_ENTERED        (PMIX_ERR_OP_BASE - 22)     // an OpenMP parallel region has been entered
    #define PMIX_OPENMP_PARALLEL_EXITED         (PMIX_ERR_OP_BASE - 23)     // an OpenMP parallel region has completed

    /* model attributes */
    #define PMIX_MODEL_NUM_THREADS              "pmix.mdl.nthrds"           // (uint64_t) number of active threads being used by the model
    #define PMIX_MODEL_NUM_CPUS                 "pmix.mdl.ncpu"             // (uint64_t) number of cpus being used by the model
    #define PMIX_MODEL_CPU_TYPE                 "pmix.mdl.cputype"          // (char*) granularity - "hwthread", "core", etc.
    #define PMIX_MODEL_PHASE_NAME               "pmix.mdl.phase"            // (char*) user-assigned name for a phase in the application
                                                                            //         execution - e.g., "cfd reduction"
    #define PMIX_MODEL_PHASE_TYPE               "pmix.mdl.ptype"            // (char*) type of phase being executed - e.g., "matrix multiply"
    #define PMIX_MODEL_AFFINITY_POLICY          "pmix.mdl.tap"              // (char*) thread affinity policy - e.g.:
                                                                            //           "master" (thread co-located with master thread),
                                                                            //           "close" (thread located on cpu close to master thread)
                                                                            //           "spread" (threads load-balanced across available cpus)

Events generated this way can be captured by registering for the
relevant codes. Note that debuggers and other tools can also use this
information if/when it is provided.

Protoype Implementation
-----------------------

Related prototype code resides in several pull requests against both the
PMIx and Open MPI master repositories. These include:

-   [Event Notification Extension](https://github.com/pmix/RFCs/pull/18)
-   [OpenMP/MPI Coordination](https://github.com/pmix/pmix/pull/450)

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

