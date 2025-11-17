from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            components = ["asl", "asl2", "asl-mt", "asl2-mt", "asl-dynrt", "asl2-dynrt"]
            for comp in components:
                bin_path = os.path.join(self.cpp.build.bindir, f"test_package_{comp}")
                if os.path.exists(bin_path):
                    self.run(bin_path, env="conanrun")
                else:
                    self.output.info(f"Skipping missing component {comp}")
