---
layout: page
title: Register Cleanup of Files and Directories
---

RFC0027
=======

Extends:

-   [RFC0015: Job Control and Monitoring
    APIs](https://github.com/pmix/RFCs/blob/master/RFC0015.md)
    -   Adds attributes to register files and directories for cleanup
        upon client termination

Title
-----

Register Cleanup of Files and Directories

Abstract
--------

Application processes frequently need to create temporary files and
directories (e.g., for shared memory backing) that need to be cleaned up
upon termination. This RFC provides a mechanism by which the process can
register files or directories for post-termination cleanup by the PMIx
server.

Labels
------

\[ATTRIBUTES\]\[EXTENSION\]

Action
------

\[APPROVED\]

Copyright Notice
----------------

Copyright (c) 2017-2018 Intel, Inc. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

Application processes frequently need to create temporary files and
directories (e.g., for shared memory backing) that need to be cleaned up
upon termination. This RFC provides a mechanism by which the process can
register files or directories for post-termination cleanup by the PMIx
server.

Processes will register files/directories for post-termination removal
using the PMIx\_Job\_control\_nb interface via the following attributes:

    #define PMIX_REGISTER_CLEANUP           "pmix.reg.cleanup"      // (char*) comma-delimited list of files to
                                                                    //         be removed upon process termination
    #define PMIX_REGISTER_CLEANUP_DIR       "pmix.reg.cleanupdir"   // (char*) comma-delimited list of directories to
                                                                    //         be removed upon process termination
    #define PMIX_CLEANUP_IGNORE             "pmix.cleanup.ignore"   // (char*) comma-delimited list of files or
                                                                    //         directories that are not to be removed

All directives in a request will pertain to all registered cleanup
directories included in that request. Directives supported for this
request include:

    #define PMIX_CLEANUP_RECURSIVE          "pmix.cleanup.recurse"  // (bool) recursively traverse subdirectories under the
                                                                    //        specified one(s)
    #define PMIX_CLEANUP_LEAVE_TOPDIR       "pmix.cleanup.lvtop"    // (bool) when recursively cleaning subdirs, do not remove
                                                                    //        the top-level directory (the one given in the
                                                                    //        cleanup request)

Multiple requests can be issued by a given client and/or in a single
call to PMIx\_Job\_control\_nb – the PMIx server will aggregate them
upon receipt. Duplicate file requests will return an error if they
conflict regarding removal vs ignore, but will otherwise return success
(with the duplicate entry dropped). Any duplicate directory-targeted
requests will be de-duplicated by the server using the following
conflict resolution rules:

-   a directive to recursively traverse subdirectories will take
    precedence over any duplicate request that does not include that
    directive

-   a directive to leave the top-level directory will take precedence
    over any duplicate request that does not so specify

Note that the PMIx server is not responsible for checking overlap
between directory-targeted requests. Thus, a request involving a
directory that is underneath another directory involvced in a request
will be treated as non-duplicate.

The PMIx\_Job\_control\_nb API takes an array of pmix\_proc\_t
structures to identify the target processes to be impacted by the
requested control operation. Registering for cleanup shall be strictly a
*LOCAL* operation. Hence, any such requests shall not be relayed to the
local host RM for processing, but instead will be handled by the local
PMIx server itself.

Requests that specify the requesting process for the pmix\_proc\_t
argument shall refer solely to the requesting process itself. The PMIx
server shall implement such requests upon termination of that process.
Requests that include a given namespace with PMIX\_RANK\_WILDCARD shall
be executed upon termination of all local clients from that nspace.
Likewise, a request that provides a NULL for the pmix\_proc\_t argument
shall be executed upon termination of all local clients from the nspace
of the requestor.

Note that filenames and directories not including an absolute path are
considered ambiguous and will result in return of an error – this is
done to avoid confusion over location versus the working directory of
the PMIx server.

Requests to cleanup subdirectories will proceed by:

1.  remove all specified files – i.e., non-directories;

2.  traverse the directory tree under each specified target location,
    removing all files not specified as "to be ignored". Note that
    requests specifying a file as "to be removed" that is also specified
    (either as part of the same request, or in either an earlier or
    later request) as "to be ignored" is considered contradictory and
    will return an error for the contradicting request; and

3.  directories shall be removed if empty, starting from the deepest
    part of the directory tree and working upwards.

Files and/or directories that cannot be removed (e.g., due to a
permissions problem) will be silently ignored, and only files and/or
directories with matching effective uid and gid of the requesting client
process will be considered – thus, files owned by other users and groups
will be automatically ignored. Printed output indicating that this has
occurred may be available from the PMIx library implementation (e.g., in
the case of the PMIx Reference Implementation, upon setting PMIX\_DEBUG
to a value of at least 10 in the PMIx server’s local environment).

Example
-------

    #include <pmix.h>
    #include <pmix_common.h>

    typedef struct {
        pthread_mutex_t mutex;
        pthread_cond_t cond;
        volatile bool active;
        pmix_status_t status;
    } mylock_t;

    #define DEBUG_CONSTRUCT_LOCK(l)                     \
        do {                                            \
            pthread_mutex_init(&(l)->mutex, NULL);      \
            pthread_cond_init(&(l)->cond, NULL);        \
            (l)->active = true;                         \
            (l)->status = PMIX_SUCCESS;                 \
        } while(0)

    #define DEBUG_DESTRUCT_LOCK(l)              \
        do {                                    \
            pthread_mutex_destroy(&(l)->mutex); \
            pthread_cond_destroy(&(l)->cond);   \
        } while(0)

    #define DEBUG_WAIT_THREAD(lck)                                      \
        do {                                                            \
            pthread_mutex_lock(&(lck)->mutex);                          \
            while ((lck)->active) {                                     \
                pthread_cond_wait(&(lck)->cond, &(lck)->mutex);         \
            }                                                           \
            pthread_mutex_unlock(&(lck)->mutex);                        \
        } while(0)

    #define DEBUG_WAKEUP_THREAD(lck)                        \
        do {                                                \
            pthread_mutex_lock(&(lck)->mutex);              \
            (lck)->active = false;                          \
            pthread_cond_broadcast(&(lck)->cond);           \
            pthread_mutex_unlock(&(lck)->mutex);            \
        } while(0)

    static void cbfunc(pmix_status_t status,
                       pmix_info_t *info, size_t ninfo,
                       void *cbdata,
                       pmix_release_cbfunc_t release_fn,
                       void *release_cbdata)
    {
        mylock_t *lock = (mylock_t*)cbdata;

        lock->status = status;

        /* let the library release the data and cleanup from
         * the operation */
        if (NULL != release_fn) {
            release_fn(release_cbdata);
        }

        /* release the block */
        DEBUG_WAKEUP_THREAD(lock);
    }

    int main (int argc, char **argv)
    {
        pmix_proc_t myproc, proc;
        pmix_info_t *info;
        mylock_t lock;

        PMIx_Init(&myproc, NULL, 0);

        /* request to cleanup a process-specific tmp directory tree and a specific shmem backing file */
        PMIX_INFO_CREATE(info, 5);
        PMIX_INFO_LOAD(&info[0], PMIX_REGISTER_CLEANUP_DIR, "/mytmpdir", PMIX_STRING);
        PMIX_INFO_LOAD(&info[1], PMIX_REGISTER_CLEANUP, "/tmp/dev_shm/mybackfile", PMIX_STRING);
        /* recursively cleanup subdirectories */
        PMIX_INFO_LOAD(&info[2], PMIX_CLEANUP_RECURSIVE, NULL, PMIX_BOOL);
        /* ignore a file used for debugging output, if present */
        PMIX_INFO_LOAD(&info[3], PMIX_CLEANUP_IGNORE, "/mytmpdir/output-124.txt", PMIX_STRING);
        /* ignore a file containing contact info, if present */
        PMIX_INFO_LOAD(&info[4], PMIX_CLEANUP_IGNORE, "/mytmpdir/subdir/contact.info", PMIX_STRING);

        DEBUG_CONSTRUCT_LOCK(&lock);
        /* pass the request - note that this request will be serviced upon
         * my termination */
        rc = PMIx_Job_control_nb(&myproc, 1, info, 5, cbfunc, (void*)&lock);
        if (PMIX_SUCCESS != rc) {
            fprintf(stderr, "Job control failed\n");
            PMIX_INFO_FREE(info, 5);
            DEBUG_DESTRUCT_LOCK(&lock);
            goto done;
        }
        DEBUG_WAIT_THREAD(&lock);
        rc = lock.status;
        PMIX_INFO_FREE(info, 5);
        DEBUG_DESTRUCT_LOCK(&lock);

        /* now register to have my job-level tmp directory tree
         * cleaned up. Any overlapping requests by my peers will
         * be de-duplicated by the server so this cleanup occurs
         * only once when all local job clients have terminated */
        PMIX_INFO_CREATE(info, 2);
        PMIX_INFO_LOAD(&info[0], PMIX_REGISTER_CLEANUP_DIR, "/myjobtmpdir", PMIX_STRING);
        /* recursively cleanup subdirectories */
        PMIX_INFO_LOAD(&info[1], PMIX_CLEANUP_RECURSIVE, NULL, PMIX_BOOL);
        /* we want this to refer to the entire local job, not just us */
        PMIX_PROC_CONSTRUCT(&proc);
        (void)strncpy(proc.nspace, myproc.nspace, PMIX_MAX_NSLEN);
        proc.rank = PMIX_RANK_WILDCARD;
        rc = PMIx_Job_control_nb(&proc, 1, info, 2, cbfunc, (void*)&lock);
        if (PMIX_SUCCESS != rc) {
            fprintf(stderr, "Job control failed\n");
            PMIX_INFO_FREE(info, 2);
            DEBUG_DESTRUCT_LOCK(&lock);
            goto done;
        }
        DEBUG_WAIT_THREAD(&lock);
        rc = lock.status;
        PMIX_INFO_FREE(info, 2);
        DEBUG_DESTRUCT_LOCK(&lock);

        ...

      done:
        PMIx_Finalize(NULL, 0);
        return rc;
    }

Protoype Implementation
-----------------------

Prototype implementation available in PMIx master repo in Pull Request
[Add registration for cleanup
support](https://github.com/pmix/master/pull/608), and in Open MPI PR
[Update to PMIx v3.0 PR for cleanup
registration](https://github.com/open-mpi/ompi/pull/4606)

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

