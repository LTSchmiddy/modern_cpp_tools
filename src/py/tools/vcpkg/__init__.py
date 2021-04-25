from re import sub
from typing import Dict, List, Tuple, Union

import os, subprocess
# from tools.vcpkg import package_list
from tools.vcpkg.package_list import *

from util import *
from colors import *
import settings
from settings import get_exec_path

from tools import cmake_presets

def ready_check():
    if settings.current['vcpkg']['path'] is None or not os.path.isdir(settings.current['vcpkg']['path']):
        print_error("FATAL ERROR: vcpkg path does not exist.")
        print("Vcpkg may not have been installed. Run `mct install-vcpkg` to fix.")
        return False, ""

    vcpkg_path = exec_path(os.path.join(settings.current['vcpkg']['path'], "vcpkg"))
    if not os.path.isfile(vcpkg_path):
        print_error(f"FATAL ERROR: '{vcpkg_path}' does not exist.")
        print("Vcpkg may not have been installed. Run `mct install-vcpkg` to fix.")
        return False, ""

    return True, vcpkg_path


def install_vcpkg() -> Union[subprocess.CalledProcessError, int, None]:
    if \
    settings.current["vcpkg"]["path"] is not None \
    and settings.current["vcpkg"]["path"] != settings.s_globals["vcpkg"]["path"] \
    and os.path.isdir(settings.current["vcpkg"]["path"]) \
    :
        print_warning("An old copy of vcpkg was detected. Delete this in order to reinstall vcpkg.")
        print_warning("Skipping...")

        if settings.is_local_project:
            cmake_presets.update_project_toolchain_file()

        return None

    # Download vcpkg:
    vcpkg_git_cmd = [settings.current["git"]["exec"], "clone", settings.current["vcpkg"]["repo_uri"]]

    git_result = subprocess.run(vcpkg_git_cmd,  cwd=get_exec_path(""))

    if git_result.returncode != 0:
        return git_result

    # Setting vcpkg path setting to the new location:

    settings.current["vcpkg"]["path"] = get_exec_path("vcpkg")

    # Running setup:
    bootstrap_result = bootstrap_vcpkg()
    if bootstrap_result.returncode != 0:
        return bootstrap_result

    user_presets_path = get_exec_path("CMakeUserPresets.json")
    if settings.is_local_project and os.path.isfile(user_presets_path):
        user_presets = {}
        settings.load_settings(user_presets_path, user_presets)
        cmake_presets.set_toolchain_file(user_presets)
        settings.save_settings(user_presets_path, user_presets)

    return None

def bootstrap_vcpkg():
    bootstrap_cmd = None
    if os.name == "nt":
        bootstrap_cmd = [os.path.join(settings.current["vcpkg"]["path"], "bootstrap-vcpkg.bat")]
    elif os.name == "posix":
        bootstrap_cmd = [os.path.join(settings.current["vcpkg"]["path"], "bootstrap-vcpkg.sh")]
    else:
        print_error(f"FATAL ERROR: Unsure of how to proceed for {os.name=}")
        return 1

    if settings.current["vcpkg"]["disable_metrics"]:
        bootstrap_cmd += ["-disableMetrics"]

    result = subprocess.run(bootstrap_cmd, cwd=settings.current["vcpkg"]["path"])
    if settings.is_local_project:
        cmake_presets.update_project_toolchain_file()
    return result


def parse_package_list(package_list: str) -> List[PackageList]:
    pkg_dict: Dict[str, PackageList] = {}
    
    for line in package_list.split("\n"):
        if line.strip() == "":
            continue
        triplet, package = parse_package_line(line)
        
        if triplet not in pkg_dict:
            pkg_dict[triplet] = PackageList(triplet)
            
        pkg_dict[triplet].packages.append(package)
    
    retVal = []
    for triplet, pkgs in pkg_dict.items():
        retVal.append(pkgs)
    return retVal
        
        
def parse_package_line(line: str) -> Tuple[str, PackageEntry]:
    # print (line)
    name_end = line.index(":")
    name, line = line[:name_end], line[name_end+1:]
    
    triplet_end = line.index(" ")
    triplet, line = line[:triplet_end], line[triplet_end+1:].strip()
    
    version = None
    
    if " " in line:
        version_end = line.index(" ")
        version, line = line[:version_end], line[version_end+1:].strip()
    else:
        version = line
    
    print ("Found:", name, triplet, version)
    
    return triplet, PackageEntry(name, version)