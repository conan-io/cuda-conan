cmake_minimum_required(VERSION 3.25)

project(PackageTest LANGUAGES CXX CUDA)

find_package(CUDAToolkit REQUIRED)

message("CUDAToolkit_VERSION: ${CUDAToolkit_VERSION}")
message("CUDAToolkit_BIN_DIR: ${CUDAToolkit_BIN_DIR}")
message("CUDAToolkit_LIBRARY_DIR: ${CUDAToolkit_LIBRARY_DIR}")
message("CUDAToolkit_LIBRARY_ROOT: ${CUDAToolkit_LIBRARY_ROOT}")
message("CUDAToolkit_NVCC_EXECUTABLE: ${CUDAToolkit_NVCC_EXECUTABLE}")

add_executable(example hello_cuda.cu)
target_compile_options(example PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:--verbose>)
