cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(llama-cpp REQUIRED CONFIG)
if (LLAMA_WITH_CUDA)
    find_package(CUDAToolkit REQUIRED)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE llama-cpp::llama llama-cpp::common)
if (LLAMA_WITH_CUDA)
    target_link_libraries(${PROJECT_NAME} PRIVATE CUDA::cudart)
endif()
