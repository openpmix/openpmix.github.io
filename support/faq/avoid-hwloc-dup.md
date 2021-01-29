---
layout: default
title: Avoiding duplication of HWLOC topology tree
---

HWLOC provides a wide range of information of use to many libraries and applications. However, that support comes at a cost, especially on many-core architectures where the hardware topology can be quite complex. In these circumstances, construction of the HWLOC topology tree:

- requires a fair amount of time as HWLOC must open/parse many system-level files. Further exacerbating the problem is that many operating systems thread-protect access to the system-level files, thus serializing the parsing procedure when multiple libraries or processes are attempting to construct topology trees at the same time (e.g., at process startup or library initialization)

- consumes a fair amount of memory. A single HWLOC topology tree on a complex many-core architecture may consume on the order of 512Kbytes. This seems small - until one realizes that this amount of memory will be consumed by _every_ topology tree. If an application has multiple libraries within it that are independently constructing topology trees, and you are running many processes on a node, memory consumed by topology trees can easily extend into the 10s of megabytes.

Fortunately, PMIx and HWLOC have combined forces to help alleviate this problem. Beginning with HWLOC 2.0, HWLOC offers support for a shared memory version of the topology tree. PMIx 3.0 introduced attribute keys by which this shared memory region can be exposed to users and/or libraries should the host environment (whether the RM or a launcher like "mpirun") create it. The region can be accessed by PMIx-enabled libraries and applications using the following code:

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

This, of course, requires that the library or application build/link against a PMIx library. In some cases, particularly in lower-level libraries, adding a dependency on PMIx is something rather undesirable - developers of such libraries prefer to keep them "thin" with minimal dependencies and as small a memory footprint as possible. Beginning with PMIx v4.1, PMIx provides additional support for such cases by exposing the three HWLOC shmem "hooks" as environmental variables in addition to PMIx keys. Thus, an alternative to the previous code in such circumstances would look like the following:
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
At the completion of either procedure, you can traverse/query the topology tree in "topo" using the usual HWLOC support functions. Note that any attempt to modify the topology tree (including adding data to the "userdata" field of an HWLOC object) will fail, and that you should not "destruct" the topology when done with it (a call to `hwloc_topology_destroy` will return an error).
