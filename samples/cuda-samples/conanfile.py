from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get


class cuda_samplesRecipe(ConanFile):
    name = "cuda-samples"
    version = "13.2"
    package_type = "application"
    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        cuda_samples_url = "https://github.com/NVIDIA/cuda-samples/archive/refs/tags/v13.2update.tar.gz"
        cuda_samples_checksum = "057e68d22bd02e41d60c9826e7622ac1b88de0f1dbe25ed49bd995f768306f9d"
        get(self, cuda_samples_url, sha256=cuda_samples_checksum, strip_root=True)

    def requirements(self):
        self.requires("cuda-toolkit/[>=13 <14]")
        self.requires("opengl/system")
        self.requires("freeimage/[*]")

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
