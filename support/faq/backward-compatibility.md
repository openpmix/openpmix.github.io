---
layout: default
title: Backward Compatibility
---

PMIx offers limited backward compatibility with the PMI-1 and PMI-2
definitions. Support for those definitions is provided by translating
the called function into its PMIx equivalent – e.g., a call to PMI\_Get
invokes a wrapper that translates the provided input parameters, calls
PMIx\_Get, translates the returned PMIx values into a form compatible
with the PMI-1 definition, and returns them.

The following table shows the supported and unsupported functions for
both sets of definitions. An ‘X’ indicates that the function is
supported, while a ‘-‘ indicates it is not supported.

Notes:

-   This support is not intended to fully encompass the PMI-1 and PMI-2
    definitions. Instead, the intent was to provide a minimum level of
    support consistent both with that typically required by parallel
    programming libraries and found in supporting resource managers.
    Thus, while every PMI-1 or PMI-2 function definition is present in
    the respective PMIx-provided library, not every function is actually
    supported. Unsupported functions will return the PMI\_FAIL or
    PMI2\_FAIL response.
-   PMIx support for a backward compatible definition does not imply
    support by the underlying host environment – it only indicates that
    PMIx will communicate the request
-   System-provided values (e.g., universe size) may differ from those
    returned by PMI-1 or PMI-2 due to differences in definitions and/or
    implementations
-   The table rows reflect the API ordering in the original include
    files


<table border="5" width="50%" cellspacing="3" cellpadding="4">
<tbody>
<tr>
<th colspan="4">
<h3><center>PMIx Backward Compatibility Support</center></h3>
</th>
</tr>
<tr align="CENTER" valign="MIDDLE">
<th colspan="2">PMI-1</th>
<th colspan="2">PMI-2</th>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Init</td>
<td>X</td>
<td>PMI2_Init</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Initialized</td>
<td>X</td>
<td>PMI2_Initialized</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Finalize</td>
<td>X</td>
<td>PMI2_Finalize</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Abort</td>
<td>X</td>
<td>PMI2_Abort</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_KVS_Put</td>
<td>X</td>
<td>PMI2_Job_Spawn</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_KVS_Commit</td>
<td>X</td>
<td>PMI2_Job_GetId</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_KVS_Get</td>
<td>X</td>
<td>PMI2_Job_GetRank</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Barrier</td>
<td>X</td>
<td>PMI2_Info_GetSize</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Get_size</td>
<td>X</td>
<td>PMI2_Job_Connect</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Get_rank</td>
<td>X</td>
<td>PMI2_Job_Disconnect</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Get_universe_size</td>
<td>X</td>
<td>PMI2_KVS_Put</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Get_appnum</td>
<td>X</td>
<td>PMI2_KVS_Fence</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Publish_name</td>
<td>X</td>
<td>PMI2_KVS_Get</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Unpublish_name</td>
<td>X</td>
<td>PMI2_Info_GetNodeAttr</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Lookup_name</td>
<td>X</td>
<td>PMI2_Info_GetNodeAttrIntArray</td>
<td>&#8211;</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Get_id</td>
<td>X</td>
<td>PMI2_Info_PutNodeAttr</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Get_kvs_domain_id</td>
<td>X</td>
<td>PMI2_Info_GetJobAttr</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Get_id_length_max</td>
<td>X</td>
<td>PMI2_Info_GetJobAttrIntArray</td>
<td>&#8211;</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Get_clique_size</td>
<td>X</td>
<td>PMI2_Nameserv_publish</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Get_clique_ranks</td>
<td>X</td>
<td>PMI2_Nameserv_lookup</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_KVS_Get_my_name</td>
<td>X</td>
<td>PMI2_Nameserv_unpublish</td>
<td>X</td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_KVS_Get_name_length_max</td>
<td>X</td>
<td></td>
<td></td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_KVS_Get_key_length_max</td>
<td>X</td>
<td></td>
<td></td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_KVS_Get_value_length_max</td>
<td>X</td>
<td></td>
<td></td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_KVS_Create</td>
<td>&#8211;</td>
<td></td>
<td></td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_KVS_Destroy</td>
<td>&#8211;</td>
<td></td>
<td></td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_KVS_Iter_first</td>
<td>&#8211;</td>
<td></td>
<td></td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_KVS_Iter_next</td>
<td>&#8211;</td>
<td></td>
<td></td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Spawn_multiple</td>
<td>X</td>
<td></td>
<td></td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Parse_option</td>
<td>&#8211;</td>
<td></td>
<td></td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Args_to_keyval</td>
<td>&#8211;</td>
<td></td>
<td></td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Free_keyvals</td>
<td>&#8211;</td>
<td></td>
<td></td>
</tr>
<tr align="CENTER" valign="MIDDLE">
<td>PMI_Get_options</td>
<td>&#8211;</td>
<td></td>
<td></td>
</tr>
</tbody>
</table>
