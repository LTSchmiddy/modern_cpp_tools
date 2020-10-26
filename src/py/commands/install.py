from re import sub
from typing import Union

import sys, os, subprocess, argparse

from util import *
from colors import *
import settings
from settings import get_exec_path, get_exec_path_fslashed

from tools import vcpkg, cmake_presets

from commands import CommandBase


class InstallVcpkgCommand(CommandBase):
    cmd: str = "install-vcpkg"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Install and setup vcpkg directory."
    )

    def setup_args(self):
        pass

    def process(self, args: argparse.Namespace):
        if settings.current["common"]["has_been_installed"]:
            print_warning(
                "WARNING: Apparently, installation has been run before. Installation might behave unpredictably..."
            )
        else:
            print("Running vcpkg installation...")

        # Installing vcpkg
        if settings.current["vcpkg"]["use_external"]:
            print("Using external copy of vcpkg. Skipping installation of local version...")
        else:
            install_result = vcpkg.install_vcpkg()
            if isinstance(install_result, subprocess.CompletedProcess):
                return install_result.returncode

            if isinstance(install_result, int):
                return install_result

            if os.path.isdir(get_exec_path("vcpkg")):
                print_color("green", "Successfully installed vcpkg")
            else:
                return "FATAL ERROR: vcpkg failed to install"


class ResetToolchainCommand(CommandBase):
    cmd: str = "reset-toolchain"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Sets the CMake toolchain to the current vcpkg instance."
    )

    def setup_args(self):
        pass

    def process(self, args: argparse.Namespace):
        user_presets_path = get_exec_path("CMakeUserPresets.json")
        if settings.is_local_project and os.path.isfile(user_presets_path):
            user_presets = {}
            settings.load_settings(user_presets_path, user_presets)
            cmake_presets.set_toolchain_file(user_presets)
            settings.save_settings(user_presets_path, user_presets)

        return None


class VcpkgCommand(CommandBase):
    cmd: str = "vcpkg"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Run 'vcpkg' tool directly."
    )
    parse: bool = False

    def setup_args(self):
        pass

    def process(self, args: argparse.Namespace):
        if settings.current['vcpkg']['path'] is None or not os.path.isdir(settings.current['vcpkg']['path']):
            print_error("FATAL ERROR: vcpkg path does not exist.")
            print("Vcpkg may not have been installed. Run `mcppt install` to fix.")
            return 1

        vcpkg_path = exec_path(os.path.join(settings.current['vcpkg']['path'], "vcpkg"))
        if not os.path.isfile(vcpkg_path):
            print_error(f"FATAL ERROR: '{vcpkg_path}' does not exist.")
            print("Vcpkg may not have been installed. Run `mcppt install-vcpkg` to fix.")
            return 1

        
        params = sys.argv[2:]      
        
        build_result = subprocess.run([vcpkg_path] + params, cwd=settings.current['vcpkg']['path'])

        if build_result.returncode != 0:
            return build_result



class UpdateVcpkgCommand(CommandBase):
    cmd: str = "update-vcpkg"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Updates the vcpkg system."
    )

    def setup_args(self):
        pass

    def process(self, args: argparse.Namespace):
        if settings.current['vcpkg']['path'] is None or not os.path.isdir(settings.current['vcpkg']['path']):
            print_error("FATAL ERROR: vcpkg path does not exist.")
            print("Boost may not have been installed. Run `mcppt install` to fix.")
            return 1

        vcpkg_path = exec_path(os.path.join(settings.current['vcpkg']['path'], "vcpkg"))
        if not os.path.isfile(vcpkg_path):
            print_error(f"FATAL ERROR: '{vcpkg_path}' does not exist.")
            print("Vcpkg may not have been installed. Run `mcppt install-vcpkg` to fix.")
            return 1
 
        
        build_result = subprocess.run([settings.current["git"]["exec"], "pull"], cwd=settings.current['vcpkg']['path'])

        if build_result.returncode != 0:
            return build_result
        
        bootstrap_result = vcpkg.bootstrap_vcpkg()
        if bootstrap_result.returncode != 0:
            return bootstrap_result
        
        return None