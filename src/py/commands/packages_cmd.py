from re import sub
from typing import Union

import sys, os, subprocess, argparse, shutil, json
from pathlib import Path


from util import *
from colors import *
import project
import settings
from settings import get_exec_path, get_exec_path_fslashed

from tools import vcpkg, cmake_presets

from commands import CommandBase

default_pkglists_filename = "vcpkg-lists.json"

class InstallVcpkgCommand(CommandBase):
    cmd: str = "install-vcpkg"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Install and setup vcpkg directory."
    )

    def setup_args(self):
        pass

    def process(self, args: argparse.Namespace):
        if "has_been_installed" in settings.current["vcpkg"] and settings.current["vcpkg"]["has_been_installed"]:
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
                settings.current["vcpkg"]["has_been_installed"] = True
            else:
                return "FATAL ERROR: vcpkg failed to install"

class VcpkgCommand(CommandBase):
    cmd: str = "vcpkg"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Run 'vcpkg' tool directly."
    )
    parse: bool = False

    def setup_args(self):
        pass

    def process(self, args: argparse.Namespace):
        vcpkg_ready, vcpkg_path = vcpkg.ready_check()
        
        if not vcpkg_ready:
            print_error("ERROR: Vcpkg is not set up... ")
            return 1
        
        params = sys.argv[2:]      
        
        build_result = subprocess.run([vcpkg_path] + params, cwd=settings.current['vcpkg']['path'])

        if build_result.returncode != 0:
            return build_result



class DeleteVcpkgTempsCommand(CommandBase):
    cmd: str = "delete-vcpkg-temps"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Delete temporary files from vcpkg instance to free disk space."
    )
    def setup_args(self):
        self.argparser.add_argument(
            "-i",
            "--ignore-errors",
            action='store_true',
            help="Do not stop on encountering an error while in deleting a file. Instead, continue with the next file."
        )

    def process(self, args: argparse.Namespace):
        vcpkg_ready, vcpkg_path = vcpkg.ready_check()
        
        if not vcpkg_ready:
            print_error("ERROR: Vcpkg is not set up... ")
            return 1
        
        vcpkg_dir = Path(vcpkg_path).parent
        
        package_dir = vcpkg_dir.joinpath("packages")
        buildtrees_dir = vcpkg_dir.joinpath("buildtrees")
        downloads_dir = vcpkg_dir.joinpath("downloads")
        
        if package_dir.exists():
            print(f"Deleting packages directory at '{package_dir}'")
            shutil.rmtree(package_dir, args.ignore_errors)
        else:
            print("No packages directory.")
        
        if buildtrees_dir.exists():
            print(f"Deleting buildtrees directory at '{buildtrees_dir}'")
            shutil.rmtree(buildtrees_dir, args.ignore_errors)
        else:
            print("No buildtrees directory.")
        
        if downloads_dir.exists():
            print(f"Deleting downloads directory at '{downloads_dir}'")
            shutil.rmtree(downloads_dir, args.ignore_errors)
        else:
            print("No downloads directory.")
        

class UpdateVcpkgCommand(CommandBase):
    cmd: str = "update-vcpkg"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Updates the vcpkg instance."
    )

    def setup_args(self):
        pass

    def process(self, args: argparse.Namespace):
        vcpkg_ready, vcpkg_path = vcpkg.ready_check()
        
        if not vcpkg_ready:
            return 1
 
        
        build_result = subprocess.run([settings.current["git"]["exec"], "pull"], cwd=settings.current['vcpkg']['path'])

        if build_result.returncode != 0:
            return build_result
        
        bootstrap_result = vcpkg.bootstrap_vcpkg()
        if bootstrap_result.returncode != 0:
            return bootstrap_result
        
        return None




# class DeleteVcpkgCommand(CommandBase):
#     cmd: str = "delete-vcpkg"
#     argparser: argparse.ArgumentParser = argparse.ArgumentParser(
#         description="Deletes any local vcpkg instance folder and switches back to using the global instance."
#     )

#     def setup_args(self):
#         pass

#     def process(self, args: argparse.Namespace):
#         if settings.current["vcpkg"]["path"] == settings.s_globals["vcpkg"]["path"] and not settings.forced_global_mode:
#             print_error("FATAL ERROR: Vcpkg instance to be deleted was MCT's global instance.")
#             print_error("As a safety measure, you must specify global mode by running 'mct g delete-vcpkg'")


class InstallProjectPackagesCommand(CommandBase):
    cmd: str = "install-packages"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Loads and installs vcpkg packages from the project info file."
    )
    
    def setup_args(self):
        self.argparser.add_argument(
            "-g",
            "--groups",
            default="",
            help="Specify the package group[s] to install, seperated by commas. "
            "Triplets can be set with ':' after each group name. If not present "
            "or left blank, the default triplet for your system is used. "
            "If this argument is not used, all groups will be installed."
        )
    
    def process(self, args: argparse.Namespace):
        vcpkg_ready, vcpkg_path = vcpkg.ready_check()
        
        if not vcpkg_ready:
            return 1
    
        vcpkg.construct_package_group_triplets()
        group_info: dict = {}
        
        # What packages are we installing?
        if args.groups == "":
            group_info: dict = settings.current['vcpkg']['package-group-triplets'].copy()
        else:
            def _process_entry(entry: str):
                if ":" in entry:
                    name, triplet = entry.split(':')
                    
                    if not name in project.current['packages']:
                        print_warning(f"WARNING: No package group named '{name}'. Skipping...")
                    else:
                        group_info[name] = triplet
                else:
                    if not entry in project.current['packages']:
                        print_warning(f"WARNING: No package group named '{entry}'. Skipping...")
                    else:
                        group_info[entry] = settings.current['vcpkg']['package-group-triplets'][entry]
            
            
            if "," in args.groups:
                for i in args.groups.split(","):
                    _process_entry(i)
            else:
                _process_entry(args.groups)

                
        
        # Performing installations:
        for group, triplet in group_info.items():
            print_color(cmake_presets.toolchain_message_color, f"=== Installing group '{group}'", end="")
            
            if triplet != "":
                print_color(cmake_presets.toolchain_message_color, f" (Triplet: {triplet})", end="")
            print_color(cmake_presets.toolchain_message_color, " ===")

            
            for pkg in project.current['packages'][group]:
                pkg_request = pkg
                if triplet != "":
                    pkg_request = f"{pkg}:{triplet}"
                
                print_color(cmake_presets.toolchain_message_color, f"--> installing {pkg}")
                install_result = subprocess.run([vcpkg_path, "install", "--recurse", pkg_request], cwd=settings.current['vcpkg']['path'])
                
                if install_result.returncode != 0:
                    return install_result
                
                
        

class LoadPackageListCommand(CommandBase):
    cmd: str = "load-pkg-list"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Loads and installs vcpkg packages from a vcpkg-list.json file."
    )
    

    def setup_args(self):
        self.argparser.add_argument(
            "-f",
            "--filename",
            default=default_pkglists_filename
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


class SavePackageListCommand(CommandBase):
    cmd: str = "save-pkg-list"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Saves a list of vcpkg the currently installed vcpkg packages."
    )

    def setup_args(self):
        self.argparser.add_argument(
            "-f",
            "--filename",
            default=default_pkglists_filename
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