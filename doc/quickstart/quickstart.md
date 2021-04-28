# Quickstart Guide

The `mct setup` command is used to create new projects, and to setup pre-existing ones for local work.

## Starting a new project with MCT:

When the `mct setup` command is used, it will generate several files.

These files (I call them "user files") are specific to your instance of the project, and should NOT be added to version control:

* `CMakeUserPresets.json`: This file contains CMake presets specific to your copy of the project, based on your system and triplet selection.
* `mct_user_settings.json`: Contains various settings and configuration info for your instance of the project. Initially, it will just be a copy of your global settings. This is the file that MCT uses to identify the project and its root folder.
* `mct_user_toolchain.cmake`: This is the toolchain file that CMake will actually use, as set in `CMakeUserPresets.json`. It is automatically generated to include toolchain of your VCPKG instance and to set a handful of other values. This file is subject to overwrites, and thus any changes made here will not be saved. Instead, you can specify additional toolchain files to include in both `mct_project_info.json` and `mct_user_settings.json`.

MCT can also generates a couple of files that are common to the project as a whole. If the following files are not found, MCT will create the default versions and continue.

* `CMakePresets.json`: This file contains the main, default CMake preset that all other presets will inherit from. This file is meant to be shared among users, and can be added to version control.
* `mct_project_info.json`: This is the common, shared information for the MCT project.

## Loading an MCT project

Before you can work on a pre-existing MCT project, you still need to generate the user files for your instance of a project, so you need to run the `mct setup` command to generate them.

If MCT finds `mct_project_info.json` or `CMakePresets.json` in the project root, it will use the pre-existing copies of those files instead of generating new ones. If the project has custom CMake values that the user needs to set locally in `mct_user_settings.json`, MCT will prompt them at this time.

## Global vs. Local behavior

You might have noticed that when running an MCT command, you'll see a message specifying whether MCT is running on global or local mode.

Running a command in local mode means that the operation will only affect that project, and only use the project's local settings. This mode is the default if `mct_user_settings.json` is found in the current working directory or any of its parent directories.

Running a command in global mode means that the operation will effect the MCT installation as a whole, ususally in reference to the global VCPKG instance and the global settings. Of course, not all commands are actually relevant to global mode. This mode is the default if `mct_user_settings.json` is not found, or the `g` modifier is used before the command name (ex: `mct g install-vcpkg`).

## Setting the VCPKG Instance

By default, the user files will specify that CMake use MCT's global copy of VCPKG. But perhaps you don't want to install this project's dependencies globally. It's often better to install those dependencies in the project folder itself, as to avoid conflicts and compatibility issues (similar to Python's `virtualenv` or Nodejs' `node_modules` folder).

The command `mct install-vcpkg` will install and bootstrap a fresh copy of VCPKG into the project's root folder. All of your user files will then be updated to use this version of VCPKG instead of the global one.

MCT provides an easy way to use these different VCPKG instances, without having to navigate to the directory for the local (or worse, the global) VCPKG instance and invoke the `vcpkg` executable there. When running inside a local project, the `mct vcpkg ...` command will invoke the correct VCPKG instance for that project, forwarding any additional argument to the `vcpkg` process. When in global mode, `mct vcpkg ...` will simply use the global VCPKG instance instead.

## VCPKG Triplet Presets

Before CMake can use any of the packages that VCPKG provides, you'll need to specify the triplet that VCPKG built your packages with. Use the `mct add-triplet [-c=CONFIG_TYPE] TRIPLET` command to automatically generate a CMake preset in `CMakeUserPresets.json` for the triplet `TRIPLET`. Additionally, the optional `c` flag can be used to set the configuration type (Debug, Release, etc.) of the preset.

Each preset will automatically be assigned it's own build folder in the `build` subdirectory (which will be created if it does not already exist).

MCT tries to be as unintrusive as possible when editing `CMakeUserPresets.json`, and currently doesn't make any changes to `CMakePresets.json` after it's creation. Therefore, you're welcome to modify these files to your liking, as long as you don't rename the two default presets.

---

## TBC