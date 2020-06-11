---
layout: default
title: PMIx Groups
---

UNDER CONSTRUCTION
==================

Please note that the PMIx Groups concept is a subject of current RFC
development. Thus, the description on this page should be considered a
“draft” at this time and is provided to help stimulate discussion.

### PMIx Groups: An Overview

**PMIx Groups** are defined as a collection of processes desiring a
unified identifier for purposes such as passing events or participating
in PMIx fence operations. Groups differ from processes that
PMIx\_Connect with each other in the following key areas:

-   Relation to the host resource manager (RM)
    -   Calls to PMIx\_Connect are relayed to the host RM. This means
        that the RM should treat the failure of any process in the
        specified assemblage as a reportable event and take appropriate
        action. However, the RM does *not* define a new identifier for
        the connected assemblage, nor does it define a new rank for each
        process within that group. In addition, the PMIx server does not
        provide any tracking support for the assemblage. Thus, the
        caller is responsible for maintaining the membership list of the
        assemblage

    -   Calls to PMIx\_Group are first processed within the local PMIx
        server, which creates a tracker that associates the specified
        processes with the user-provided group identifier. Each process
        in the group is assigned a *group rank* based on their relative
        position in the array of processes provided in the call to
        Group\_construct. In addition, each member of the group is
        provided with the job-level information of any other nspace
        represented in the group, and the contact information for all
        group members. Members of the group can subsequently utilize the
        provided group identifier in PMIx function calls to address the
        group’s members, using either PMIX\_RANK\_WILDCARD to refer to
        all of them or the group-level rank of specific members. The
        PMIx server will translate the specified processes into their
        RM-assigned identifiers prior to passing the request up to its
        host. Thus, the RM has no visibility into the group’s existence
        or membership.

        ***Critical Note:*** User-provided group identifiers *must* be
        distinct from anything provided by the RM so as to avoid
        collisions between group identifiers and RM-assigned nspaces.
        This can best be accomplished through the use of an
        application-specific prefix – e.g., “myapp-foo”
-   Construction procedure
    -   PMIx\_Connect calls require that every process call the API
        before completing – i.e., it is modeled upon the bulk
        synchronous traditional MPI connect/accept methodology. Thus,
        the application developer must hard-code the creation of a new
        assemblage.
    -   PMIx Groups are designed to be more flexible in their
        construction procedure by also providing for dynamic definition
        of membership based on an invite/join model. A process can
        asynchronously construct a group of any processes via the
        PMIx\_Group\_invite function call. Invitations are delivered in
        a PMIx event (using the PMIX\_GROUP\_INVITED event) to the
        invited processes which can then accept or decline the
        invitation using the PMIx\_Group\_join API. Alternatively, users
        can construct groups via a collective operation using the
        PMIx\_Group\_construct API
-   Destruct procedure
    -   Processes that combine via PMIx\_Connect must all depart the
        group together – i.e., no member can depart the group while
        leaving the remaining members in it. Even the non-blocking form
        of “disconnect” retains this requirement in that members remain
        a part of the group until all members have called
        PMIx\_Disconnect\_nb
    -   Members of a PMIx Group may depart the group at any time via the
        PMIx\_Group\_leave API. Other members are notified via the
        PMIX\_GROUP\_LEFT event to distinguish such events from those
        reporting process termination. This leaves the remaining members
        free to continue group operations. The PMIx\_Group\_destruct
        operation offers a collective method akin to PMIx\_Disconnect
        for deconstructing the group.

Another way to think of it might be that members of PMIx Groups are
“loosely” coupled as opposed to “tightly” connected when constructed via
PMIx\_Connect. The APIs are explained below.

***Critical Note:*** The reliance on PMIx events in the PMIx Group
concept dictates that processes utilizing these APIs *must register* for
the corresponding events. Failure to do so will likely lead to
operational failures. Users are recommended to utilize the PMIX\_TIMEOUT
directive (or retain an internal timer) on calls to PMIx Group APIs
(especially the blocking form of those functions) as processes that have
not registered for required events will never respond.

#### PMIx\_Group\_construct

    PMIX_EXPORT pmix_status_t PMIx_Group_construct(const char id[],
                                                   const pmix_proc_t procs[], size_t nprocs,
                                                   const pmix_info_t info[], size_t ninfo);

    PMIX_EXPORT pmix_status_t PMIx_Group_construct_nb(const char id[],
                                                      const pmix_proc_t procs[], size_t nprocs,
                                                      const pmix_info_t info[], size_t ninfo,
                                                      pmix_op_cbfunc_t cbfunc, void *cbdata);

Construct a new group composed of the specified processes and identified
with the provided group identifier. Both blocking and non-blocking
versions are provided (the callback function for the non-blocking form
will be called once all specified processes have responded). The group
identifier is a user-defined, NULL-terminated character array of length
less than or equal to PMIX\_MAX\_NSLEN. Only characters accepted by
standard string comparison functions (e.g., strncmp) are supported.
Processes may engage in multiple simultaneous group construct operations
as desired so long as each is provided with a unique group ID. The info
array can be used to pass user-level directives regarding timeout
constraints and other options available from the PMIx server.

Some specific info keys relevant to this operation:

-   PMIX\_GROUP\_LEADER (bool): declare this process to be the *leader*
    of the construction procedure. If a process provides this attribute,
    then failure notification for any participating process will go only
    to that one process. If the leader fails, then a
    PMIX\_GROUP\_LEADER\_FAILED event will be delivered to all
    participants so they can optionally declare a new leader. In the
    absence of a declared leader, failure events go to all participants.
-   PMIX\_GROUP\_OPTIONAL (bool): participation is optional – do not
    return an error if any of the specified processes terminate without
    having joined. The default is *false*
-   PMIX\_GROUP\_NOTIFY\_TERMINATION (bool): notify remaining members
    when another member terminates without first leaving the group. The
    default is *false*. PMIx-based group collective operations will be
    adjusted appropriately regardless of this attribute
-   PMIX\_TIMEOUT (int): return an error if the group doesn’t assemble
    within the specified number of seconds. Targets the scenario where a
    process fails to call PMIx\_Group\_connect due to hanging

The construct leader (if PMIX\_GROUP\_LEADER is provided) or all
participants will receive events (if registered for the
PMIX\_GROUP\_INVITE\_FAILED event) whenever a process fails or
terminates prior to calling PMIx\_Group\_construct(\_nb) – the events
will contain the identifier of the process that failed to join plus any
other information that the resource manager provided. This provides an
opportunity for the leader to react to the event – e.g., to invite an
alternative member to the group or to decide to proceed with a smaller
group. The decision to proceed with a smaller group is communicated to
the PMIx library in the results array at the end of the event handler.
This allows PMIx to properly adjust accounting for procedure completion.
When construct is complete, the participating PMIx servers will be
alerted to any change in participants and each group member will (if
registered) receive a PMIX\_GROUP\_MEMBERSHIP\_UPDATE event updating the
group membership.

Processes in a group under construction are not allowed to leave the
group until group construction is complete. Upon completion of the
construct procedure, each group member will have access to the job-level
information of all nspaces represented in the group and the contact
information for every group member.

Failure of the leader at any time will cause a
PMIX\_GROUP\_LEADER\_FAILED event to be delivered to all participants so
they can optionally declare a new leader. A new leader is identified by
providing the PMIX\_GROUP\_LEADER attribute in the results array in the
return of the event handler. Only one process is allowed to return that
attribute, declaring itself as the new leader. Results of the leader
selection will be communicated to all participants via a
PMIX\_GROUP\_LEADER\_SELECTED event identifying the new leader. If no
leader was selected, then the status code provided in the event handler
will provide an error value so the participants can take appropriate
action.

Any participant that returns PMIX\_GROUP\_CONSTRUCT\_ABORT from the
leader failed event handler will cause the construct process to abort.
Those processes engaged in the blocking construct will return from the
call with the PMIX\_GROUP\_CONSTRUCT\_ABORT status. Non-blocking
partipants will have their callback function executed with that status.

***Implementation Note:*** The current PRI uses the host’s PMIx\_Fence
module function as the backend for this operation, thus avoiding
definition of another host-to-server entry point. However, the signature
of that function only involves passing of the proc array – thus,
implementors may have used the proc array itself as the “signature” for
identifying a given operation. If this was done, then multiple parallel
calls to construct groups of different names but involving the same
processes will conflict. Resolving the problem (either with a new entry
point or attribute identifying the operation name) requires
modifications to the PMIx server library’s host. This will be defined
prior to adoption of the RFC.

#### PMIx\_Group\_invite

    PMIX_EXPORT pmix_status_t PMIx_Group_invite(const char grp[],
                                                const pmix_proc_t procs[], size_t nprocs,
                                                const pmix_info_t info[], size_t ninfo);

    PMIX_EXPORT pmix_status_t PMIx_Group_invite_nb(const char grp[],
                                                   const pmix_proc_t procs[], size_t nprocs,
                                                   const pmix_info_t info[], size_t ninfo,
                                                   pmix_op_cbfunc_t cbfunc, void *cbdata)

Explicitly invite the specified processes to join a group. Each invited
process will be notified of the invitation via the PMIX\_GROUP\_INVITED
event. The processes being invited must register for the
PMIX\_GROUP\_INVITED event in order to be notified of the invitation.
The invitation event will include the identity of the inviting process
plus the name of the group. When ready to respond, each invited process
provides a response using the appropriate form of PMIx\_Group\_join.
This will notify the inviting process that the invitation was either
accepted (via the PMIX\_GROUP\_INVITE\_ACCEPTED event) or declined (via
the PMIX\_GROUP\_INVITE\_DECLINED event). The
PMIX\_GROUP\_INVITE\_ACCEPTED event is captured by the PMIx client
library of the inviting process – i.e., the application itself does not
need to register for this event. The library will track the number of
accepting processes and alert the inviting process (by returning from
the blocking form of PMIx\_Group\_invite or calling the callback
function of the non-blocking form) when group construction completes.

The inviting process should, however, register for the
PMIX\_GROUP\_INVITE\_DECLINED if the application allows invited
processes to decline the invitation. This provides an opportunity for
the application to either invite a replacement, declare “abort”, or
choose to remove the declining process from the final group. The
inviting process should also register to receive
PMIX\_GROUP\_INVITE\_FAILED events whenever a process fails or
terminates prior to responding to the invitation. Actions taken by the
inviting process in response to these events must be communicated at the
end of the event handler by returning the corresponding result so that
the PMIx library can adjust accordingly.

Upon accepting the invitation, all members of the new group will receive
access to the job-level information of each other’s nspaces and the
contact information of the other members.

Some specific info keys relevant to this operation:

-   PMIX\_TIMEOUT (int): return an error if the group doesn’t assemble
    within the specified number of seconds. Targets the scenario where a
    process fails to call PMIx\_Group\_connect due to hanging

The inviting process is automatically considered the *leader* of the
asynchronous group construction procedure and will receive all failure
or termination events for invited members prior to completion. The
inviting process is required to provide a
PMIX\_GROUP\_CONSTRUCT\_COMPLETE event once the group has been fully
assembled – this event will be distributed to all participants along
with the final group membership.

***Critical Note:*** Applications are not allowed to use the group in
any operations until after receiving the
PMIX\_GROUP\_CONSTRUCT\_COMPLETE event signifying completion of group
construction. This is required in order to ensure consistent knowledge
of group membership across all participants.

Failure of the leader at any time will cause a
PMIX\_GROUP\_LEADER\_FAILED event to be delivered to all participants so
they can optionally declare a new leader. A new leader is identified by
providing the PMIX\_GROUP\_LEADER attribute in the results array in the
return of the event handler. Only one process is allowed to return that
attribute, declaring itself as the new leader. Results of the leader
selection will be communicated to all participants via a
PMIX\_GROUP\_LEADER\_SELECTED event identifying the new leader. If no
leader was selected, then the status code provided in the event handler
will provide an error value so the participants can take appropriate
action.

Any participant that returns PMIX\_GROUP\_CONSTRUCT\_ABORT from the
PMIX\_GROUP\_LEADER\_FAILED event handler will cause all participants to
receive an event notifying them of that status. Similarly, the leader
may elect to abort the procedure by either returning
PMIX\_GROUP\_CONSTRUCT\_ABORT from the handler assigned to the
PMIX\_GROUP\_INVITE\_ACCEPTED or PMIX\_GROUP\_INVITE\_DECLINED codes, or
by generating an event for the abort code. Abort events will be sent to
all invited participants.

#### PMIx\_Group\_join

    /* define values associated with PMIx_Group_join
     * to indicate accept and decline - this is
     * done for readability of user code */
    typedef enum {
        PMIX_GROUP_DECLINE,
        PMIX_GROUP_ACCEPT
    } pmix_group_opt_t;

    PMIX_EXPORT pmix_status_t PMIx_Group_join(const char grp[],
                                              const pmix_proc_t *leader,
                                              pmix_group_opt_t opt,
                                              const pmix_info_t info[], size_t ninfo);

    PMIX_EXPORT pmix_status_t PMIx_Group_join_nb(const char grp[],
                                                 const pmix_proc_t *leader,
                                                 pmix_group_opt_t opt,
                                                 const pmix_info_t info[], size_t ninfo,
                                                 pmix_op_cbfunc_t cbfunc, void *cbdata);

Respond to an invitation to join a group that is being asynchronously
constructed. The process must have registered for the
PMIX\_GROUP\_INVITED event in order to be notified of the invitation.
When ready to respond, the process provides a response using the
appropriate form of PMIx\_Group\_join.

***Critical Note:*** Since the process is alerted to the invitation in a
PMIx event handler, the process *must not* use the blocking form of this
call unless it first “thread shifts” out of the handler and into its own
thread context. Likewise, while it is safe to call the non-blocking form
of the API from the event handler, the process must not block in the
handler while waiting for the callback function to be called.

Calling this function causes the group “leader” to be notified that the
process has either accepted or declined the request. The blocking form
of the API will return once the group has been completely constructed or
the group’s construction has failed (as described below) – likewise, the
callback function of the non-blocking form will be executed upon the
same conditions.

Some specific info keys relevant to this operation:

-   PMIX\_TIMEOUT (int): return an error if the group construct doesn’t
    complete within the specified number of seconds. Targets the
    scenario where a process fails to call PMIx\_Group\_join due to
    hanging

Failure of the leader at any time will cause a
PMIX\_GROUP\_LEADER\_FAILED event to be delivered to all participants so
they can optionally declare a new leader. A new leader is identified by
providing the PMIX\_GROUP\_LEADER attribute in the results array in the
return of the event handler. Only one process is allowed to return that
attribute, declaring itself as the new leader. Results of the leader
selection will be communicated to all participants via a
PMIX\_GROUP\_LEADER\_SELECTED event identifying the new leader. If no
leader was selected, then the status code provided in the event handler
will provide an error value so the participants can take appropriate
action.

Any participant that returns PMIX\_GROUP\_CONSTRUCT\_ABORT from the
leader failed event handler will cause all participants to receive an
event notifying them of that status. Similarly, the leader may elect to
abort the procedure by either returning PMIX\_GROUP\_CONSTRUCT\_ABORT
from the handler assigned to the PMIX\_GROUP\_INVITE\_ACCEPTED or
PMIX\_GROUP\_INVITE\_DECLINED codes, or by generating an event for the
abort code. Abort events will be sent to all invited participants.

#### PMIx\_Group\_leave

    PMIX_EXPORT pmix_status_t PMIx_Group_leave(const char grp[],
                                               const pmix_info_t info[], size_t ninfo);

    PMIX_EXPORT pmix_status_t PMIx_Group_leave_nb(const char grp[],
                                                  const pmix_info_t info[], size_t ninfo,
                                                  pmix_op_cbfunc_t cbfunc, void *cbdata);

Leave a PMIx Group. Calls to PMIx\_Group\_leave (or its non-blocking
form) will cause a PMIX\_GROUP\_LEFT event to be generated notifying all
members of the group of the caller’s departure. The function will return
(or the non-blocking function will execute the specified callback
function) once the event has been locally generated and is not
indicative of remote receipt. All PMIx-based collectives such as
PMIx\_Fence in action across the group will automatically be adjusted if
the collective was called with the PMIX\_GROUP\_FT\_COLLECTIVE attribute
(default is false) – otherwise, the standard error return behavior for
that collective will be executed.

***Critical Note:*** The PMIx\_Group\_leave API is intended solely for
asynchronous departures of individual processes from a group as it is
not a scalable operation – i.e., when a process determines it should no
longer be a part of a defined group, but the remainder of the group
retains a valid reason to continue in existence. Developers are advised
to use PMIx\_Group\_destruct (or its non-blocking form) for all other
scenarios as it represents a more scalable operation.

#### PMIx\_Group\_destruct

    PMIX_EXPORT pmix_status_t PMIx_Group_destruct(const char grp[],
                                                  const pmix_info_t info[], size_t ninfo);

    PMIX_EXPORT pmix_status_t PMIx_Group_destruct_nb(const char grp[],
                                                     const pmix_info_t info[], size_t ninfo,
                                                     pmix_op_cbfunc_t cbfunc, void *cbdata);

Destruct a group identified by the provided group identifier. Both
blocking and non-blocking versions are provided (the callback function
for the non-blocking form will be called once all members of the group
have called “destruct”). Processes may engage in multiple simultaneous
group destruct operations as desired so long as each involves a unique
group ID. The info array can be used to pass user-level directives
regarding timeout constraints and other options available from the PMIx
server.

Some specific info keys relevant to this operation:

-   PMIX\_TIMEOUT (int): return an error if the group doesn’t destruct
    within the specified number of seconds. Targets the scenario where a
    process fails to call PMIx\_Group\_destruct due to hanging

The destruct API will return an error if any group process fails or
terminates prior to calling PMIx\_Group\_destruct or its non-blocking
version unless the PMIX\_GROUP\_NOTIFY\_TERMINATION attribute was
provided (with a value of true) at time of group construction. If
notification was requested, then an event will be delivered for each
process that fails to call destruct and the destruct tracker updated to
account for the lack of participation. The PMIx\_Group\_destruct
operation will subsequently return PMIX\_SUCCESS when the remaining
processes have all called destruct – i.e., the event will serve in place
of return of an error.

***Implementation Note:*** The current PRI uses the host’s PMIx\_Fence
module function as the backend for this operation, thus avoiding
definition of another host-to-server entry point. However, the signature
of that function only involves passing of the proc array – thus,
implementors may have used the proc array itself as the “signature” for
identifying a given operation. If this was done, then multiple parallel
calls to destruct groups of different names but involving the same
processes will conflict. Resolving the problem (either with a new entry
point or attribute identifying the operation name) requires
modifications to the PMIx server library’s host.

