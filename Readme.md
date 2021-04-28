# MCT: Modern CPP Toolchain

VCPKG integration and project bootstrapping for CMAKE, for better collaboration and cross-platform support.

## About

MCT aims to simplify the process of cross-platform dependency management in future C/C++ projects by providing VCPKG integration for CMAKE:

MCT does this by:

* Providing an easy mechanism to integrate VCPKG into new CMAKE projects.
* Easily setting up and managing a local copy of VCPKG for a given project, seperate from the global environment. Similar in function to Python's virtualenv system or Nodejs' local vs. global packages.
* Generating and managing the CMAKE presets (a feature recently added to CMake) and toolchain files required for VCPKG integration. To aid in collaboration and cross-platform development, these presets are generated locally for the current user/system and desired VCPKG triplet, instead of needing to be stored in version control.
* Allows certain project configuration values and CMAKE variables to be specified on the user end, to mitigate situations where a user cannot compile a project without changing a version-controlled file.

## Requirements

You need to have the requirements for VCPKG on your system, and Git is required to actually install and manage instances of VCPKG.

In the name of cross-platform compatibility, MCT favors using Ninja as the default generator and build system.

At this time, MCT never actually invokes CMake itself. Therefore, CMake isn't actually required for MCT to work (not sure how that's useful to anyone, though).

## Installation

If using a packaged release version, just extract to a folder and add that folder to you PATH. Then run `mct g install-vcpkg` to install the global VCPKG instance.

## Usage

* [Quickstart Guide](doc/quickstart/quickstart.md)

See the documentation folder.
