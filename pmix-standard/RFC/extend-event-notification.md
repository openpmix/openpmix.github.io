---
layout: default
title: Extend Event Notification
---

RFC0018
=======

Title
-----

Extend the [Event Notification RFC](https://github.com/pmix/RFCs/pull/2)

Abstract
--------

As use of the event notification system grows, requests for some added
capabilities have begun to surface. These include the ability to notify
across threads in the same process, and the ability to direct ordering
of event notifications when registering event handlers. This RFC
addresses those needs without requiring any changes to the involved
APIs.

Labels
------

\[ATTRIBUTES\]\[BEHAVIOR\]

Action
------

\[APPROVED\]

Copyright Notice
----------------

Copyright (c) 2017 Intel, Inc. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

Several use-cases have identified desirable extensions to the behavior
of the event notification system, especially in the registration area.
These include:

-   Hybrid applications (i.e., applications that utilize more than one
    programming model, such as an MPI application that also uses OpenMP)
    are growing in popularity. As addressed by the relevant
    [RFC](https://github.com/pmix/RFCs/pull/17), this trend would
    benefit from cross-library coordination. Coordinating with a
    threading library such as OpenMP subsequently creates the need for
    separate event handlers for threads of the same process, thus
    requiring support for multiple threads to potentially register
    different event handlers against the same status code.

-   a need for the caller to define a desired callback sequence when
    registering event handlers. This is primarily driven by a desire to
    ensure that a particular event handler is called prior to a global
    default event handler that might take draconian action (e.g., abort
    the job)

-   a need for an event handler to indicate whether or not an "abort" is
    required at completion of the event processing chain. In many cases,
    the default event handler simply aborts the application. This is
    adequate in cases where a prior event handler can fully resolve the
    problem, and therefore safely terminate the event handler callback
    chain. However, in some cases an event handler may handle only
    enough of the problem to assure that an "abort" operation is not
    required, but needs to allow other event handlers an opportunity to
    further resolve issues. Since the subsequent handlers may have
    differing conclusions regarding termination, a method for reaching a
    consolidated result is required.

None of these require modification of existing PMIx APIs, nor addition
of new ones. Instead, all can be supported by adding attributes to
direct the behavior of the existing event registration/notification
functions.

#### Event registration extensions

There are three proposed changes to event registration.

##### Registering multiple event handlers against same codes

This change stipulates that the implementation must support multiple
event handlers being registered against the same status code(s). PMIx
has always had a requirement that a status code could be used in both a
single status event handler, and multiple multi-status event handlers.
However, we previously required that a single-status event registration
could only be done once using that status code, and that a given
combination of status codes could only be registered once as a
multi-status handler. This RFC removes those restrictions and requires
that an implementation support multiple single-status handlers
registered against a given code, and multiple handlers registered
against the same combination of codes. The precedence attributes
described below can be applied to direct ordering across these handlers.

Note that the current standard doesn’t explicitly state that any
*PMIX\_EVENT\_HDLR\_NAME* attribute given at registration be unique. The
RFC corrects that lack by making this an explicit requirement. The PMIx
implementation is required to return an error whenever this is violated,
regardless of any other attributes that may or may not be provided.
However, an event registration is not *required* to provide a handler
name – any non-named handlers cannot be subsequently cited when
requesting precedence.

##### Desired ordering

The current PMIx standard does not actually specify a default ordering
for event handlers as they are being registered. However, it does
include an inherent ordering for invocation. Specifically, PMIx
stipulates that handlers be called in the following categorical order:

-   single status event handlers – i.e., handlers that were registered
    against a single specific status.

-   multi status event handlers – those registered against more than one
    specific status

-   default event handlers – those registered against no specific status

The intent of this RFC is to add a capability to support arbitrary
ordering within these categories – i.e., one can direct that a single
status event handler come before another single status handler, but not
that a multi-event handler precede a single event handler. There are
only two allowed exceptions – a user may request that a specified event
handler be executed at the beginning or at the end of the chain,
regardless of category.

The primary need here is for attributes indicating desired ordering of
the event handler being registered vs other handlers that have already
been registered or will subsequently be registered. In both cases, it is
necessary that the user provide something to identify each handler so
the relative position can later be specified – this is to be done via
the existing PMIX\_EVENT\_HDLR\_NAME attribute. In addition, the RFC
retains the existing PMIX\_EVENT\_ORDER\_PREPEND attribute that directs
PMIx to prepend the handler being registered to the front of the chain
for that category of handler, but renames that attribute to
PMIX\_EVENT\_HDLR\_PREPEND for consistency.

Since no default ordering was previously specified, users could not be
certain of expected behavior when registering handlers. Thus, this RFC
removes the ambiguity by requiring implementations to default to
prepending event handlers within their respective categories.

Within these constraints, the following new attributes are proposed:

-   PMIX\_EVENT\_HDLR\_FIRST – invoke this event handler before any
    other handlers. Note that only one event handler can be given this
    directive – any subsequent registrations that contain this attribute
    will return an error, as will requests to "register before" this
    handler. As previously noted, this event handler can be of any
    category.

-   PMIX\_EVENT\_HDLR\_LAST – invoke this event handler after all other
    handlers have been called. Note that only one event handler can be
    given this directive – any subsequent registrations that contain
    this attribute will return an error, as will requests to "register
    after" this handler. As previously noted, this event handler can be
    of any category.

-   PMIX\_EVENT\_HDLR\_FIRST\_IN\_CATEGORY – invoke this event handler
    before any other handlers in this category. Note that only one event
    handler can be given this directive for each category – any
    subsequent registrations that contain this attribute will return an
    error, as will requests to "register before" this handler.

-   PMIX\_EVENT\_HDLR\_LAST\_IN\_CATEGORY – invoke this event handler
    after all other handlers in this category have been called. Note
    that only one event handler can be given this directive – any
    subsequent registrations in this category that contain this
    attribute will return an error, as will requests to "register after"
    this handler.

-   PMIX\_EVENT\_HDLR\_BEFORE – put this event handler immediately
    before the one specified in the (char\*) value. The named event
    handler must be in the same category (single, multi, or default) as
    the one being registered. An error will be returned if the named
    event handler is not found, or the categories do not match.

-   PMIX\_EVENT\_HDLR\_AFTER – put this event handler immediately after
    the one specified in the (char\*) value. The named event handler
    must be in the same category (single, multi, or default) as the one
    being registered. An error will be returned if the named event
    handler is not found, or the categories do not match.

-   PMIX\_EVENT\_HDLR\_APPEND – append the handler being registered to
    the end of the chain for that category of handler. If a handler has
    been specified to be the last in the category, then this handler
    will be placed directly in front of it.

##### Proc-Local data range

In addition to the above attributes, this RFC proposes a new data range
definition:

    #define PMIX_RANGE_PROC_LOCAL    7   // restrict range to the local proc

When given in a registration, the attribute indicates that the requestor
only wishes this event handler to receive events generated by itself
(e.g., by another thread within the same process).

#### Event notification extensions

Three changes are proposed to the event notification area.

##### Aggregation of event handler results

The current event notification standard requires that the implementation
simply append any results returned by an event handler to the array of
results passed in to subsequent handlers. It was left to each invoked
event handler to scan the array of prior results and determine what, if
any, action to take based on their content.

This RFC proposes to modify this behavior by allowing event handlers to
modify the incoming results array. Thus, the implementation will be
supplying a *consolidated* set of results to subsequent event handlers
in place of the current *aggregated* array.

Event handlers can modify the results array in two ways:

-   the value of a particular key can be altered

-   a particular key-value pair can be marked for removal by free’ing
    the key and setting it to NULL. This directs the implementation to
    remove that array element before invoking the next handler

Additions to the results array can be provided in the event handler’s
notification callback function. Any *pmix\_info\_t* structures provided
in that array will continue to be appended to the results array prior to
invoking the next handler. Note that the status returned by each event
handler will be appended to the results array just before addition of
any returned structures, as is currently done.

##### Receiver-level filtering of events

This change requires that the implementation apply any data range
directives given during event handler registration to the notification
prior to invoking the handler. Prior to this RFC, the delivery of an
event to a specific process was governed solely by the data range given
by the event generator. This RFC adds a second filter to the delivery
procedure by allowing the registration to also specify the range of
sources it will accept. Thus, even though an event generator may direct
that this event go to a target process, the individual handlers
registered by that process can specify which of them want to be invoked
to service an event from that source range. Registrations that do not
include a range directive will not be filtered.

##### New attributes

The following event attributes are added to support fault tolerance
behavior within the application:

-   PMIX\_EVENT\_NO\_TERMINATION – indicates that the handler has
    satisfactorily handled the event and believes termination of the
    application is not required. Any other operations are permitted.
    This attribute can be overwritten by subsequent handlers.

-   PMIX\_EVENT\_WANT\_TERMINATION – indicates that the handler has
    determined that the application should be terminated. Note that this
    can be overridden by subsequent event handlers *unless* the
    PMIX\_INFO\_REQD directive is set in the pmix\_info\_t struct
    containing this attribute.

Protoype Implementation
-----------------------

Prototype implementation available in PMIx master repo in [Pull Request
344](https://github.com/pmix/master/pull/344)

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

