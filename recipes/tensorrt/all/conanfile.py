import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.scm import Version

required_conan_version = ">=2.30"


class TensorRTConan(ConanFile):
    name = "tensorrt"
    package_type = "library"
    license = "DocumentRef-LICENSE:LicenseRef-tensorrt"
    url = "https://github.com/conan-io/cuda-conan"
    homepage = "https://developer.nvidia.com/tensorrt"
    description = (
        "NVIDIA TensorRT is an SDK for high-performance deep learning inference. "
        "It includes a deep learning inference optimizer and runtime."
    )
    topics = ("cuda", "tensorrt", "nvidia", "deep-learning", "inference")
    settings = "os", "arch"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }

    def config_options(self):
        if Version(self.version) >= "11":
            # From v11, tensorrt is packaged as a shared library
            self.package_type = "shared-library"
            del self.options.shared

    def requirements(self):
        self.requires("cuda-toolkit/[>=12.0 <14]", transitive_headers=True)

    def package_id(self):
        self.info.requires["cuda-toolkit"].major_mode()

    def validate(self):
        if self.settings.os not in ("Windows", "Linux"):
            raise ConanInvalidConfiguration("TensorRT is only available for Windows and Linux.")
        if self.settings.os == "Windows" and self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("TensorRT is only available for x86_64 on Windows")
        if self.settings.os == "Linux" and self.settings.arch not in ("x86_64", "armv8"):
            raise ConanInvalidConfiguration("TensorRT is only available for x86_64 and armv8 on Linux")

    def build(self):
        os = str(self.settings.os)
        arch = str(self.settings.arch)
        for dep in self.dependencies.values():
            if dep.ref.name == "cuda-toolkit":
                cuda_major = Version(dep.ref.version).major
                break
        get(self, **self.conan_data['sources'][self.version][os][arch][f"cuda-{cuda_major}"],
            strip_root=True, destination=self.source_folder)

    def package(self):
        copy(self, "Acknowledgements.txt", os.path.join(self.source_folder, "doc"), os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
        if self.settings.os == "Linux":
            copy(self, "*.so*" if self.package_type == "shared-library" else "*.a", os.path.join(self.source_folder, "lib"), os.path.join(self.package_folder, "lib"))
        if self.settings.os == "Windows":
            copy(self, "*", os.path.join(self.source_folder, "lib"), os.path.join(self.package_folder, "lib"))
            copy(self, "*.dll", os.path.join(self.source_folder, "bin"), os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TensorRT")
        self.cpp_info.set_property("cmake_extra_dependencies", ["CUDAToolkit"])

        static_suffix =  "" if self.package_type == "shared-library" else "_static"
        windows_suffix = f"_{Version(self.version).major}" if self.settings.os == "Windows" else ""
        # nvinfer_static.a needs the JIT-linker and PTX compiler to build kernels at runtime;
        # the shared nvinfer.so already links them in via its own DT_NEEDED entries.
        nvinfer_cuda_libs = ["CUDA::cudart", "CUDA::nvrtc"]
        if self.package_type == "static-library":
            # CMake's FindCUDAToolkit processes nvJitLink_static before nvptxcompiler_static
            # exists, so it never wires that dependency itself: add it explicitly here.
            nvinfer_cuda_libs.extend(["CUDA::nvJitLink_static", "CUDA::nvptxcompiler_static"])
        components = {
            "nvinfer": {"requires": [], "cuda_libs": nvinfer_cuda_libs},
            "nvinfer_plugin": {"requires": ["nvinfer"], "cuda_libs": []},
            "nvinfer_lean": {"requires": [], "cuda_libs": ["CUDA::cudart"]},
            "nvinfer_dispatch": {"requires": [], "cuda_libs": ["CUDA::cudart"]},
            "nvinfer_vc_plugin": {"requires": [], "cuda_libs": []},
            "nvonnxparser": {"requires": ["nvinfer"], "cuda_libs": []},
        }
        for component, info in components.items():
            self.cpp_info.components[component].libs = [f"{component}{static_suffix}{windows_suffix}"]
            self.cpp_info.components[component].requires = info["requires"]
            self.cpp_info.components[component].set_property("cmake_target_name", f"TensorRT::{component}")
            if info["cuda_libs"]:
                self.cpp_info.components[component].set_property("cmake_extra_interface_libs", info["cuda_libs"])
