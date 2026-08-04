#include <stdio.h>
#include <cuda_runtime.h>

__global__ void helloKernel(void) {
    printf("Hello from GPU thread (%d, %d)\n",
           blockIdx.x, threadIdx.x);
}

int main(void) {
    /* ── 1. Check driver / runtime availability ── */
    int driverVersion = 0, runtimeVersion = 0;
    cudaError_t err;

    err = cudaDriverGetVersion(&driverVersion);
    if (err != cudaSuccess || driverVersion == 0) {
        printf("Hello from CPU! (no CUDA driver: %s)\n",
               cudaGetErrorString(err));
        return 0;
    }

    cudaRuntimeGetVersion(&runtimeVersion);

    /* ── 2. Enumerate devices ── */
    int deviceCount = 0;
    err = cudaGetDeviceCount(&deviceCount);
    if (err != cudaSuccess || deviceCount == 0) {
        printf("Hello from CPU! (no CUDA devices: %s)\n",
               cudaGetErrorString(err));
        return 0;
    }

    /* ── 3. Print basic device info ── */
    cudaDeviceProp prop;
    cudaGetDeviceProperties(&prop, 0);
    printf("CUDA driver %d.%d  |  runtime %d.%d  |  device 0: %s\n",
           driverVersion / 1000, (driverVersion % 100) / 10,
           runtimeVersion / 1000, (runtimeVersion % 100) / 10,
           prop.name);

    /* ── 4. Launch kernel ── */
    helloKernel<<<2, 4>>>();

    err = cudaDeviceSynchronize();
    if (err != cudaSuccess) {
        fprintf(stderr, "Kernel failed: %s\n", cudaGetErrorString(err));
        return 1;
    }

    printf("Hello from CPU! (kernel completed successfully)\n");
    return 0;
}
