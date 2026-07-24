import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.scm import Version

required_conan_version = ">=2.30"


class CuDssConan(ConanFile):
    name = "cudss"
    package_type = "library"
    license = "Software License Agreement for NVIDIA cuDSS"
    url = "https://github.com/conan-io/cuda-conan"
    homepage = "https://developer.nvidia.com/cudss"
    description = "NVIDIA cuDSS is a GPU-accelerated library for direct sparse solvers"
    topics = ("cuda", "cudss", "nvidia", "sparse")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False]
    }
    default_options = {"shared": True}

    def requirements(self):
        self.requires("cuda-toolkit/[>=12.0 <14]")

    def package_id(self):
        # We only want os, arch, and major cuda version in package_id
        # as all other variables dont affect the package contents
        self.info.requires["cuda-toolkit"].major_mode()
        self.info.settings.rm_safe("compiler")
        self.info.settings.rm_safe("build_type")
        del self.info.options.shared

    def build(self):
        cuda_version_major = Version(self.dependencies["cuda-toolkit"].ref.version).major
        cuda = f"cuda-{cuda_version_major}"
        os = str(self.settings.os)
        installer_url = self.conan_data['sources'][self.version][os]["x86_64"][cuda]['url']
        installer_sha256 = self.conan_data['sources'][self.version][os]["x86_64"][cuda]['sha256']

        self.output.info(f"Retrieving cuDSS installer from: {installer_url}")
        get(self, installer_url, sha256=installer_sha256, strip_root=True, destination="unpacked")

    def package(self):
        copy(self, "LICENSE", os.path.join(self.build_folder, "unpacked"), os.path.join(self.package_folder, "licenses"))
        for folder in ["include", "lib", "bin"]:
            copy(self, "*", os.path.join(self.build_folder, "unpacked", folder), os.path.join(self.package_folder, folder))

    def package_info(self):
        # Matches the official lib/cmake/cudss config shipped in the package:
        # find_package(cudss) provides plain (unnamespaced) targets "cudss" / "cudss_static"
        self.cpp_info.set_property("cmake_file_name", "cudss")
        self.cpp_info.libdirs = ["lib"]
        libname = "cudss" if self.options.shared else "cudss_static"
        self.cpp_info.libs = [libname]
        self.cpp_info.set_property("cmake_target_name", libname)
