[![Linux GCC](https://github.com/sintef-ocean/conan-asl/workflows/Linux%20GCC/badge.svg)](https://github.com/sintef-ocean/conan-asl/actions?query=workflow%3A"Linux+GCC")

[Conan.io](https://conan.io) recipe for [AMPL ASL](https://github.com/ampl/asl).

## How to use this package

1. Add remote to conan's package [remotes](https://docs.conan.io/2/reference/commands/remote.html)

   ```bash
   $ conan remote add sintef https://package.smd.sintef.no
   ```

2. Using [*conanfile.txt*](https://docs.conan.io/2/reference/conanfile_txt.html) and *cmake* in your project.

   Add *conanfile.txt*:
   ```
   [requires]
   asl/1.0.1@sintef/stable

   [tool_requires]
   cmake/[>=3.25.0 <4]

   [options]

   [layout]
   cmake_layout

   [generators]
   CMakeDeps
   CMakeToolchain
   VirtualBuildEnv
   ```
   Insert into your *CMakeLists.txt* something like the following lines:
   ```cmake
   cmake_minimum_required(VERSION 3.15)
   project(TheProject CXX)

   find_package(asl REQUIRED COMPONENTS asl asl2)

   add_executable(the_executor code.cpp)
   target_link_libraries(the_executor asl2)
   ```
   Install and build e.g. a Release configuration:
   ```bash
   $ conan install . -s build_type=Release -pr:b=default
   $ source build/Release/generators/conanbuild.sh
   $ cmake --preset conan-release
   $ cmake --build build/Release
   $ source build/Release/generators/deactivate_conanbuild.sh
   ```

## Package options

Option | Default | Domain
---|---|---
shared  | False | [True, False]
fPIC | True | [True, False]
with_64bit_int | False | [True, False]
with_cpp | False | [True, False]
with_openmp | False | [True, False]

## Known recipe issues

  - This recipe does not yet build mumps on Windows
  - `with_cpp=True` is only available for static builds
