#include <stdio.h>
#include <cuda_runtime.h>

__global__ void hello_kernel(int *result) {
    *result = 42;
}

int main() {
    int deviceCount = 0;
    cudaGetDeviceCount(&deviceCount);

    if (deviceCount == 0) {
        printf("No GPU found.\n");
        return 0;
    }

    printf("Found %d GPU(s). Running on GPU 0...\n", deviceCount);

    int *d_result, h_result;
    cudaMalloc(&d_result, sizeof(int));
    hello_kernel<<<1, 1>>>(d_result);
    cudaMemcpy(&h_result, d_result, sizeof(int), cudaMemcpyDeviceToHost);
    cudaFree(d_result);

    printf("GPU kernel ran successfully. Result: %d\n", h_result);
    return 0;
}