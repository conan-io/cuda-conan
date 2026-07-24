// hello_cusparselt.cpp
// Build: nvcc -o hello_cusparselt hello_cusparselt.cpp -lcusparseLt

#include <cstdio>
#include <cusparseLt.h>
#include <cuda_runtime.h>

int main()
{
    printf("cuSPARSELt version: %d\n", CUSPARSELT_VERSION);

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

    // Create a cuSPARSELt handle
    cusparseLtHandle_t handle;
    cusparseStatus_t status = cusparseLtInit(&handle);
    if (status != CUSPARSE_STATUS_SUCCESS) {
        printf("Failed to create cuSPARSELt handle: %d\n", status);
        return 1;
    }

    printf("Hello, cuSPARSELt!\n");

    cusparseLtDestroy(&handle);
    return 0;
}
