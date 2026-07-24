// hello_cudss.cpp
// Build: nvcc -o hello_cudss hello_cudss.cpp -lcudss

#include <cstdio>
#include <cudss.h>
#include <cuda_runtime.h>

int main()
{
    printf("cuDSS version: %d\n", CUDSS_VERSION);

    // Check for a GPU
    int device_count = 0;
    cudaError_t cuda_err = cudaGetDeviceCount(&device_count);
    if (cuda_err != cudaSuccess || device_count == 0) {
        printf("No CUDA GPU available: %s\n", cudaGetErrorString(cuda_err));
        return 0;
    }

    cudaDeviceProp prop;
    cudaGetDeviceProperties(&prop, 0);
    printf("GPU: %s\n", prop.name);

    // Create a cuDSS handle
    cudssHandle_t handle;
    cudssStatus_t status = cudssCreate(&handle);
    if (status != CUDSS_STATUS_SUCCESS) {
        printf("Failed to create cuDSS handle: %d\n", status);
        return 1;
    }

    printf("Hello, cuDSS!\n");

    cudssDestroy(handle);
    return 0;
}
