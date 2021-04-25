from re import sub
from typing import Union

import sys, os, subprocess, argparse, json

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
            
        # Save MCT Settings:
        
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


class SavePackageListCommand(CommandBase):
    cmd: str = "vcpkg-save-pkg-list"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Saves a list of vcpkg the currently installed vcpkg packages."
    )

    def setup_args(self):
        self.argparser.add_argument(
            "-f",
            "--filename",
            default="vcpkg-lists.json"
        )

    def process(self, args: argparse.Namespace):
        vcpkg_ready, vcpkg_path = vcpkg.ready_check()
        
        if not vcpkg_ready:
            return 1
        
        list_result = subprocess.check_output([vcpkg_path, "list"], cwd=settings.current['vcpkg']['path']).decode('ascii')
        # print (list_result)
        pkg_list = vcpkg.jsonize_lists(vcpkg.parse_package_list(list_result))
        # print(pkg_list)
        
        outfile = open(args.filename, "w")
        json.dump(pkg_list, outfile, indent=4, sort_keys=True)
        outfile.close()

        return None
    
class LoadPackageListCommand(CommandBase):
    cmd: str = "vcpkg-load-pkg-list"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Loads and installs vcpkg packages from a vcpkg-list.json file."
    )

    def setup_args(self):
        self.argparser.add_argument(
            "-f",
            "--filename",
            default="vcpkg-lists.json"
        )
        self.argparser.add_argument(
            "-t",
            "--triplets",
            default="",
            help="Sets the triplets to use for the installation of each list. "
            "List of triplets should be separated with ':'. Blanks will install "
            "default triplet for your system. Use '_original' for the original "
            "triplet the list was gernerated with."
        )


    def process(self, args: argparse.Namespace):
        vcpkg_ready, vcpkg_path = vcpkg.ready_check()
        
        if not vcpkg_ready:
            return 1
        
        triplet_list = args.triplets.split(":")
        
        infile = open(args.filename, "r")
        pkg_list = vcpkg.dejsonize_lists(json.load(infile))
        infile.close()

        
        for i in range(0, len(pkg_list)):
            install_args = []
            
            if i >= len(triplet_list):
                install_args = pkg_list[i].get_install_args()
            else:
                install_args = pkg_list[i].get_install_args(triplet_list[i])
        
            install_result = subprocess.run([vcpkg_path, "install"] + install_args, cwd=settings.current['vcpkg']['path'])
            
            if install_result.returncode != 0:
                return install_result
                
        return None