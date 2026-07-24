import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


required_conan_version = ">=2.1.0"


class CudnnFrontendConan(ConanFile):
    name = "cudnn-frontend"
    description = (
        "cuDNN Frontend is NVIDIA's modern, header-only C++ API on top of the "
        "cuDNN C backend, providing higher-level graph and operation abstractions."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NVIDIA/cudnn-frontend"
    topics = ("cudnn", "cuda", "nvidia", "deep-learning", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # The frontend headers transitively include cudnn.h and CUDA runtime
        # headers, so consumers always need both at compile time.
        self.requires("cudnn/[>=9.24 <10]", transitive_headers=True)
        self.requires("cuda-toolkit/[>=12 <=14]", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.txt",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h",
             src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.hpp",
             src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        # Match upstream's CMake find_package name and target name.
        self.cpp_info.set_property("cmake_file_name", "cudnn_frontend")
        self.cpp_info.set_property("cmake_target_name", "cudnn_frontend")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
