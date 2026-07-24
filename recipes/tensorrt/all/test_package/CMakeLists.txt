cmake_minimum_required(VERSION 3.18)
project(test_package LANGUAGES CXX CUDA)

find_package(TensorRT REQUIRED CONFIG)

add_executable(test_package test_package.cu)
target_link_libraries(test_package PRIVATE TensorRT::nvinfer)
