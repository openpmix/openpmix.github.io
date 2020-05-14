---
layout: default
title: RM-Provided Information
---

UNDER DEVELOPMENT
=================

Launching a new job can be accomplished much more scalably if the host
resource manager provides each application process with a set of
information required for initial wireup support and for optimizing
operations. The following data is available on the indicated platforms,
beginning with the specified version.

<table border="5" width="80%" cellspacing="3" cellpadding="4">
<tbody>
<tr>
<th colspan="8">
<h3><center>Job-Level Information</center></h3>
</th>
</tr>
<tr align="CENTER" valign="MIDDLE">
<th>PMIx Standard</th>
<th>Attribute</th>
<th>Data Type</th>
<th>Description</th>
<th>PMIx Reference Server</th>
<th>Open MPI (mpiexec)</th>
<th>Slurm</th>
<th>Job Step Manager</th>
</tr>
<tr>
<td>v1</td>
<td>PMIX_CLUSTER_ID</td>
<td>char *</td>
<td>a string name for the cluster on which this job is executing</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>No plans</td>
</tr>
<tr>
<td></td>
<td>PMIX_NSPACE</td>
<td>char *</td>
<td>nspace of the job</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>1.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_JOBID</td>
<td>char *</td>
<td>jobid assigned by scheduler</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>1.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_NPROC_OFFSET</td>
<td>pmix_rank_t</td>
<td>starting global rank of this job</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>1.0 (always 0)</td>
</tr>
<tr>
<td></td>
<td>PMIX_LOCALLDR</td>
<td>pmix_rank_t</td>
<td>lowest rank on this node within this job</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>1.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_APPLDR</td>
<td>pmix_rank_t</td>
<td>lowest rank in this app within this job</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>2.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_SESSION_ID</td>
<td>uint32_t</td>
<td>session identifier</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>2.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_NODE_LIST</td>
<td>char *</td>
<td>comma-delimited list of nodes running procs for the specified nspace</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>1.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_ALLOCATED_NODELIST</td>
<td>char *</td>
<td>comma-delimited list of all nodes in this allocation regardless of whether or not they currently host procs</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>2.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_UNIV_SIZE</td>
<td>uint32_t</td>
<td>number of processes in this namespace</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>1.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_JOB_SIZE</td>
<td>uint32_t</td>
<td>number of processes in this job</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>1.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_JOB_NUM_APPS</td>
<td>uint32_t</td>
<td>number of apps in this job</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>2.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_APP_SIZE</td>
<td>uint32_t</td>
<td>number of processes in this application</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>2.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_MAX_PROCS</td>
<td>uint32_t</td>
<td>largest number of allowed processes for this application</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>1.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_NUM_NODES</td>
<td>uint32_t</td>
<td>number of nodes in the nspace</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>2.0</td>
</tr>
<tr>
<th colspan="8">
<h3><center>Per-Node Information</center></h3>
</th>
</tr>
<tr>
<td>v1</td>
<td>PMIX_NODE_SIZE</td>
<td>uint32_t</td>
<td>number of processes across all jobs on this node</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>1.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_LOCAL_SIZE</td>
<td>uint32_t</td>
<td>number of processes in this job on this node</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>1.0</td>
</tr>
<tr>
<td>v2</td>
<td>PMIX_AVAIL_PHYS_MEMORY</td>
<td>uint64_t</td>
<td>total available physical memory on this node</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>2.0</td>
</tr>
<tr>
<th colspan="8">
<h3><center>Per-Process Information</center></h3>
</th>
</tr>
<tr>
<td>v1</td>
<td>PMIX_PROCID</td>
<td>pmix_proc_t</td>
<td>process identifier</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td></td>
</tr>
<tr>
<td></td>
<td>PMIX_APPNUM</td>
<td>uint32_t</td>
<td>app number within a MPMD job</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>2.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_RANK</td>
<td>pmix_rank_t</td>
<td>process rank within the job</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>1.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_GLOBAL_RANK</td>
<td>pmix_rank_t</td>
<td>rank spanning across all jobs in this session</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>No plans</td>
</tr>
<tr>
<td></td>
<td>PMIX_APP_RANK</td>
<td>pmix_rank_t</td>
<td>rank within this app</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>1.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_LOCAL_RANK</td>
<td>uint16_t</td>
<td>rank on this node within this job</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>1.0</td>
</tr>
<tr>
<td></td>
<td>PMIX_NODE_RANK</td>
<td>uint16_t</td>
<td>rank on this node spanning all jobs</td>
<td>v1.0</td>
<td>v2.0</td>
<td>v16.05</td>
<td>No plans</td>
</tr>
</tbody>
</table>
