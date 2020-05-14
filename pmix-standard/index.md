---
layout: page
title: PMIx Standard
---

![PMIx Logo Roles](/images/pmix-logo-roles.png 'PMIx Logo Roles')

Current PMIx Standard
---------------------

The following versions of the PMIx Standard document are available:

-   Version 2.0 (Sept. 2018)
    -   [Local website](/uploads/2018/09/pmix-standard.pdf)
    -   [Repository release](https://github.com/pmix/pmix-standard/releases/tag/v2.0)
-   Version 2.1 (Dec 2018)
    -   [Local website](/uploads/2018/12/pmix-standard-2.1.pdf)
    -   [Repository release](https://github.com/pmix/pmix-standard/releases/tag/v2.1)
-   Version 2.2 (Feb. 2019)
    -   [Local website](/uploads/2019/02/pmix-standard-2.2.pdf)
    -   [Repository release](https://github.com/pmix/pmix-standard/releases/tag/v2.2)
-   Version 3.0 (Dec 2018)
    -   [Local website](/uploads/2018/12/pmix-standard-3.0.pdf)
    -   [Repository release](https://github.com/pmix/pmix-standard/releases/tag/v3.0)
-   Version 3.1 (Feb 2019)
    -   [Local website](/uploads/2019/02/pmix-standard-3.1.pdf)
    -   [Repository release](https://github.com/pmix/pmix-standard/releases/tag/v3.1)
-   Version 4.0 (Draft – Release Date TBD)
    -   A current draft of the v4.0 Standard is provided
        [here](/uploads/2019/09/pmix-standard-4.0.pdf).
        Formal release date remains TBD but is expected to be no later
        than 1Q2020.

Prior *ad hoc* versions of the standard were embodied in the header
files of the corresponding releases of the PMIx Reference
Implementation. These definitions have been superseded by the formal
documents. Each version of the Standard includes information on all
prior versions (e.g., the Version 2.0 document contains the definitions
from Version 1) and clearly marks all additions/changes incorporated
since the last release. Note that the PMIx Community chose not to
release a Version 1 document due to the delay in getting the formal
Standard document completed.

PMIx Standards Process
----------------------

The PMIx developer community is currently in an early stage – thus, the
process for *extending* the standard is relatively lightweight compared
to more mature communities. In contrast, the process for *modifying* an
existing definition in the standard is intentionally made to be very,
very hard. This serves both to discourage any breaks in backward
compatibility, and to push proposers to scrutinize and scrub their
proposed extensions to ensure they have provided adequate flexibility
for future uses.

Given the dynamic, fast-moving nature of the community at this time, the
current process for *extending* the standard consists of the following
stages:

-   Create an RFC describing the feature plus any API or attribute
    additions
-   Create a prototype against the PMIx reference library’s *master*
    branch for review (do not commit)
-   Present the RFC/prototype at a weekly developer’s teleconference.
    This is done to give the community an opportunity to consider
    whether or not the proposed extension is acceptable in principal,
    and avoids unnecessary expenditure of effort on proposals that are
    “dead on arrival”
    -   If no objection is raised to the concept, then a comment is
        added to the RFC noting that it has “Concept Approval” and the
        corresponding GitHub label is set
    -   After two presentations without objection, a comment is added to
        the RFC marking it as “Provisionally Accepted”, the
        corresponding GitHub label is set, and the proposal is free to
        move to the next stage
    -   If there is an objection or modification request, the proposer
        will change the RFC/prototype and present again the next week.
        This resets the clock, therefore requiring an additional two
        meetings before moving ahead
-   Once the RFC/prototype has been Provisionally Accepted, the proposer
    is free to merge the prototype into the PMIx reference library’s
    *master* branch. The RFC itself is held “open” in the Provisionally
    Accepted state
-   As the community works with the new code, proposed modifications to
    the RFC may be identified. When this occurs, a new commit is made to
    the RFC with a link to the PR with the proposed prototype
    modifications. Discussion resumes to determine when the prototype
    modifications should be merged into the PMIx reference library’s
    master branch
-   At release time, all Provisionally Accepted RFCs will be
    “finalized”. At this time, the proposer will close the PR and make
    sure the necessary changes have been made to the PMIx standard
    document.

Note that the above process relies heavily on the level of collaboration
in the current PMIx community. No formal voting process is involved, nor
are there “membership” requirements that must be met before someone has
a voice in the process. This is likely to change as the community grows
and matures. However, the expectation is that the standard will also
have matured by that time, and so a slower, more formal process may be
more appropriate.

The process for modifying an existing definition in the standard
utilizes the same first three steps of the extension process. However,
the initial presentation of the RFC/prototype must include:

-   a detailed justification for the change; and
-   an assessment of the impact of the change on the installed community

The amount of information provided should reflect the magnitude of the
proposed change. For example, a minor modification in behavior
associated with an existing attribute would require less explanation
than a change to an existing API. In many cases, proposals to modify
definitions are changed to attribute extensions (i.e., the adding of new
attribute definitions). This reflects the PMIx standard’s philosophy of
adding sufficient flexibility (via an array of pmix\_info\_t directives)
to each API to accommodate future additional or modified behaviors
without perturbing the API itself.

Should the justification prove sufficiently convincing, a Notice of
Impending Change (containing a summary of the proposed change and the
justification) is sent out to the community’s mailing list alerting them
to the proposed modification, and inviting comments. This provides an
opportunity for users and implementors to voice their concerns and
suggest modifications or alternative solutions. Three notices must be
sent prior to a final review of the proposal.

Assuming no objections are raised, a final review of the proposal – and
its justification – is conducted during a developer’s weekly telecon.
The proposal can be accepted, rejected, or pushed back for modification
at that time. If accepted, the change is made to the standard’s document
– this will include both a description of the change, and the
justification for it.

### What is Standardized, and What is *Not* Standardized

No standards body can *require* an implementor to support something in
their standard, and PMIx is no different in that regard. While an
implementor of the PMIx library itself must at least include the
standard PMIx headers and instantiate each function, they are free to
return “not supported” for any function they choose not to implement.

This also applies to the host environments. Resource managers and other
system management stack components retain the right to decide on support
of a particular function. The PMIx community continues to look at ways
to assist SMS implementors in their decisions by highlighting functions
that are critical to basic application execution (e.g., PMIx\_Get),
while leaving flexibility for tailoring a vendor’s software for their
target market segment.

One area where this can become more complicated is regarding the
attributes that provide information to the client process and/or control
the behavior of a PMIx standard API. For example, the PMIX\_TIMEOUT
attribute can be used to specify the time (in seconds) before the
requested operation should time out. The intent of this attribute is to
allow the client to avoid “hanging” in a request that takes longer than
the client wishes to wait, or may never return (e.g., a PMIx\_Fence that
a blocked participant never enters).

If an application (for example) truly relies on the PMIX\_TIMEOUT
attribute in a call to PMIx\_Fence, it should set the **required** flag
in the pmix\_info\_t for that attribute. This informs the library and
its SMS host that it must return an immediate error if this attribute is
not supported. By not setting the flag, the library and SMS host are
allowed to treat the attribute as **optional**, ignoring it if support
is not available.

It is therefore critical that users and application implementors:

-   consider whether or not a given attribute is required, marking it
    accordingly; and
-   check the return status on *all* PMIx function calls to ensure
    support was present and that the request was accepted. Note that for
    non-blocking APIs, a return of PMIX\_SUCCESS only indicates that the
    request had no obvious errors and is being processed – the eventual
    callback will return the status of the requested operation itself.

While a PMIx library implementor, or an SMS component server, may choose
to support a particular PMIx API, they are not *required* to support
every attribute that might apply to it. This would pose a significant
barrier to entry for an implementor as there can be a broad range of
applicable attributes to a given API, at least some of which may rarely
be used. The PMIx community is attempting to help differentiate the
attributes by indicating those that are generally used (and therefore,
of higher importance to support) vs those that a “complete
implementation” would support.

Note that an environment that does not include support for a particular
attribute/API pair is not “incomplete” or of lower quality than one that
does include that support. Vendors must decide where to invest their
time based on the needs of their target markets, and it is perfectly
reasonable for them to perform cost/benefit decisions when considering
what functions and attributes to support.

The flip side of that statement is also true: Users who find that their
current vendor does not support a function or attribute they require may
raise that concern to their vendor and request that the implementation
be expanded. Alternatively, users may wish to utilize the PMIx Reference
Server as a “shim” between their application and the host environment as
it might provide the desired support until the vendor can respond.
Finally, in the extreme, one can exploit the portability of PMIx-based
application to change vendors.

PMIx Roadmap
------------

The PMIx Standard is evolving fairly rapidly in response to milestones
associated with delivery of next-generation supercomputers. Accordingly,
the timeline is focused towards completing a broad array of features by
the end of 2019. The standard is currently defined in 3-4 header files
in each release, as shown below.

#### PMIx v1

The initial version of the standard, released in late 2015, covers the
basic functions required to launch and wireup a parallel application.
This includes the following APIs:

-   Client APIs
    -   PMIx\_Init, PMIx\_Initialized, PMIx\_Abort, PMIx\_Finalize
    -   PMIx\_Put, PMIx\_Commit, PMIx\_Fence, PMIx\_Get
    -   PMIx\_Publish, PMIx\_Lookup, PMIx\_Unpublish
    -   PMIx\_Spawn, PMIx\_Connect, PMIx\_Disconnect
    -   PMIx\_Resolve\_nodes, PMIx\_Resolve\_peers
-   Server APIs
    -   PMIx\_server\_init, PMIx\_server\_finalize
    -   PMIx\_generate\_regex, PMIx\_generate\_ppn
    -   PMIx\_server\_register\_nspace, PMIx\_server\_deregister\_nspace
    -   PMIx\_server\_register\_client, PMIx\_server\_deregister\_client
    -   PMIx\_server\_setup\_fork, PMIx\_server\_dmodex\_request
-   Common APIs
    -   PMIx\_Get\_version, PMIx\_Store\_internal, PMIx\_Error\_string
    -   PMIx\_Register\_errhandler, PMIx\_Deregister\_errhandler,
        PMIx\_Notify\_error

Note that the last set of APIs (focused on error handlers) was
subsequently replaced in v2 with a more generalized ability to handle
events. In addition, there was a modification made to PMIx\_Init and
PMIx\_Finalize in v2 to extend their flexibility and bring them into
alignment with the PMIx standard practice of including attribute arrays
to support future modifications of behavior.

#### PMIx v2

The second version of the standard, released in mid 2017, extended the
v1 release by adding support for workflow orchestration and tools.

-   Client APIs
    -   PMIx\_Query\_info\_nb, PMIx\_Log\_nb
    -   PMIx\_Allocation\_request\_nb, PMIx\_Job\_control\_nb,
        PMIx\_Process\_monitor\_nb
-   Server APIs
    -   PMIx\_server\_setup\_application,
        PMIx\_server\_setup\_local\_support
-   Tool APIs
    -   PMIx\_tool\_init, PMIx\_tool\_finalize
-   Common APIs
    -   PMIx\_Register\_event\_handler,
        PMIx\_Deregister\_event\_handler, PMIx\_Notify\_event
    -   PMIx\_Proc\_state\_string, PMIx\_Scope\_string,
        PMIx\_Persistence\_string
    -   PMIx\_Data\_range\_string, PMIx\_Info\_directives\_string,
        PMIx\_Data\_type\_string
    -   PMIx\_Alloc\_directive\_string
    -   PMIx\_Data\_pack, PMIx\_Data\_unpack, PMIx\_Data\_copy,
        PMIx\_Data\_print, PMIx\_Data\_copy\_payload

Descriptions of these APIs are provided in the v2 RFCs shown below.

#### PMIx v3

The third version of the standard, released in July 2018, focused on
completion of “instant on” support, further support for tools and
debuggers, and extension to support fabric and storage manager
integration.

-   Client APIs
    -   PMIx\_Log
    -   PMIx\_Get\_credential, PMIx\_Validate\_credential
    -   PMIx\_IOF\_pull, PMIx\_IOF\_deregister, PMIx\_IOF\_push
    -   PMIx\_Allocation\_request, PMIx\_Job\_control,
        PMIx\_Process\_monitor
-   Server APIs
    -   PMIx\_server\_IOF\_deliver
    -   PMIx\_server\_collect\_inventory,
        PMIx\_server\_deliver\_inventory
-   Tool APIs
    -   PMIx\_tool\_connect\_to\_server
-   Common APIs
    -   PMIx\_IOF\_channel\_string

#### PMIx v4

The fourth version of the standard is currently under development. The
full set of new APIs has not yet been defined, but the standard is
expected to be extended to provide schedulers with access to
point-to-point communication cost information along with providing
general access to network topology graphs, completion of debugger tool
support, the initial support for storage requests, and support for the
new PMIx Groups concept (in collaboration with the MPI Sessions Working
Group). In addition, Python bindings for the PMIx APIs will be
introduced in this release.

Development of the Standard can be followed in the v4 RFCs, as listed
below.

Roles and Responsibilities
--------------------------

Provides guidance on the expectations PMIx places on various cluster
subsystems, including required as well as desired levels of support.

-   [Fabric Manager](/pmix-standard/fabric-manager-roles-and-expectations)
-   [Input/Output Forwarding for Tools](/pmix-standard/input-output-forwarding-for-tools)
-   [Tiered Storage Support](/pmix-standard/tiered-storage-support)
-   [Logging with PMIx](/pmix-standard/logging-with-pmix)
-   [PMIx Groups](/pmix-standard/pmix-groups)

PMIx RFCs
---------

-   v2 RFCs
    -   [Basic Tool Interaction Mechanism](/pmix-standard/RFC/basic-tool-interaction-mechanism)
    -   [Event Notification](/pmix-standard/RFC/event-notification)
    -   [Modification of PMIx\_Connect/Disconnect](/pmix-standard/RFC/modification-of-pmix_connect-disconnect)
    -   [Flexible Allocation Support](/pmix-standard/RFC/flexible-allocation-support)
    -   [Modify Behavior of PMIx\_Get](/pmix-standard/RFC/modify-behavior-of-pmix_get)
    -   [Extended Tool Interaction Support](/pmix-standard/RFC/extended-tool-interaction-support)
    -   [Refactor Security Support](/pmix-standard/RFC/refactor-security-support)
    -   [Support for Network Interactions](/pmix-standard/RFC/support-for-network-interactions)
    -   [Query Time Remaining in Allocation](/pmix-standard/RFC/query-time-remaining-in-allocation)
    -   [Job Control and Monitoring](/pmix-standard/RFC/job-control-and-monitoring)
    -   [Extend Event Notification](/pmix-standard/RFC/extend-event-notification)
    -   [Expose PMIx Buffer Manipulation Functions](/pmix-standard/RFC/expose-pmix-buffer-manipulation-functions)
    -   [Acquisition of Subsystem Launch Information](/pmix-standard/RFC/acquisition-of-subsystem-launch-information)
-   v3 RFCs
    -   [Security Credential Transactions](/pmix-standard/RFC/security-credential-transactions)
    -   [Register Cleanup of Files and Directories](/pmix-standard/RFC/register-cleanup-of-files-and-directories)
    -   [IO Forwarding for Tools and Debuggers (provisionally accepted)](/pmix-standard/RFC/io-forwarding-for-tools-and-debuggers)
    -   [Environmental Parameter Directives for Applications and Launchers](/pmix-standard/RFC/envar-directives-for-applications-and-launchers)
    -   [Coordination Across Programming Models (OpenMP/MPI)](/pmix-standard/RFC/coordination-across-programming-models-openmp-mpi)
    -   [Modify the PMIx buffer manipulation APIs](/pmix-standard/RFC/modify-the-pmix-buffer-manipulation-apis)
    -   [Extended Debugger Support (in progress)](/pmix-standard/RFC/extended-debugger-support)
    -   [DataStore Abstraction Framework (in progress)](/pmix-standard/RFC/datastore-abstraction-framework)
    -   [Extension of PMIx Logging Support](/pmix-standard/RFC/extension-of-pmix-logging-support)
-   v4 RFCs
    -   [PMIx Support for Storage Systems (in progress)](/pmix-standard/RFC/pmix-support-for-storage-systems)
    -   [Support for Launching Applications under Debugger Tools (in progress)](/pmix-standard/RFC/support-for-launching-applications-under-debugger-tools)
    -   [PMIx Groups (in progress)](/pmix-standard/RFC/pmix-groups-2)

PMIx Presentations
------------------

-   Debuggers, Tools, and Next-Gen Fabric
    [PDF](/uploads/2018/11/PMIxF2F.pdf)
    [PPX](https://www.slideshare.net/rcastain/pmix-debuggers-and-fabric-support)
-   SC18 BoF [PDF](/uploads/2018/11/PMIx-BoF-2018.pdf)
    [PPX](https://www.slideshare.net/rcastain/sc18-bof-presentation)

