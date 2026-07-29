import os
import xml.etree.ElementTree as ET

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, download, replace_in_file


required_conan_version = ">=2.1.0"


class CudaToolkitConan(ConanFile):
    name = "cuda-toolkit"
    package_type = "shared-library"
    license = "CUDA Toolkit End-User License Agreement"
    url = "https://github.com/conan-io/cuda-conan"
    homepage = "https://developer.nvidia.com/cuda-toolkit"
    description = "A development environment for creating high performance GPU-accelerated applications"
    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only Windows supported, this is a proof of concept for Windows arm64 support based on 13.4.0 developer preview")

    def requirements(self):
        if self.settings_build.os == "Windows":
            self.tool_requires("7zip/[*]")

    def build(self):
        os = str(self.settings.os)
        arch = str(self.settings.arch)

        installer_url = self.conan_data['sources'][self.version][os][arch]['url']
        installer_md5 = self.conan_data['sources'][self.version][os][arch]['md5']
        installer_sha256 = self.conan_data['sources'][self.version][os][arch]['sha256']

        self.output.info(f'Cuda installer URL: {installer_url}')
        installer_filename = "installer"
        download(self, installer_url, installer_filename, md5=installer_md5, sha256=installer_sha256)

        self.run(f"7z x {installer_filename} -o{self.build_folder}")

        # When cross-building, get nvcc to locate libraries in host package
        replace_in_file(
            self,
            "cuda_nvcc/nvcc/bin/nvcc.profile",
            'LIBRARIES        =+ $(_SPACE_) "/LIBPATH:$(TOP)/lib/$(_WIN_PLATFORM_)"',
            'CONAN_CUDA_LIB_DIR ?= $(TOP)/lib/$(_WIN_PLATFORM_)\n'
            'LIBRARIES        =+ $(_SPACE_) "/LIBPATH:$(CONAN_CUDA_LIB_DIR)"',
        )

    def package(self):
        components = [
            "cccl/cccl/cccl.nvi",
            "cuda_crt/crt/crt.nvi",
            "cuda_cudart/cudart/cudart.nvi",
            "cuda_cuobjdump/cuobjdump/cuobjdump.nvi",
            "cuda_cupti/cupti/cupti.nvi",
            "cuda_cuxxfilt/cuxxfilt/cuxxfilt.nvi",
            "cuda_nvcc/nvcc/nvcc.nvi",
            "cuda_nvdisasm/nvdisasm/nvdisasm.nvi",
            "cuda_nvml_dev/nvml_dev/nvml_dev.nvi",
            "cuda_nvprune/nvprune/nvprune.nvi",
            "cuda_nvrtc/nvrtc_dev/nvrtc_dev.nvi",
            "cuda_nvrtc/nvrtc/nvrtc.nvi",
            "cuda_nvtx/nvtx/nvtx.nvi",
            "cuda_opencl/opencl/opencl.nvi",
            "cuda_profiler_api/cuda_profiler_api/cuda_profiler_api.nvi",
            "cuda_sanitizer_api/sanitizer/sanitizer.nvi",
            "cuda_tileiras/tileiras/tileiras.nvi",
            "CUDAToolkit/CUDAToolkit.nvi",
            "libcublas/cublas_dev/cublas_dev.nvi",
            "libcublas/cublas/cublas.nvi",
            "libcufft/cufft_dev/cufft_dev.nvi",
            "libcufft/cufft/cufft.nvi",
            "libcurand/curand_dev/curand_dev.nvi",
            "libcurand/curand/curand.nvi",
            "libcusolver/cusolver_dev/cusolver_dev.nvi",
            "libcusolver/cusolver/cusolver.nvi",
            "libcusparse/cusparse_dev/cusparse_dev.nvi",
            "libcusparse/cusparse/cusparse.nvi",
            "libnpp/npp_dev/npp_dev.nvi",
            "libnpp/npp/npp.nvi",
            "libnvjitlink/nvjitlink/nvjitlink.nvi",
            "libnvjpeg/nvjpeg_dev/nvjpeg_dev.nvi",
            "libnvjpeg/nvjpeg/nvjpeg.nvi",
            "libnvfatbin/nvfatbin/nvfatbin.nvi",
            "libnvptxcompiler/libnvptxcompiler/libnvptxcompiler.nvi",
            "libnvvm/nvvm/nvvm.nvi",
            "visual_studio_integration/CUDAVisualStudioIntegration/CUDAVisualStudioIntegration.nvi"
        ]

        if self.settings.arch == "armv8":
            components.append("libcudla/cudla/cudla.nvi")

        for nvi_file in components:
            source_folder = os.path.dirname(nvi_file)
            self.output.info(f"Component folder: {source_folder}")
            full_nvi_file = f"{self.build_folder}/{nvi_file}"

            tree = ET.parse(full_nvi_file).getroot()

            for x in tree.findall("phases/standard[@phase='copyFiles']/copyFile"):
                if 'source' in x.attrib:
                    continue

                target = x.attrib['target']
                rel_dir = os.path.dirname(target)
                filename = os.path.basename(target)

                src = os.path.join(self.build_folder, source_folder, rel_dir)
                dest = os.path.join(self.package_folder, rel_dir)
                copy(self, filename, src, dest, keep_path=False)

    def package_id(self):
        self.info.settings.rm_safe("compiler")
        self.info.settings.rm_safe("build_type")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CUDAToolkit") # what consumers will expect
        self.cpp_info.set_property("cmake_find_mode", "none") # but don't generate it
        self.cpp_info.set_property("cmake_target_name", "CUDA::toolkit")

        self.buildenv_info.define_path("CUDACXX", os.path.join(self.package_folder, "bin", "nvcc.exe"))

        arch = "arm64" if self.settings.arch == "armv8" else "x64"
        if not self.settings_target:
            self.buildenv_info.define_path("CUDAToolkit_ROOT", self.package_folder)
            self.buildenv_info.define_path("CONAN_CUDA_LIB_DIR", os.path.join(self.package_folder, "lib", arch).replace("\\", "/"))
       
        self.cpp_info.libdirs = [f"lib/{arch}", f"nvvm/lib/{arch}"]
        self.cpp_info.bindirs = ["bin", f"bin/{arch}", "nvvm/lib"]

        # The following only effect CMake generator is Visual Studio
        package_folder = f"{self.package_folder}".replace('\\', '/')
        self.conf_info.define("tools.cmake.cmaketoolchain:toolset_cuda", package_folder)

        if self.settings_target and self.settings_target.get_safe("build_type"):
            arch = "arm64" if self.settings_target.arch == "armv8" else "x64"
            self.conf_info.update("tools.cmake.cmaketoolchain:extra_variables",
                                    {"CMAKE_TRY_COMPILE_CONFIGURATION": str(self.settings_target.build_type),
                                     "CMAKE_TRY_COMPILE_PLATFORM_VARIABLES": "CMAKE_VS_GLOBALS",
                                     "CMAKE_VS_GLOBALS": f"CudaToolkitLibDir=$ENV{{CUDAToolkit_ROOT}}/lib/{arch}"})
        
