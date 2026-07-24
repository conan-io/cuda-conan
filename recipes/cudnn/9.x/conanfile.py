import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.scm import Version


required_conan_version = ">=2.31.0"


class CuDnnConan(ConanFile):
    name = "cudnn"
    package_type = "library"
    license = "Software License Agreement for NVIDIA cuDNN"
    url = "https://github.com/conan-io/cuda-conan"
    homepage = "https://developer.nvidia.com/cuda-toolkit"
    description = "NVIDIA cuDNN is a GPU-accelerated library of primitives for deep neural networks"
    topics = ("cuda", "cudnn", "nvidia", "deep-learning")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False]
    }
    default_options = {"shared": True}

    def requirements(self):
        # https://docs.nvidia.com/deeplearning/cudnn/backend/v9.24.0/reference/support-matrix.html
        # (We are assuming it remains compatible for future 13.x versions of CUDA)
        self.requires("cuda-toolkit/[>=12.0 <14.0]")
        
        if self.settings.os == "Linux":
            # https://docs.nvidia.com/deeplearning/cudnn/installation/latest/linux.html#installing-zlib
            self.requires("zlib/[>=1.3 <2]", options={"shared": True})

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def validate(self):
        if self.settings.os not in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Operating system not supported")
        
        if self.settings.os == "Windows" and not self.options.shared:
            raise ConanInvalidConfiguration("cuDNN on Windows is not available as a static library")

        if self.settings.os == "Linux" and self.dependencies["zlib"].package_type != "shared-library":
            raise ConanInvalidConfiguration("cuDNN requires zlib to be a shared library")
        
    def build(self):
        cuda_version_major = Version(self.dependencies["cuda-toolkit"].ref.version).major

        os = str(self.settings.os)
        arch = str(self.settings.arch)
        cuda = f"cuda-{cuda_version_major}"

        installer_url = self.conan_data['sources'][self.version][os][arch][cuda]['url']
        installer_sha256 = self.conan_data['sources'][self.version][os][arch][cuda]['sha256']

        self.output.info(f"Retrieving cuDNN installer from: {installer_url}")
        get(self, installer_url, sha256=installer_sha256, strip_root=True, destination="unpacked")

    def package(self):
        copy(self, "LICENSE", os.path.join(self.build_folder, "unpacked"), os.path.join(self.package_folder, "licenses"))
        for folder in ["include", "lib", "bin"]:
            copy(self, "*", os.path.join(self.build_folder, "unpacked", folder), os.path.join(self.package_folder, folder))

    def package_id(self):
        # We only want os, arch, and major cuda version in package_id
        # as all other variables dont affect the package contents
        self.info.requires["cuda-toolkit"].major_mode()
        self.info.settings.rm_safe("compiler")
        self.info.settings.rm_safe("build_type")
        del self.info.options.shared

    def package_info(self):
        self.cpp_info.ignored_requires = ["cuda-toolkit"]

        cudnn_version_major = str(Version(self.version).major)
        # Note: no official CMake config file but both pytorch and opencv use the following
        self.cpp_info.set_property("cmake_file_name", "CUDNN")
        self.cpp_info.bindirs = ["bin/x64" if self.settings.os == "Windows" else "bin"]

        if self.settings.os == "Windows":
            libdir = "lib/x64"
            suffix = f"64_{cudnn_version_major}" if self.options.shared else ""
        else:
            libdir = "lib"
            suffix = "_static" if not self.options.shared else ""
        self.cpp_info.libdirs = [libdir]
       
        # cuDNN components
        # https://docs.nvidia.com/deeplearning/cudnn/backend/v9.24.0/api/overview.html
        components = {
            "9": {
                "adv": ["ops", "graph"],
                "cnn": ["ops", "graph"],
                "ops": ["graph"],
                "engines_precompiled": ["graph"],
                "engines_runtime_compiled": ["graph"],
                "heuristic": ["graph"],
                "graph": []
            }
        }

        if self.settings.os == "Linux":
            components["9"]["graph"].append("zlib::zlib")

        prefix = "cudnn_"
        for component, deps in components[cudnn_version_major].items():
            # Reference: https://github.com/NVIDIA/cudnn-frontend/blob/develop/cmake/cuDNN.cmake
            self.cpp_info.components[component].libs = [f"{prefix}{component}{suffix}"]
            self.cpp_info.components[component].libdirs = [libdir]
            self.cpp_info.components[component].requires = deps
            self.cpp_info.components[component].set_property("cmake_target_name", f"CUDNN::{prefix}{component}")
            self.cpp_info.components[component].bindirs = ["bin/x64" if self.settings.os == "Windows" else "bin"]

        if self.options.shared:
            # Legacy shim layer - only available as a shared library
            self.cpp_info.components["cudnn"].libs = [f"cudnn{suffix}"]
            self.cpp_info.components["cudnn"].libdirs = [libdir]
            self.cpp_info.components["cudnn"].set_property("cmake_target_name", "CUDNN::cudnn")
            self.cpp_info.components["cudnn"].requires = list(components[cudnn_version_major].keys())
