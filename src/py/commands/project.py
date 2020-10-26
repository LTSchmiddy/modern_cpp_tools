from re import sub
from typing import Union

import sys, os, subprocess, argparse

from util import *
from colors import *
import settings
from settings import get_exec_path, get_exec_path_fslashed

from tools import vcpkg, cmake_presets

from commands import CommandBase


class SetupProjectCommand(CommandBase):
    cmd: str = "setup"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Setup a MCCPT project for local usage."
    )

    def setup_args(self):
        self.argparser.add_argument(
            "-p",
            "--path",
            default=os.getcwd()
        )

        self.argparser.add_argument(
            "-f",
            "--force",
            action='store_true'
        )

    def process(self, args: argparse.Namespace):
        mkdir_if_missing(args.path)

        is_local, l_path, l_set = settings.local_project_check(args.path)
        if is_local and not args.force:
                return "This path is already a mpcct project."
            
        # Save MCPPT Settings:
        
        settings.local_settings_path = os.path.join(args.path, settings.local_file_name)
        settings.save_settings(settings.local_settings_path, settings.current)
        settings.project_dir = args.path
        settings.is_local_project = True

        # settings.update_local_status(args.path) # Should be considered a local project from here on...

        # cmake_presets.update_project_toolchain_file()
        cmake_presets.update_project_toolchain_file(root_dir=args.path)

        # Handle CMakePresets.json. Do nothing if file is already present.
        cmake_presets_path = os.path.join(args.path, "CMakePresets.json")
        if not os.path.isfile(cmake_presets_path):
            settings.save_settings(cmake_presets_path, cmake_presets.default_preset_file())
        
        # Handle CMakeUserPresets.json. As this file should not be added to repositories, we will overwrite any if found.
        cmake_user_presets_path = os.path.join(args.path, "CMakeUserPresets.json")

        user_presets = cmake_presets.make_user_preset_file(cmake_presets.get_custom_toolchain_path(args.path))

        settings.save_settings(cmake_user_presets_path, user_presets)


class AddTripletCommand(CommandBase):
    cmd: str = "add-triplet"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Adds presets for a vcpkg triplet"
    )

    def setup_args(self):
        self.argparser.add_argument('triplet')
        self.argparser.add_argument(
            '-c',
            "--config",
            default=""
        )

    def process(self, args: argparse.Namespace):
        user_presets_path = get_exec_path("CMakeUserPresets.json")
        if settings.is_local_project and os.path.isfile(user_presets_path):
            user_presets = {}
            settings.load_settings(user_presets_path, user_presets)

            cmake_presets.add_triplet(user_presets, args.triplet, args.config)

            settings.save_settings(user_presets_path, user_presets)
        else:
            return "CMake Project not found."
        
        return None


        # user_presets["configurePresets"].append(cmake_presets.make_user_preset("x64-windows", "debug"))
