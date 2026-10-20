import os
import json
from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, download, get, load, rename, replace_in_file

class CudaToolkitConan(ConanFile):
    name = "cuda-toolkit"
    package_type = "shared-library"
    version = "12.9.2"
    license = "CUDA Toolkit End-User License Agreement"
    url = "https://github.com/conan-io/cuda-conan"
    homepage = "https://developer.nvidia.com/cuda-toolkit"
    description = "A development environment for creating high performance GPU-accelerated applications"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        # Linux armv8 only: SBSA (Arm servers) vs Jetson/Tegra (linux-aarch64)
        "arm_target": ["sbsa", "jetson"],
    }
    default_options = {
        "arm_target": "sbsa",
    }

    def config_options(self):
        if self.settings.os != "Linux" or self.settings.arch != "armv8":
            del self.options.arm_target

    def validate(self):
        if self.settings.os not in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Operating system not supported")

        # CUDA 12.9 redistributables: linux-x86_64, linux-sbsa, linux-aarch64, windows-x86_64
        supported_archs = ["x86_64", "armv8"] if self.settings.os == "Linux" else ["x86_64"]
        if self.settings.arch not in supported_archs:
            raise ConanInvalidConfiguration(f"{self.settings.arch} is not supported on {self.settings.os}")

        # TODO: Add checks for supported compilers as per https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#id56

    def _cuda_platform(self):
        if self.settings.os == "Linux" and self.settings.arch == "armv8":
            return "linux-aarch64" if self.options.arm_target == "jetson" else "linux-sbsa"
        return f"{str(self.settings.os).lower()}-{self.settings.arch}"

    def _targets_arch(self):
        if self.settings.os == "Linux" and self.settings.arch == "armv8":
            return "aarch64" if self.options.arm_target == "jetson" else "sbsa"
        return str(self.settings.arch)

    def build(self):
        base_url = "https://developer.download.nvidia.com/compute/cuda/redist"
        distrib = f"redistrib_{self.version}.json"
        json_distrib = f"{base_url}/{distrib}"
        download(self, url=json_distrib, filename=distrib)
        json_content = load(self, distrib)
        cuda_distrib = json.loads(json_content)

        cuda_platform = self._cuda_platform()
        self.output.info(f"About to download CUDA toolkit components for {cuda_platform}")

        components = [
            "cuda_cccl",
            "cuda_cudart",
            "cuda_cupti",
            "cuda_cuxxfilt",
            "cuda_nvcc",
            "cuda_nvml_dev",
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
        ]

        platform_components = {
            "linux-x86_64": ["libcufile", "cuda_sandbox_dev", "cuda_opencl"],
            "linux-sbsa": ["libcufile"],
            "linux-aarch64": ["libcufile", "cuda_compat", "libcudla"],
            "windows-x86_64": ["cuda_opencl", "visual_studio_integration"],
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

    def package(self):
        copy(self, "LICENSE*", src=self.build_folder, dst=os.path.join(self.package_folder, "licenses"))

        for folder in ["bin", "nvml", "nvvm", "compat"]:
            copy(self, "*", src=os.path.join(self.build_folder, "cuda", folder), dst=os.path.join(self.package_folder, folder))

        if self.settings.os == "Linux":
            arch = self._targets_arch()
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
        # only os, arch, and arm_target (when set) matter for this package
        self.info.settings.rm_safe("compiler")
        self.info.settings.rm_safe("build_type")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CUDAToolkit") # what consumers will expect
        self.cpp_info.set_property("cmake_find_mode", "none") # but don't generate it
        self.cpp_info.set_property("cmake_target_name", "CUDA::toolkit")

        nvcc = "nvcc.exe" if self.settings.os == "Windows" else "nvcc"
        self.buildenv_info.define_path("CUDACXX", os.path.join(self.package_folder, "bin", nvcc))

        if not self.settings_target:
            arch = self._targets_arch() if self.settings.os == "Linux" else str(self.settings.arch)
            self.buildenv_info.define_path("CUDAToolkit_ROOT", self.package_folder)
            if self.settings.os == "Linux":
                self.buildenv_info.define_path("CONAN_CUDA_TARGET_DIR", os.path.join(self.package_folder, "targets", f"{arch}-linux"))

        if self.settings.os == "Linux":
            self.cpp_info.libdirs = ["lib64"]
        else:
            self.cpp_info.libdirs = ["lib", "lib/x64"]

        if self.settings_build.os == "Windows":
            # Only has effect when Windows and the CMake generator is Visual Studio
            package_folder = f"{self.package_folder}".replace('\\', '/')
            self.conf_info.define("tools.cmake.cmaketoolchain:toolset_cuda", package_folder)

        if self.settings_target and self.settings_target.get_safe("build_type"):
            self.conf_info.update("tools.cmake.cmaketoolchain:extra_variables",
                                    {"CMAKE_TRY_COMPILE_CONFIGURATION": str(self.settings_target.build_type)})
