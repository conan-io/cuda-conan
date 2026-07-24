cmake_minimum_required(VERSION 3.22)

project(HelloCuDSS LANGUAGES C CXX)

find_package(cudss REQUIRED)
find_package(CUDAToolkit REQUIRED)

add_executable(test_package hello_cudss.cpp)

target_link_libraries(test_package PRIVATE cudss CUDA::cudart)
