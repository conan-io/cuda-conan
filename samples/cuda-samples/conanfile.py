import os
import platform

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, patch, rename


class cuda_samplesRecipe(ConanFile):
    name = "cuda-samples"
    version = "13.2"
    package_type = "application"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "patches/*.patch"

    def source(self):
        cuda_samples_url = "https://github.com/NVIDIA/cuda-samples/archive/refs/tags/v13.2update.tar.gz"
        cuda_samples_checksum = "057e68d22bd02e41d60c9826e7622ac1b88de0f1dbe25ed49bd995f768306f9d"
        get(self, cuda_samples_url, sha256=cuda_samples_checksum, strip_root=True)
        if platform.system() == "Windows":
            # Note: conditional patches are not good practice, but this isn't a
            # packaged recipe. need a more robust approach.
            for patch_file in ["13.2-windows-fixes.patch", "13.2-windows-fixes-arm64.patch"]:
                patch(self, patch_file=os.path.join(self.export_sources_folder, "patches", patch_file))
            # Rename the GL folder and use these from Conan
            rename(self, 
               os.path.join(self.source_folder, "Common", "GL"),
               os.path.join(self.source_folder, "Common", "GL__"))

    def requirements(self):
        self.requires("cuda-toolkit/[>=13 <14]")
        self.requires("opengl/system")
        self.requires("freeimage/[*]")
        if self.settings.os == "Windows":
            # cuda-samples uses vendored glew binaries that are x86_64 only
            # lets use them from Conan on Windows to support Windows arm64 too
            self.requires("glew/[*]")
            self.requires("freeglut/[*]")

    def build_requirements(self):
        self.tool_requires("cuda-toolkit/<host_version>")
        self.tool_requires("cmake/[*]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.set_property("freeimage", "cmake_file_name", "FreeImage")
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
