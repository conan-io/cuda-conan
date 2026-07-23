# cuda-conan
Conan recipes, integration examples, and tutorials for the NVIDIA CUDA Toolkit and CUDA-X GPU accelerated libraries (cuDNN, TensorRT, cuDSS, and more)

> [!WARNING]
> This repository provides **Conan recipes only — no binaries are distributed here**. Creating packages from these recipes will download the NVIDIA CUDA Toolkit and other NVIDIA components as made available by NVIDIA. Use of those downloaded components is governed by NVIDIA's own terms, including any applicable End User License Agreements (EULAs).
>
> The recipes download and unpack binaries as described in NVIDIA's own documentation and tooling:
> - [Windows installer: Extracting and Inspecting the Files Manually](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html)
> - [Tarball and Zip archive deliverables](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#tarball-and-zip-archive-deliverables)
> - https://github.com/NVIDIA/build-system-archive-import-examples

## Why use Conan for CUDA Toolkit and libraries?

- **No system-level installs.** No need to install the CUDA Toolkit separately (system packages, `.deb`, `.rpm`, manual installers, etc.) — Conan fetches all the development components you need, just like any other dependency.
- **One workflow, every platform.** The same installation process works on Linux, Windows, and cross-builds — no platform-specific setup steps to maintain in your CI.
- **Build without a GPU.** Building a CUDA-dependent project does not require a GPU or the GPU driver. You'll only need those for running the resulting executables. This is great for CI runners or workflows where it is faster to cross-build on a workstation than on a low-power NVIDIA Jetson device.
- **Run with confidence.** Use [`conan run`](https://docs.conan.io/2/reference/commands/run.html) or [`conanrunenv`](https://docs.conan.io/2/reference/tools/env/virtualrunenv.html) to run CUDA-enabled executables with the right environment set up automatically.
- **Side-by-side installs.** Because Conan never installs packages at the system level or makes them globally discoverable, multiple CUDA Toolkit versions can coexist on the same machine — build and test the same project against several versions with no conflicts.
- **Cross-building, out of the box.** Just provide a `host` profile with the right cross-compiler, and Conan's host/build profile model handles the rest.

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

### Recipes available in this repository
- `cuda-toolkit`
- `cudnn`
- `cudnn-frontend`
- `cudss`
- `cusparselt`
- `cutlass`
- `nvtx`
- `tensorrt`

If configured as a local remote, you can list them with:

```
conan list "*" -r cuda-conan
```

### Sample integrations
The `samples/` folder contains reference implementations of recipes that make use of the tools and libraries above, currently:

- `libtorch`
- `llama-cpp`
- `onnxruntime`
