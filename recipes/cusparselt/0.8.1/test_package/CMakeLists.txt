cmake_minimum_required(VERSION 3.22)

project(HelloCuSPARSELt LANGUAGES C CXX)

find_package(cuSPARSELt REQUIRED)
find_package(CUDAToolkit REQUIRED)

add_executable(test_package hello_cusparselt.cpp)

target_link_libraries(test_package PRIVATE cuSPARSELt::cusparseLt CUDA::cudart)
