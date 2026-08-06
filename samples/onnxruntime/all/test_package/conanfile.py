from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.files import copy
import os


# It will become the standard on Conan 2.x
class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self, src_folder=".")
        
    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["WITH_CUDA"] = self.dependencies["onnxruntime"].options.with_cuda
        tc.generate()
        if self.settings.os == "Windows":
            # on windows the system dll C:\WINDOWS\system32\onnxruntime.dll may be loaded instead even if the conan lib is first in the PATH, see https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order
            for bindir in self.dependencies[self.tested_reference_str].cpp_info.bindirs:
                copy(self, "*.dll", bindir, os.path.join(self.build_folder, self.cpp.build.bindir))

        if self.settings.os == "Linux" and not self.dependencies["onnxruntime"].options.shared:
            # the providers are always dlopend() - when the library is static,
            # onnxruntime attempts to load them from the same directory as the executable
            # not needed when it is shared (they are loaded relative to the shared library)
            for libdir in self.dependencies[self.tested_reference_str].cpp_info.libdirs:
                self.output.info(f"Copying shared libraries from {libdir} to {self.build_folder}")
                copy(self, "*.so*", libdir, self.build_folder)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
