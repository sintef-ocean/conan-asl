from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches, copy, export_conandata_patches, get,
    mkdir, rm, rmdir
    )
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.system.package_manager import Apt
import os

required_conan_version = ">=2.0.9"


class PackageConan(ConanFile):
    name = "asl"
    description = "AMPL Solver Library"
    license = ["BSD-3-Clause", "SMLNJ"]
    url = "https://github.com/sintef-ocean/conan-asl"
    homepage = "https://github.com/ampl/asl"
    topics = ("asl", "ampl")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_64bit_int": [True, False],
        "with_cpp": [True, False],
        "with_openmp": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_64bit_int": False,
        "with_cpp": False,
        "with_openmp": False
    }
    implements = ["auto_shared_fpic"]

    def _msvc_dynamic_runtime(self):
        return is_msvc(self) and not is_msvc_static_runtime(self)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_openmp and not self.settings.os == "Windows":
            if not self.settings.compiler == "gcc":
                self.requires("llvm-openmp/20.1.6")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def validate(self):
        if self.options.shared and self.options.with_cpp:
            raise ConanInvalidConfiguration(
                "asl cannot be built with shared when `with_cpp=True`")

    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables["BUILD_DYNRT_LIBS"] = self._msvc_dynamic_runtime()
        tc.cache_variables["BUILD_MCMODELLARGE"] = False
        tc.cache_variables["BUILD_MT_LIBS"] = self.options.with_openmp
        tc.cache_variables["BUILD_CPP"] = self.options.with_cpp
        tc.cache_variables["BUILD_F2C"] = False
        tc.cache_variables["BUILD_ASL_EXAMPLES"] = False
        tc.cache_variables["BUILD_LICCHECK_PRINT"] = False
        tc.generate()

        if self.options.with_64bit_int:
            tc.preprocessor_definitions["ASL_big_goff"] = "1"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.2", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows":
            mkdir(self, os.path.join(self.package_folder, "bin"))
            copy(self, "*.dll", os.path.join(self.package_folder, "lib"),
                 os.path.join(self.package_folder, "bin"))
            rm(self, "*.dll", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ampl-asl")

        libs = ["asl", "asl2"]
        if self.options.with_openmp:
            libs.extend(["asl-mt", "asl2-mt"])

        self.cpp_info.components["asl"].set_property("cmake_target_name", "asl")
        self.cpp_info.components["asl"].libs = ["asl"]

        self.cpp_info.components["asl2"].set_property("cmake_target_name", "asl2")
        self.cpp_info.components["asl2"].libs = ["asl2"]

        if self.options.with_cpp:
            self.cpp_info.components["aslcpp"].set_property("cmake_target_name", "aslcpp")
            self.cpp_info.components["aslcpp"].libs = ["aslcpp"]
            self.cpp_info.components["aslcpp"].requires = ["asl"]

        if self._msvc_dynamic_runtime():
            rtlibs = ["asl-dynrt", "asl2-dynrt"]
            for rtlib in rtlibs:
                self.cpp_info.components[rtlib].set_property("cmake_target_name", rtlib)
                self.cpp_info.components[rtlib].libs = [rtlib]
                self.cpp_info.components[rtlib].defines.append("NO_MBLK_LOCK")

        if self.options.with_openmp:
            mtlibs = ["asl-mt", "asl2-mt"]
            for mtlib in mtlibs:
                self.cpp_info.components[mtlib].set_property("cmake_target_name", mtlib)
                self.cpp_info.components[mtlib].libs = [mtlib]
                self.cpp_info.components[mtlib].defines.append("ALLOW_OPENMP")
                if self.settings.compiler == "gcc":
                    self.cpp_info.components[mtlib].system_libs.extend(["gomp"])
                elif not self.settings.os == "Windows":
                    self.cpp_info.components[mtlib].requires.append("llvm-openmp::llvm-openmp")

        for lib in libs:
            defs = ["No_Control87"]
            if self.options.with_64bit_int:
                defs.append("ASL_big_goff=1")
            self.cpp_info.components[lib].defines.extend(defs)

        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.with_cpp:
                libs.append("aslcpp")
            for lib in libs:
                self.cpp_info.components[lib].system_libs.extend(["m", "dl"])

    def system_requirements(self):
        if self.options.with_openmp and not self.settings.compiler == "gcc":
            Apt(self).install(["libgomp1"])
