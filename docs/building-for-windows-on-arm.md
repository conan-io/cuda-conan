# Building CUDA-enabled applications for Windows 11 on ARM (NVIDIA RTX Spark)

`cuda-conan` packages the **CUDA Toolkit 13.4.0 developer preview**, the first CUDA release with a compiler
and device libraries that target **Windows 11 on ARM64** — both natively and as a cross-compilation target from
x86_64. This guide covers adding CUDA to an existing `conanfile.py`, cross-compiling without ARM hardware, and
verifying the setup.

> [!NOTE]
> CUDA 13.4 is currently a **developer preview**, made available by NVIDIA so that Developers can start porting their applications.
> See [Release Notes](https://docs.nvidia.com/cuda/developer-preview/13.4/cuda-toolkit-release-notes/index.html).

## Prerequisites

- A recent version of Conan 2 (>=2.31.1 recommended)
- Visual Studio 2022 or 2026, with the **ARM64 MSVC toolset** installed:
  * Open the **Visual Studio Installer** → **Modify** your installation.
  * Under **Individual components**, search for **"ARM64"** and select the **C++ ARM64 build tools**
     component for your version (e.g. **MSVC v143 - VS 2022 C++ ARM64 build tools**).
  * Apply.

  This is required whether you're cross-building from x86_64 or building natively on an Arm64 device — see
  [ARM64 Visual Studio is officially here!](https://devblogs.microsoft.com/visualstudio/arm64-visual-studio-is-officially-here/)
  and [Visual Studio on Arm Processor-Powered Devices](https://learn.microsoft.com/en-us/visualstudio/install/visual-studio-on-arm-devices?view=visualstudio)
  for background.
- For the rest of your dependencies, Conan Center currently builds and supports over 800 libraries
  for Windows ARM64, so your most likely dependencies should already be covered! — see
  [Windows ARM64 builds now enabled in Conan Center](https://blog.conan.io/armv8/arm64/windows/conan/2025/10/01/Windows-arm64-builds-now-enabled-in-Conan-Center.html).

## Adding CUDA support to your project

In your `conanfile.py`:

```python
def requirements(self):
    self.requires("cuda-toolkit/[>=13 <14]")
    self.tool_requires("cuda-toolkit/<host_version>")
```

And that's it! This is the same configuration we expect on all platforms where CUDA is supported, for both native and cross-build context.

Your `CMakeLists.txt` needs no CUDA-specific changes, and can follow the recommended CMake practice:

```cmake
enable_language(CUDA)
find_package(CUDAToolkit)
```

Conan resolves and provides the dependency and `find_package(CUDAToolkit)` finds it — no need for a system-wide CUDA install, no environment variables to point to specific CUDA installations, and nothing extra to configure in CI beyond having Conan available - it's the same as with other dependencies.

In your Conan profile, it is recommended that you add the following configuration for your desired GPU architecture(s), for example:

```
tools.cmake.cmaketoolchain:extra_variables*={'CMAKE_CUDA_ARCHITECTURES':'87-real'}
```

## Cross-building for Windows ARM64

Cross-compiling does not require ARM64 hardware; it can be performed directly on existing Windows x86_64 workstations or CI runners while letting Conan configure the build for ARM64. If you are on Windows x86_64 and your Conan profile is set up for msvc, you can simply add `-s arch=armv8` to cross-build for ARM64, for example:

```
conan create . -s arch=armv8
```

When cross-building, Conan ensures that `nvcc` runs on your x86_64 workstation, while the CUDA libraries linked into your application are ARM64.

## Example 1: building and running `cuda-samples`

[`cuda-samples`](https://github.com/NVIDIA/cuda-samples) is NVIDIA's official collection of example CUDA
applications. It ranges from minimal examples like
`vectorAdd` and `deviceQuery` to CUDA library usage (cuBLAS, cuFFT, ...) and domain-specific examples, grouped
into folders such as `0_Introduction`, `1_Utilities`, and `4_CUDA_Libraries`. 

This repository contains a recipe to build `cuda-samples` from source using CUDA from Conan, including support for Windows ARM64.

Clone the repository and register it as a local Conan remote:

```
git clone https://github.com/conan-io/cuda-conan
conan remote add cuda-conan ./cuda-conan
```

Then build the samples for ARM64:

```
cd cuda-conan/samples/cuda-samples

conan build . -s arch=armv8 -c tools.cmake.cmaketoolchain:generator=Ninja -cc core.version_ranges:resolve_prereleases=True
```

* If building on Windows `armv8`, the samples will be built natively and the executables can be run on your development device
* If cross-building from `x86_64`, Conan will set up the cross-build for you
* If you want to build and run natively on Windows x86_64, simply remove the `-s arch=` argument.

Note that `-cc core.version_ranges:resolve_prereleases=True` is required as 13.4.0 is explicitly published as a pre-release.

Once the build finishes, you can run any of the executables in the build if built for your CPU architecture. Remember to first load up `conanrun.bat` so that Conan configures the run environment for you, e.g.:

```
cmd.exe /k "build\Release\generators\conanrun.bat"
build\Release\cpp\1_Utilities\deviceQuery\deviceQuery.exe
```

The application should launch successfuly. If there is no GPU with an NVIDIA driver installed, it should simply report that cudaGetDeviceCount returned an error querying the devices.


## Example 2: building `llama-cpp` for Windows ARM64 with CUDA support for RTX Spark

[`llama.cpp`](https://github.com/ggml-org/llama.cpp) is a widely used, dependency-light C/C++ inference engine
for LLaMA and other GGUF-format language models. It's one of the most popular ways to run LLMs locally, with
over 80k stars on GitHub, and is the engine behind many downstream projects (Ollama, LM Studio, and others).

This repository contains a recipe to build `llama.cpp` from source using CUDA from Conan, including support
for Windows ARM64:

```
cd samples/llama-cpp
conan create all --version=b6565 -pr clang-cl-arm64 -cc core.version_ranges:resolve_prereleases=True
```

This command can be run on x86_64 Windows and ARM64 Windows. You can customize the CUDA GPU architecture by editing the profile at `samples/llama-cpp/clang-cl-common`.

> [!IMPORTANT]
> Windows ARM64 builds of `llama.cpp` currently currently require building with **Clang** (`clang-cl`), rather than MSVC's
> `cl.exe`. Clang can be installed via the **Visual Studio Installer**: under **Individual components**, search
> for **"Clang"** and select the **C++ Clang Compiler for Windows** component, then apply.

## Current limitations

- While the ARM64 binaries will run on any Windows on ARM, CUDA support at runtime can only be tested on NVIDIA-powered devices.
- At the moment, only `cuda-toolkit` 13.4 preview is available. Other libraries (such as cuDNN) will be made available once they are released publicly by NVIDIA.

## References

- [CUDA Toolkit 13.4 Developer Preview release notes](https://docs.nvidia.com/cuda/developer-preview/13.4/cuda-toolkit-release-notes/index.html) — NVIDIA
- [CUDA Toolkit 13.4 Developer Preview documentation](https://docs.nvidia.com/cuda/developer-preview/13.4/index.html) — NVIDIA
- [NVIDIA and Microsoft Reinvent Windows PCs for the Age of Personal AI](https://nvidianews.nvidia.com/news/nvidia-microsoft-windows-pcs-agents-rtx-spark) — NVIDIA Newsroom
- [Introducing a powerful new chapter for Windows PCs, accelerated by NVIDIA RTX Spark](https://blogs.windows.com/windowsexperience/2026/05/31/introducing-a-powerful-new-chapter-for-windows-pcs-accelerated-by-nvidia-rtx-spark/) — Microsoft Windows Experience Blog

## Feedback

Please report issues or feedback on the
[cuda-conan repository](https://github.com/conan-io/cuda-conan), and check the
[roadmap discussion](https://github.com/conan-io/cuda-conan/discussions/2) for what's coming next.
