import os
import json
from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, download, get, load, rename, replace_in_file


class CudaToolkitConan(ConanFile):
    name = "cuda-toolkit"
    version = "13.4.3"
    package_type = "shared-library"
    license = "CUDA Toolkit End-User License Agreement"
    url = "https://github.com/conan-io/cuda-conan"
    homepage = "https://developer.nvidia.com/cuda-toolkit"
    description = "A development environment for creating high performance GPU-accelerated applications"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _windows_arch(self):
        return "arm64" if self.settings.arch == "armv8" else "x64"

    def validate(self):
        if self.settings.os not in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Operating system not supported")
        if self.settings.arch not in ["x86_64", "armv8"]:
            raise ConanInvalidConfiguration("Architecture not supported")

    def build(self):
        base_url = "https://developer.download.nvidia.com/compute/cuda/redist"
        distrib = f"redistrib_{self.version}.json"
        json_distrib = f"{base_url}/{distrib}"
        download(self, url=json_distrib, filename=distrib)
        json_content = load(self, distrib)
        cuda_distrib = json.loads(json_content)

        if self.settings.os == "Linux":
            cuda_platform = "linux-sbsa" if self.settings.arch == "armv8" else "linux-x86_64"
        else:
            cuda_platform = "windows-arm64" if self.settings.arch == "armv8" else "windows-x86_64"

        self.output.info(f"About to download CUDA toolkit components for {cuda_platform}")

        components = [
            "cccl",
            "cuda_crt",
            "cuda_cudart",
            "cuda_cuobjdump",
            "cuda_cupti",
            "cuda_cuxxfilt",
            "cuda_nvcc",
            "cuda_nvdisasm",
            "cuda_nvml_dev",
            "cuda_nvprune",
            "cuda_nvrtc",
            "cuda_nvtx",
            "cuda_profiler_api",
            "cuda_sanitizer_api",
            "libcublas",
            "libcufft",
            "libcurand",
            "libcusolver",
            "libcusparse",
            "libnpp",
            "libnvfatbin",
            "libnvjitlink",
            "libnvjpeg",
            "libnvptxcompiler",
            "libnvvm",
            "cuda_tileiras",
        ]

        platform_components = {
            "linux-x86_64": ["libcufile", "cuda_sandbox_dev", "cuda_opencl", "cuda_culibos", "libcuobjclient"],
            "linux-sbsa": ["libcufile", "cuda_sandbox_dev", "cuda_culibos", "cuda_compat_orin", "libcudla", "libcuobjclient"],
            "windows-x86_64": ["cuda_opencl", "visual_studio_integration"],
            "windows-arm64": ["cuda_opencl", "visual_studio_integration", "libcudla"],
        }
        components += platform_components.get(cuda_platform, [])

        for component_name, data in cuda_distrib.items():
            if component_name not in components:
                self.output.info(f"Skipping {component_name}")
                continue
            else:
                self.output.info(f"About to download {component_name} for {cuda_platform}")

            url = f"{base_url}/{data[cuda_platform]['relative_path']}"
            checksum = data[cuda_platform]['sha256']

            get(self, url, sha256=checksum, destination="cuda", strip_root=True, keep_permissions=False)
            rename(self, f"{self.build_folder}/cuda/LICENSE", f"LICENSE_{component_name}")
        if self.settings.os == "Linux":
            # When crossbuilding, point nvcc to the target directory in the "host" package (for the target architecture),
            # rather than have it look relative to itself (which is the current architecture of the build machine)
            replace_in_file(self, "cuda/bin/nvcc.profile", '$(TOP)/$(_TARGET_DIR_)/', '$(CONAN_CUDA_TARGET_DIR)/')
            replace_in_file(self, "cuda/bin/nvcc.profile", "lib$(_TARGET_SIZE_)", "lib" )
        else:
            # When cross-building, get nvcc to locate libraries in host package
            replace_in_file(
                self,
                "cuda/bin/nvcc.profile",
                'LIBRARIES        =+ $(_SPACE_) "/LIBPATH:$(TOP)/lib/$(_WIN_PLATFORM_)"',
                'CONAN_CUDA_LIB_DIR ?= $(TOP)/lib/$(_WIN_PLATFORM_)\n'
                'LIBRARIES        =+ $(_SPACE_) "/LIBPATH:$(CONAN_CUDA_LIB_DIR)"',
            )

    def package(self):
        copy(self, "LICENSE*", src=self.build_folder, dst=os.path.join(self.package_folder, "licenses"))

        for folder in ["bin", "nvml", "nvvm", "compat_orin"]:
            copy(self, "*", src=os.path.join(self.build_folder, "cuda", folder), dst=os.path.join(self.package_folder, folder))

        if self.settings.os == "Linux":
            arch = "sbsa" if self.settings.arch == "armv8" else str(self.settings.arch)
            targets_folder = f"targets/{arch}-linux"
            copy(self, "*", src=os.path.join(self.build_folder, "cuda", "lib"), dst=os.path.join(self.package_folder, targets_folder, "lib"))
            copy(self, "*", src=os.path.join(self.build_folder, "cuda", "include"), dst=os.path.join(self.package_folder, targets_folder, "include"))
            copy(self, "*", src=os.path.join(self.build_folder, "cuda", "res"), dst=os.path.join(self.package_folder, targets_folder, "res"))

            include_symlink = Path(f"targets/{arch}-linux/include")
            lib64_symlink = Path(f"targets/{arch}-linux/lib")
            res_symlink = Path(f"targets/{arch}-linux/res")
            include = Path(os.path.join(self.package_folder, "include"))
            lib = Path(os.path.join(self.package_folder, "lib64"))
            res = Path(os.path.join(self.package_folder, "res"))
            include.symlink_to(include_symlink)
            lib.symlink_to(lib64_symlink)
            res.symlink_to(res_symlink)
        elif self.settings.os == "Windows":
            for folder in ["compute-sanitizer", "include", "lib"]:
                copy(self, "*", src=os.path.join(self.build_folder, "cuda", folder), dst=os.path.join(self.package_folder, folder))

            copy(self, "*", src=os.path.join(self.build_folder, "cuda", "visual_studio_integration"),
                            dst=os.path.join(self.package_folder, "extras", "visual_studio_integration") )

    def package_id(self):
        self.info.settings.rm_safe("compiler")
        self.info.settings.rm_safe("build_type")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CUDAToolkit") # what consumers will expect
        self.cpp_info.set_property("cmake_find_mode", "none") # but don't generate it
        self.cpp_info.set_property("cmake_target_name", "CUDA::toolkit")

        nvcc = "nvcc.exe" if self.settings.os == "Windows" else "nvcc"
        self.buildenv_info.define_path("CUDACXX", os.path.join(self.package_folder, "bin", nvcc))

        if not self.settings_target:
            self.buildenv_info.define_path("CUDAToolkit_ROOT", self.package_folder)
            if self.settings.os == "Linux":
                arch = "sbsa" if self.settings.arch == "armv8" else str(self.settings.arch)
                self.buildenv_info.define_path("CONAN_CUDA_TARGET_DIR", os.path.join(self.package_folder, "targets", f"{arch}-linux"))
            else:
                lib_dir = os.path.join(self.package_folder, "lib", self._windows_arch).replace("\\", "/")
                self.buildenv_info.define_path("CONAN_CUDA_LIB_DIR", lib_dir)

        if self.settings.os == "Linux":
            self.cpp_info.libdirs = ["lib64"]
        else:
            arch = self._windows_arch
            self.cpp_info.libdirs = [f"lib/{arch}", f"nvvm/lib/{arch}"]
            # nvvm64 dll is in nvvm/bin/x64 for x86_64, but directly in nvvm/bin for arm64
            self.cpp_info.bindirs = ["bin", f"bin/{arch}", "nvvm/bin/x64" if arch == "x64" else "nvvm/bin"]

        if self.settings_build.os == "Windows":
            # Only has effect when Windows and the CMake generator is Visual Studio
            package_folder = f"{self.package_folder}".replace('\\', '/')
            self.conf_info.define("tools.cmake.cmaketoolchain:toolset_cuda", package_folder)

        if self.settings_target and self.settings_target.get_safe("build_type"):
            extra_variables = {"CMAKE_TRY_COMPILE_CONFIGURATION": str(self.settings_target.build_type)}
            if self.settings_target.os == "Windows":
                # Visual Studio generator: point the CUDA MSBuild integration to the libraries for the target architecture
                target_arch = "arm64" if self.settings_target.arch == "armv8" else "x64"
                extra_variables.update({
                    "CMAKE_TRY_COMPILE_PLATFORM_VARIABLES": "CMAKE_VS_GLOBALS",
                    "CMAKE_VS_GLOBALS": f"CudaToolkitLibDir=$ENV{{CUDAToolkit_ROOT}}/lib/{target_arch}",
                })
            self.conf_info.update("tools.cmake.cmaketoolchain:extra_variables", extra_variables)
