---
layout: page
title: How Does PMIx Work with Containers?
---

The use of containers for high-performance computing and other purposes
has seen increasing popularity in recent years. A variety of container
technologies are now available, and researchers continue to investigate
best practices for creating, distributing, and using containerized
applications.

![Containers Fig](/images/containers.png 'Containers Fig')

One point of concern lies in the cross-boundary integration of the
containerized application to the hosting system management stack (SMS).
While a containerized application generally includes all of its
dependent libraries, there are operations that need to cross the
container’s boundary and interact with services outside the container.
For example, containers launched by a system-supplied starter such as
MPI’s *mpiexec* may need to exchange wireup information using daemons
running outside the container, as shown at right, or request additional
resources via the system-level PMIx server.

Use-cases such as these require compatibility between the
SMS-to-application communication libraries inside and outside the
container. Managing this requirement by matching library versions is
very difficult as it would require that containers continually update
their internal libraries – which somewhat defeats the point.

As PMIx has grown to support a wider range of application-SMS
interactions, it has become a natural place to define an alternative
solution to the cross-boundary compatibility problem. PMIx has addressed
this by utilizing a plugin-based architecture that allows both the
client and server to select from a range of supported protocol levels.
The resulting coordination is based on a client-driven handshake – i.e.,
the client selects the protocol to be used, and the server adapts to
support it. The client’s selection is based on a combination of
environmental parameters passed to it at launch by the server, filtered
against the protocols available to that particular client. For example,
a PMIx v1.2 client only has the “usock” messaging transport available to
it, and so would select that transport even when a PMIx v3 server
offered “usock” and “tcp” options. Note that if the PMIx v3 server had
not been instructed to support “usock”, then the v1.2 client would have
failed PMIx\_Init with an error indicating the server was unreachable.

Although the PMIx community is committed to supporting the cross-version
use-case, early releases did not fully provide the necessary
capabilities. Each release branch has since been updated to include the
required translation logic for communicating to other versions, but full
compatibility could not be provided due to the level of changes it would
introduce to what would otherwise be considered a “stable’ release
series. Thus, the following chart shows the available compatibility:

![Compatibility  Fig](/images/compatibility.png 'Compatibility Fig')

Starting with v2.1.1, all versions are fully cross-compatible – i.e.,
the client and server versions can be any combination of release level.
Thus, a v2.1.1 client can connect to a v3.0.0 server, and vice versa.

PMIx v1.2.5 servers can only serve v1.2.x clients, but v1.2.5 clients
can connect to v2.0.3, and v2.1.1 or higher servers. Similarly, v2.0.3
servers can only serve v2.0.x and v1.2.5 clients, but v2.0.3 clients can
connect to v2.1.1 or higher servers.

