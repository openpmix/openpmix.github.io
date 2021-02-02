---
layout: default
title: Avoiding duplication of HWLOC topology tree
---

HWLOC provides a wide range of information of use to many libraries and applications. However, that support comes at a cost, especially on many-core architectures where the hardware topology can be quite complex. In these circumstances, construction of the HWLOC topology tree:

- requires a fair amount of time as HWLOC must open/parse many system-level files. Further exacerbating the problem is that many operating systems thread-protect access to the system-level files, thus serializing the parsing procedure when multiple libraries or processes are attempting to construct topology trees at the same time (e.g., at process startup or library initialization)

- consumes a fair amount of memory. A single HWLOC topology tree on a complex many-core architecture may consume on the order of 512Kbytes. This seems small - until one realizes that this amount of memory will be consumed by _every_ topology tree. If an application has multiple libraries within it that are independently constructing topology trees, and you are running many processes on a node, memory consumed by topology trees can easily extend into the 10s of megabytes.

Unfortunately, there is no good way of detecting multiple HWLOC topology discovery operations in a process. The only method I've been able to come up with is to simply edit the HWLOC code and add a print statement at the beginning of the `hwloc_topology_load` function. I plan to talk to the HWLOC developers about adding a flag to generate that output as this is a somewhat global issue.

On the plus side, PMIx and HWLOC have combined forces to help alleviate this problem. Beginning with HWLOC 2.0, HWLOC offers support for a shared memory version of the topology tree. PMIx 3.0 introduced attribute keys by which this shared memory region can be exposed to users and/or libraries should the host environment (whether the RM or a launcher like "mpirun") create it. PMIx 4.0 and 4.1 further extended this support by providing simpler, more transparent ways for applications and libraries to gain access to the HWLOC shared memory region.

**Accessing the HWLOC topology tree from clients**

Once the HWLOC topology information has been provided to the PMIx library (either from the host or via its own
discovery), clients are provided with several rendezvous options.

Starting with PMIx v4.1, clients can directly obtain a pointer to the `hwloc_topology_t` by calling `PMIx_Get`
with the `PMIX_TOPOLOGY2` key. **This is the recommended way to obtain the HWLOC topology tree as it guarantees
use of the most optimal method for obtaining it**. This will return a `pmix_topology_t` structure that contains a `source` field
identifying the generator of the topology (for now, only HWLOC is supported) plus a `topology` field that contains
the `hwloc_topology_t` pointer. The PMIx library is responsible for obtaining the topology tree in the most efficient manner, according to the following priorities:
- shared memory region created by an external source (e.g., the PMIx server)
- XML string converted to local topology tree (avoids the discovery process)
- direct discovery

An example of the code for this method is shown below:

```c
pmix_value_t *val;
pmix_proc_t wildcard;
pmix_info_t info;
pmix_topology_t *ptopo;
hwloc_topology_t topo;

PMIX_LOAD_PROCID(&wildcard, myproc.nspace, PMIX_RANK_WILDCARD);
PMIX_INFO_LOAD(&info, PMIX_OPTIONAL, NULL, PMIX_BOOL);
rc = PMIx_Get(&wildcard, PMIX_TOPOLOGY2, &info, 1, &val);
if (PMIX_SUCCESS != rc) {
    /* topology isn't available */
}
ptopo = val->data.topo;
PMIX_VALUE_RELEASE(val);
if (0 != strcasecmp(ptopo->source, "hwloc")) {
    /* hwloc didn't create this */
}
topo = (hwloc_topology_t)ptopo->topology;
```

Clients using PMIx 3.x can obtain the rendezvous information for the HWLOC shared memory region
containing the topology using code such as this:

```c
pmix_value_t *val;
pmix_proc_t wildcard;
pmix_info_t info;
char *shmemfile;
size shmemaddress;
size_t shmemsize;
int fd;
hwloc_topology_t topo;

PMIX_LOAD_PROCID(&wildcard, myproc.nspace, PMIX_RANK_WILDCARD);
PMIX_INFO_LOAD(&info, PMIX_OPTIONAL, NULL, PMIX_BOOL);
rc = PMIx_Get(&wildcard, PMIX_HWLOC_SHMEM_FILE, &info, 1, &val);
if (PMIX_SUCCESS != rc) {
    /* shmem support not available */
}
shmemfile = strdup(val->data.string);
PMIX_VALUE_RELEASE(val);

rc = PMIx_Get(&wildcard, PMIX_HWLOC_SHMEM_ADDR, &info, 1, &val);
if (PMIX_SUCCESS != rc) {
    /* shmem support not available */
}
shmemaddress = val->data.size;
PMIX_VALUE_RELEASE(val);

rc = PMIx_Get(&wildcard, PMIX_HWLOC_SHMEM_SIZE, &info, 1, &val);
if (PMIX_SUCCESS != rc) {
    /* shmem support not available */
}
shmemsize = val->data.size;
PMIX_VALUE_RELEASE(val);

if (0 > (fd = open(shmemfile, O_RDONLY))) {
    /* can't connect */
}

if (0 != hwloc_shmem_topology_adopt(&topo, fd, 0, (void*)shmemaddress, shmemsize, 0)) {
    /* can't connect */
}
```

These methods, of course, require that the library or application build/link against a PMIx library. In some cases, particularly in lower-level libraries, adding a dependency on PMIx is something rather undesirable - developers of such libraries prefer to keep them "thin" with minimal dependencies and as small a memory footprint as possible. Beginning with PMIx v4.1, PMIx provides additional support for such cases by exposing the three HWLOC shmem "hooks" as environmental variables in addition to PMIx keys. Thus, an alternative to the previous code in such circumstances would look like the following:

```c
char *efile, *eaddr, *esize;
size_t addr, size;
int fd;
hwloc_topology_t topo;

efile = getenv("PMIX_HWLOC_SHMEM_FILE");
eaddr = getenv("PMIX_HWLOC_SHMEM_ADDR");
esize = getenv("PMIX_HWLOC_SHMEM_SIZE");

if (NULL == efile || NULL == eaddr || NULL == esize) {
    /* can't connect */
}

addr = strtoul(eaddr, NULL, 10);
size = strtoul(esize, NULL, 10);

if (0 > (fd = open(efile, O_RDONLY))) {
    /* can't connect */
}

if (0 != hwloc_shmem_topology_adopt(&topo, fd, 0, (void*)addr, size, 0)) {
    /* can't connect */
}
```

At the completion of any of these procedures, you can traverse/query the topology tree in "topo" using the usual HWLOC support functions. Note that any attempt to modify the topology tree (including adding data to the "userdata" field of an HWLOC object) will fail, and that you should not "destruct" the topology when done with it (a call to `hwloc_topology_destroy` will return an error).

For cases where shared memory topology support is not present (e.g., when using HWLOC versions prior to v2.0) or not desirable, PMIx servers provide XML representations of the topology via the PMIX_TOPOLOGY_XML attribute. Please check the PMIx Standard for details.

**Providing HWLOC topology tree to the PMIx server**

Host environments have several options for providing HWLOC topology support to their client applications.
The host can create the topology tree and pass it down to its embedded PMIx server with instructions to
share the topology with clients. This is done at time of calling `PMIx_server_init` by passing appropriate
attributes that includes the PMIX_SERVER_SHARE_TOPOLOGY (for v4.0 and above) or the
PMIX_HWLOC_SHARE_TOPO (for v3.x) directive.

If the host has instantiated the topology as a simple tree, then it can pass :

- starting in PMIx 4, the PMIX_TOPOLOGY2 attribute that contains a `pmix_topology_t` structure with
the `source` field set to "hwloc" and the `topology` field set to the `hwloc_topology_t` containing the
tree. The PMIx server shall convert the tree into a shared memory representation for sharing with its clients

- in PMIx 3, the PMIX_TOPOLOGY attribute that contains the `hwloc_topology_t` pointer

If the host has instantiated the tree in a shared memory region that it wishes to share with its clients, then it can
pass the file, address, and size information to the PMIx library for relay to those clients. In this case, the PMIx library
acts as a simple relay for the information.

Note that PMIx itself requires access to HWLOC information in order to provide several of its features. Thus, if
the host does not provide a topology to the PMIx library, the library itself will most likely create one for its own
use. Hosts that wish to access the PMIx version of the topology tree (e.g., if the host wants to take advantage
of the PMIx shared memory support) can obtain the required rendezvous information in the same manner as a
client - i.e., by appropriate use of PMIx_Get.
