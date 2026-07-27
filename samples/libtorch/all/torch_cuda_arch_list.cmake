# libtorch computes its own nvcc -gencode flags from TORCH_CUDA_ARCH_LIST (dotted
# versions, e.g. "7.5", optionally suffixed "+PTX" for virtual/PTX code) instead of
# using CMake's CMAKE_CUDA_ARCHITECTURES (undotted codes, e.g. "75", optionally
# suffixed "-real"/"-virtual"). If both were left set, CMake would inject its own
# competing -gencode flags on top of libtorch's, so once we've translated the value
# we force CMAKE_CUDA_ARCHITECTURES off to leave TORCH_CUDA_ARCH_LIST as the only
# source of truth.

if(NOT CMAKE_CUDA_ARCHITECTURES)
  return()
endif()

set(_orig_cmake_cuda_architectures "${CMAKE_CUDA_ARCHITECTURES}")

# CMake's "native" ("compile for the host GPU's architecture") maps directly onto
# select_compute_arch.cmake's "Auto", which detects installed GPUs at configure time.
if(CMAKE_CUDA_ARCHITECTURES STREQUAL "native")
  set(TORCH_CUDA_ARCH_LIST "Auto" CACHE STRING "Translated from CMAKE_CUDA_ARCHITECTURES" FORCE)
  set(CMAKE_CUDA_ARCHITECTURES FALSE CACHE STRING "Disabled in favor of TORCH_CUDA_ARCH_LIST" FORCE)
  message(STATUS "Translated CMAKE_CUDA_ARCHITECTURES '${_orig_cmake_cuda_architectures}' to "
                 "TORCH_CUDA_ARCH_LIST '${TORCH_CUDA_ARCH_LIST}' (CMAKE_CUDA_ARCHITECTURES disabled)")
  return()
endif()

# Multiple CMAKE_CUDA_ARCHITECTURES entries can share the same code (e.g.
# "87-real;87-virtual" both refer to 8.7), so real/PTX wishes are gathered per
# unique dotted arch before emitting - otherwise they'd produce separate,
# overlapping TORCH_CUDA_ARCH_LIST tokens (e.g. "8.7 8.7+PTX") for the same arch.
set(_arch_keys "")

foreach(_arch ${CMAKE_CUDA_ARCHITECTURES})
  set(_mode "both")
  if(_arch MATCHES "^(.+)-real$")
    set(_code "${CMAKE_MATCH_1}")
    set(_mode "real")
  elseif(_arch MATCHES "^(.+)-virtual$")
    set(_code "${CMAKE_MATCH_1}")
    set(_mode "virtual")
  else()
    set(_code "${_arch}")
  endif()

  if(NOT _code MATCHES "^[0-9]+[af]?$")
    message(FATAL_ERROR "Cannot translate CMAKE_CUDA_ARCHITECTURES entry '${_arch}' to TORCH_CUDA_ARCH_LIST: "
                         "only numeric compute-capability codes (optionally suffixed -real/-virtual, "
                         "and optionally an 'a'/'f' family suffix) are supported.")
  endif()

  set(_letter "")
  if(_code MATCHES "^([0-9]+)([af])$")
    set(_code "${CMAKE_MATCH_1}")
    set(_letter "${CMAKE_MATCH_2}")
  endif()

  string(LENGTH "${_code}" _code_len)
  math(EXPR _major_len "${_code_len} - 1")
  string(SUBSTRING "${_code}" 0 ${_major_len} _major)
  string(SUBSTRING "${_code}" ${_major_len} 1 _minor)
  set(_dotted "${_major}.${_minor}${_letter}")

  list(FIND _arch_keys "${_dotted}" _key_idx)
  if(_key_idx EQUAL -1)
    list(APPEND _arch_keys "${_dotted}")
    set(_want_real_${_dotted} FALSE)
    set(_want_ptx_${_dotted} FALSE)
  endif()
  if(_mode STREQUAL "real" OR _mode STREQUAL "both")
    set(_want_real_${_dotted} TRUE)
  endif()
  if(_mode STREQUAL "virtual" OR _mode STREQUAL "both")
    # "virtual" (PTX-only) has no equivalent in TORCH_CUDA_ARCH_LIST, since a listed
    # version always generates real code there; "+PTX" is the closest safe superset.
    set(_want_ptx_${_dotted} TRUE)
  endif()
endforeach()

set(_torch_cuda_arch_list "")
foreach(_dotted ${_arch_keys})
  if(_want_ptx_${_dotted})
    list(APPEND _torch_cuda_arch_list "${_dotted}+PTX")
  else()
    list(APPEND _torch_cuda_arch_list "${_dotted}")
  endif()
endforeach()

list(JOIN _torch_cuda_arch_list " " TORCH_CUDA_ARCH_LIST)
set(TORCH_CUDA_ARCH_LIST "${TORCH_CUDA_ARCH_LIST}" CACHE STRING "Translated from CMAKE_CUDA_ARCHITECTURES" FORCE)
set(CMAKE_CUDA_ARCHITECTURES FALSE CACHE STRING "Disabled in favor of TORCH_CUDA_ARCH_LIST" FORCE)
message(STATUS "Translated CMAKE_CUDA_ARCHITECTURES '${_orig_cmake_cuda_architectures}' to "
               "TORCH_CUDA_ARCH_LIST '${TORCH_CUDA_ARCH_LIST}' (CMAKE_CUDA_ARCHITECTURES disabled)")
