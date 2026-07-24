// cudnn_hello_world.cpp
// Build: nvcc -o cudnn_hello_world cudnn_hello_world.cpp -lcudnn
 
#include <cstdio>
#include <cudnn.h>
#include <cuda_runtime.h>
 
int main()
{
    // print cudnn version
    printf("cuDNN version: %zu\n", cudnnGetVersion());
    
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
 
    // Create a cuDNN handle
    cudnnHandle_t handle;
    cudnnStatus_t status = cudnnCreate(&handle);
    if (status != CUDNN_STATUS_SUCCESS) {
        printf("Failed to create cuDNN handle: %s\n", cudnnGetErrorString(status));
        return 1;
    }
 
    
    printf("Hello, cuDNN!\n");
 
    cudnnDestroy(handle);
    return 0;
}
 