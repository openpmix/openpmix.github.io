---
layout: default
title: Modify the PMIx Buffer Manipulation APIs
---

RFC0028
=======

Modify the [Expose the PMIx buffer manipulation functions
RFC](https://github.com/pmix/RFCs/pull/20)  
\* Add a pmix\_proc\_t to the parameter list for PMIx\_Data\_pack and
PMIx\_Data\_unpack

Title
-----

Modify the PMIx buffer manipulation APIs

Abstract
--------

The v2 public data buffer op APIs (PMIx\_Data\_pack and
PMIx\_Data\_unpack) do not provide an input parameter for specifying the
intended target (for pack) or source (for unpack) of the data. This
isn’t an issue for operations where both parties are using the same
version of PMIx, but is an issue for cross-version operations. This RFC
adds those parameters.

Labels
------

\[MODIFICATION\]

Action
------

\[APPROVED\]

Copyright Notice
----------------

Copyright 2018 Intel, Inc. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

The v2 public data buffer op APIs (PMIx\_Data\_pack and
PMIx\_Data\_unpack) do not provide an input parameter for specifying the
intended target (for pack) or source (for unpack) of the data. This
isn’t an issue for operations where both parties are using the same
version of PMIx, but is an issue for cross-version operations where the
precise pack/unpack support depends on the version of the source/target.

NOTE: PMIx requires that all processes in the same nspace be based on
the same PMIx version. Cross-version communication, therefore, can only
occur between a client (or tool) and server based on different versions.
It is possible for a client from one application to pack data, publish
it, and have a client of another application (possibly using a different
PMIx version) retrieve that data – in such a case, the PMIx library
shall request the version of the remote participant prior to performing
the data pack/unpack operation. Failure to determine the version of the
source/target shall result in return of the PMIX\_ERR\_NOT\_SUPPORTED
status.

Specifically, the RFC modifies the APIs as follows:

    /**
     * Top-level interface function to pack one or more values into a
     * buffer.
     *
     * The pack function packs one or more values of a specified type into
     * the specified buffer.  The buffer must have already been
     * initialized via the PMIX_DATA_BUFFER_CREATE or PMIX_DATA_BUFFER_CONSTRUCT
     * call - otherwise, the pack_value function will return an error.
     * Providing an unsupported type flag will likewise be reported as an error.
     *
     * Note that any data to be packed that is not hard type cast (i.e.,
     * not type cast to a specific size) may lose precision when unpacked
     * by a non-homogeneous recipient.  The PACK function will do its best to deal
     * with heterogeneity issues between the packer and unpacker in such
     * cases. Sending a number larger than can be handled by the recipient
     * will return an error code (generated upon unpacking) -
     * the error cannot be detected during packing.
     *
     * The identity of the intended recipient of the packed buffer (i.e., the
     * process that will be unpacking it) is used solely to resolve any data type
     * differences between PMIx versions. The recipient must, therefore, be
     * known to the user prior to calling the pack function so that the
     * PMIx library is aware of the version the recipient is using.
     *
     * @param *target Pointer to a pmix_proc_t structure containing the
     * nspace/rank of the process that will be unpacking the final buffer.
     * A NULL value may be used to indicate that the target is based on
     * the same PMIx version as the caller.
     *
     * @param *buffer A pointer to the buffer into which the value is to
     * be packed.
     *
     * @param *src A void* pointer to the data that is to be packed. Note
     * that strings are to be passed as (char **) - i.e., the caller must
     * pass the address of the pointer to the string as the void*. This
     * allows PMIx to use a single pack function, but still allow
     * the caller to pass multiple strings in a single call.
     *
     * @param num_values An int32_t indicating the number of values that are
     * to be packed, beginning at the location pointed to by src. A string
     * value is counted as a single value regardless of length. The values
     * must be contiguous in memory. Arrays of pointers (e.g., string
     * arrays) should be contiguous, although (obviously) the data pointed
     * to need not be contiguous across array entries.
     *
     * @param type The type of the data to be packed - must be one of the
     * PMIX defined data types.
     *
     * @retval PMIX_SUCCESS The data was packed as requested.
     *
     * @retval PMIX_ERROR(s) An appropriate PMIX error code indicating the
     * problem encountered. This error code should be handled
     * appropriately.
     *
     * @code
     * pmix_data_buffer_t *buffer;
     * int32_t src;
     *
     * PMIX_DATA_BUFFER_CREATE(buffer);
     * status_code = PMIx_Data_pack(buffer, &src, 1, PMIX_INT32);
     * @endcode
     */
    PMIX_EXPORT pmix_status_t PMIx_Data_pack(const pmix_proc_t *target,
                                             pmix_data_buffer_t *buffer,
                                             void *src, int32_t num_vals,
                                             pmix_data_type_t type);

    /**
     * Unpack values from a buffer.
     *
     * The unpack function unpacks the next value (or values) of a
     * specified type from the specified buffer.
     *
     * The buffer must have already been initialized via an PMIX_DATA_BUFFER_CREATE or
     * PMIX_DATA_BUFFER_CONSTRUCT call (and assumedly filled with some data) -
     * otherwise, the unpack_value function will return an
     * error. Providing an unsupported type flag will likewise be reported
     * as an error, as will specifying a data type that DOES NOT match the
     * type of the next item in the buffer. An attempt to read beyond the
     * end of the stored data held in the buffer will also return an
     * error.
     *
     * NOTE: it is possible for the buffer to be corrupted and that
     * PMIx will *think* there is a proper variable type at the
     * beginning of an unpack region - but that the value is bogus (e.g., just
     * a byte field in a string array that so happens to have a value that
     * matches the specified data type flag). Therefore, the data type error check
     * is NOT completely safe. This is true for ALL unpack functions.
     *
     *
     * Unpacking values is a "nondestructive" process - i.e., the values are
     * not removed from the buffer. It is therefore possible for the caller
     * to re-unpack a value from the same buffer by resetting the unpack_ptr.
     *
     * Warning: The caller is responsible for providing adequate memory
     * storage for the requested data. As noted below, the user
     * must provide a parameter indicating the maximum number of values that
     * can be unpacked into the allocated memory. If more values exist in the
     * buffer than can fit into the memory storage, then the function will unpack
     * what it can fit into that location and return an error code indicating
     * that the buffer was only partially unpacked.
     *
     * Note that any data that was not hard type cast (i.e., not type cast
     * to a specific size) when packed may lose precision when unpacked by
     * a non-homogeneous recipient.  PMIx will do its best to deal with
     * heterogeneity issues between the packer and unpacker in such
     * cases. Sending a number larger than can be handled by the recipient
     * will return an error code generated upon unpacking - these errors
     * cannot be detected during packing.
     *
     * The identity of the source of the packed buffer (i.e., the
     * process that packed it) is used solely to resolve any data type
     * differences between PMIx versions. The source must, therefore, be
     * known to the user prior to calling the unpack function so that the
     * PMIx library is aware of the version the source used.
     *
     * @param *source Pointer to a pmix_proc_t structure containing the
     * nspace/rank of the process that packed the provided buffer.
     * A NULL value may be used to indicate that the source is based on
     * the same PMIx version as the caller.
     *
     * @param *buffer A pointer to the buffer from which the value will be
     * extracted.
     *
     * @param *dest A void* pointer to the memory location into which the
     * data is to be stored. Note that these values will be stored
     * contiguously in memory. For strings, this pointer must be to (char
     * **) to provide a means of supporting multiple string
     * operations. The unpack function will allocate memory for each
     * string in the array - the caller must only provide adequate memory
     * for the array of pointers.
     *
     * @param type The type of the data to be unpacked - must be one of
     * the BFROP defined data types.
     *
     * @retval *max_num_values The number of values actually unpacked. In
     * most cases, this should match the maximum number provided in the
     * parameters - but in no case will it exceed the value of this
     * parameter.  Note that if you unpack fewer values than are actually
     * available, the buffer will be in an unpackable state - the function will
     * return an error code to warn of this condition.
     *
     * @note The unpack function will return the actual number of values
     * unpacked in this location.
     *
     * @retval PMIX_SUCCESS The next item in the buffer was successfully
     * unpacked.
     *
     * @retval PMIX_ERROR(s) The unpack function returns an error code
     * under one of several conditions: (a) the number of values in the
     * item exceeds the max num provided by the caller; (b) the type of
     * the next item in the buffer does not match the type specified by
     * the caller; or (c) the unpack failed due to either an error in the
     * buffer or an attempt to read past the end of the buffer.
     *
     * @code
     * pmix_data_buffer_t *buffer;
     * int32_t dest;
     * char **string_array;
     * int32_t num_values;
     *
     * num_values = 1;
     * status_code = PMIx_Data_unpack(buffer, (void*)&dest, &num_values, PMIX_INT32);
     *
     * num_values = 5;
     * string_array = malloc(num_values*sizeof(char *));
     * status_code = PMIx_Data_unpack(buffer, (void*)(string_array), &num_values, PMIX_STRING);
     *
     * @endcode
     */
    PMIX_EXPORT pmix_status_t PMIx_Data_unpack(const pmix_proc_t *source,
                                               pmix_data_buffer_t *buffer, void *dest,
                                               int32_t *max_num_values,
                                               pmix_data_type_t type);

Protoype Implementation
-----------------------

Prototype implementation is available in the PMIx master repo in [Pull
Request 644](https://github.com/pmix/pmix/pull/644)

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

