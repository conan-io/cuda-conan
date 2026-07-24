cmake_minimum_required(VERSION 3.22)

project(HelloCUDNN LANGUAGES C CXX)

find_package(CUDNN REQUIRED)
find_package(CUDAToolkit REQUIRED)

add_executable(test_package hello_cudnn.cpp)

target_link_libraries(test_package PRIVATE CUDNN::cudnn CUDA::cudart)
