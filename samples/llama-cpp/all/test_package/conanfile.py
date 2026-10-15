import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return
        if self.settings.os in ("Linux", "FreeBSD"):
            if self.dependencies["llama-cpp"].options.get_safe("with_cuda"):
                self.output.warning("Skipping the test run: the NVIDIA driver (libcuda.so.1) not available in CI")
                return
        bin_path = os.path.join(self.cpp.build.bindir, "test_package")
        self.run(bin_path, env="conanrun")
