cmake_minimum_required(VERSION 3.17)

project(PackageTest LANGUAGES CXX CUDA)

# Note: this will fall back to CMake's built-in find module
# if the package keeps the structure CMake knows about,
# it will locate the libraries relative to where it found nvcc
# Note2: this is only for demonstrations purposes
find_package(CUDAToolkit REQUIRED)
message("CUDAToolkit_BIN_DIR: ${CUDAToolkit_BIN_DIR}")

add_executable(example example.cu)

