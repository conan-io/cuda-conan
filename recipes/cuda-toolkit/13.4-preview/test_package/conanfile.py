import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout


class CudatoolkitTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires(self.tested_reference_str)
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self, src_folder='.')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_CUDA_ARCHITECTURES"] = "87-real"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "example")
            self.run(bin_path, env="conanrun")
