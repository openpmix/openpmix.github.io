---
layout: default
title: Expose PMIx Buffer Manipulation Functions
---

RFC0020
=======

Title
-----

Expose the PMIx buffer manipulation functions

Abstract
--------

Host resource managers (RMs) need to transfer PMIx public data
structures between nodes. Many clusters are homogeneous, and so
transferring can be done rather simply. However, greater effort is
required in heterogeneous environments to ensure binary data is
correctly transferred. The PMIx buffer manipulation functions in the
convenience library have been developed and validated for this purpose –
exposing them to the host environment eases PMIx adoption.

Labels
------

\[EXTENSION\]

Action
------

\[APPROVED\]

Copyright Notice
----------------

Copyright 2017 Intel, Inc. All rights reserved.

This document is subject to all provisions relating to code
contributions to the PMIx community as defined in the community’s
[LICENSE](https://github.com/pmix/RFCs/tree/master/LICENSE) file. Code
Components extracted from this document must include the License text as
described in that file.

Description
-----------

The PMIx community has developed and validated several data utilities
for supporting heterogeneous environments in their convenience library.
While the library stands independently of the PMIx standard, users of
the library have requested that the utilities be exposed to ease
adoption. Accordingly, this RFC adds five APIs for this purpose.

NOTE: PMIx implementations focused solely on homogeneous environments
are unlikely to require such support. The PMIx community, however,
requests that all implementations at least provide the data utility APIs
as "stubs" that return PMIX\_ERR\_NOT\_SUPPORTED to maximize
portability.

The APIs operate on a new data structure defined in pmix\_common.h,
along with some convenience macros for creating and releasing
structures:

    typedef struct pmix_data_buffer {
        /** Start of my memory */
        char *base_ptr;
        /** Where the next data will be packed to (within the allocated
            memory starting at base_ptr) */
        char *pack_ptr;
        /** Where the next data will be unpacked from (within the
            allocated memory starting as base_ptr) */
        char *unpack_ptr;
        /** Number of bytes allocated (starting at base_ptr) */
        size_t bytes_allocated;
        /** Number of bytes used by the buffer (i.e., amount of data --
            including overhead -- packed in the buffer) */
        size_t bytes_used;
    } pmix_data_buffer_t;
    #define PMIX_DATA_BUFFER_CREATE(m)                                          \
        do {                                                                    \
            (m) = (pmix_data_buffer_t*)calloc(1, sizeof(pmix_data_buffer_t));   \
        } while (0)
    #define PMIX_DATA_BUFFER_RELEASE(m)             \
        do {                                        \
            if (NULL != (m)->base_ptr) {            \
                free((m)->base_ptr);                \
            }                                       \
            free((m));                              \
            (m) = NULL;                             \
        } while (0)
    #define PMIX_DATA_BUFFER_CONSTRUCT(m)       \
        memset((m), 0, sizeof(pmix_data_buffer_t))
    #define PMIX_DATA_BUFFER_DESTRUCT(m)        \
        do {                                    \
            if (NULL != (m)->base_ptr) {        \
                free((m)->base_ptr);            \
            }                                   \
        } while (0)

The utilities use the standard C-language functions to convert binary
data to/from network and host byte order. The results are packed into a
binary array that is automatically expanded as required to accommodate
the stored data. Thus, while a provided pmix\_data\_buffer\_t pointer to
a data utility API will not be changed, users need to be aware that the
internal pointers will be modified when returned.

The provided functions include:

    /* Pack the provided data into a buffer in preparation for transmission. The resulting
     * data array pointed to by buffer->base_ptr contains the packed data
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

    pmix_status_t PMIx_Data_pack(pmix_data_buffer_t *buffer,
                                 void *src, int32_t num_vals,
                                 pmix_data_type_t type);

    /* Unpack data.
     *
     * @param *buffer A pointer to the buffer from which the value will be
     * extracted.
     *
     * @param *dest A void* pointer to the memory location into which the
     * data is to be stored. Note that these values will be stored
     * contiguously in memory. For strings, this pointer must be to (char**)
     * to provide a means of supporting multiple string
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
    */
    pmix_status_t PMIx_Data_unpack(pmix_data_buffer_t *buffer, void *dest,
                                   int32_t *max_num_values,
                                   pmix_data_type_t type);

    /* Copy a PMIx data type
     * Since registered data types can be complex structures, the system
     * needs some way to know how to copy the data from one location to
     * another (e.g., for storage in the registry). This function, which
     * can call other copy functions to build up complex data types, defines
     * the method for making a copy of the specified data type.
     *
     * @param **dest The address of a pointer into which the
     * address of the resulting data is to be stored.
     *
     * @param *src A pointer to the memory location from which the
     * data is to be copied.
     *
     * @param type The type of the data to be copied - must be one of
     * the PMIx defined data types.
     *
     * @retval PMIX_SUCCESS The value was successfully copied.
     *
     * @retval PMIX_ERROR(s) An appropriate error code.
    */
    pmix_status_t PMIx_Data_copy(void **dest, void *src, pmix_data_type_t type);

    /* Print a PMIx data type
     * Since registered data types can be complex structures, the system
     * needs some way to know how to print them (i.e., convert them to a string
     * representation). Provided for debug purposes.
     *
     * @retval PMIX_SUCCESS The value was successfully printed.
     *
     * @retval PMIX_ERROR(s) An appropriate error code.
    */
    pmix_status_t PMIx_Data_print(char **output, char *prefix,
                                  void *src, pmix_data_type_t type);

    /* Copy the pmix_data_buffer_t payload from a src struct to a dest
     * This function will append a copy of the payload in one buffer into
     * another buffer.
     * NOTE: This is NOT a destructive procedure - the
     * source buffer's payload will remain intact, as will any pre-existing
     * payload in the destination's buffer.
    */
    pmix_status_t PMIx_Data_copy_payload(pmix_data_buffer_t *dest,
                                         pmix_data_buffer_t *src);

These are thin wrappers around the internal PMIx convenience library
functions to avoid exposing the internal object management system to the
standard.

Protoype Implementation
-----------------------

Prototype implementation is available in the PMIx master repo in [Pull
Request 379](https://github.com/pmix/master/pull/379)

Author(s)
---------

Ralph H. Castain  
Intel, Inc.  
Github: rhc54

