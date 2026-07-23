# cuda-conan
Conan recipes, integration examples, and tutorials for the NVIDIA CUDA Toolkit and CUDA-X GPU accelerated libraries (cuDNN, TensorRT, cuDSS, and more)

> [!WARNING]
> This repository provides **Conan recipes only — no binaries are distributed here**. Creating packages from these recipes will download the NVIDIA CUDA Toolkit and other NVIDIA components as made available by NVIDIA. Use of those downloaded components is governed by NVIDIA's own terms, including any applicable End User License Agreements (EULAs).
>
> The recipes download and unpack binaries as described in NVIDIA's own documentation and tooling:
> - [Windows installer: Extracting and Inspecting the Files Manually](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html)
> - [Tarball and Zip archive deliverables](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#tarball-and-zip-archive-deliverables)
> - https://github.com/NVIDIA/build-system-archive-import-examples

## Getting started

You can add this repository as a local Conan remote:

```
$ git clone https://github.com/conan-io/cuda-conan
$ conan remote add cuda-conan ./cuda-conan
```

In your recipes (`conanfile.py`), you can add the CUDA Toolkit as a requirement in the following way:

```
def requirements(self):
    self.requires("cuda-toolkit/13.2.0")
    self.tool_requires("cuda-toolkit/<host_version>)
```

In your `CMakeLists.txt`

```
enable_language(CUDA)
find_package(CUDAToolkit)
```
