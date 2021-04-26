import os, textwrap, sys

from typing import Union
import settings
import project
from util import *

toolchain_message_color = 'orange';

vcpkg_toolchain_rel_path = "scripts/buildsystems/vcpkg.cmake"
project_toolchain_rel_path = "mct_user_toolchain.cmake"

vcpkg_include_rel_path = "installed/${VCPKG_TARGET_TRIPLET}/include"
vcpkg_include_rel_path_template = lambda triplet: f"installed/{triplet}/include"


# Absolute Paths:
get_vcpkg_toolchain_path = lambda: os.path.join(settings.current["vcpkg"]["path"], vcpkg_toolchain_rel_path).replace("\\", "/")
get_global_vcpkg_toolchain_path = lambda: os.path.join(settings.s_globals["vcpkg"]["path"], vcpkg_toolchain_rel_path).replace("\\", "/")

get_vcpkg_include_path = lambda: os.path.join(settings.current["vcpkg"]["path"], vcpkg_include_rel_path).replace("\\", "/")
get_global_vcpkg_include_path = lambda: os.path.join(settings.s_globals["vcpkg"]["path"], vcpkg_include_rel_path).replace("\\", "/")

get_vcpkg_include_path_template = lambda triplet: os.path.join(settings.current["vcpkg"]["path"], vcpkg_include_rel_path_template(triplet)).replace("\\", "/")
get_global_vcpkg_include_path_template = lambda triplet: os.path.join(settings.s_globals["vcpkg"]["path"], vcpkg_include_rel_path_template(triplet)).replace("\\", "/")

get_project_toolchain_path = lambda: os.path.join(settings.project_dir, project_toolchain_rel_path).replace("\\", "/")
get_custom_toolchain_path = lambda path: os.path.join(path, project_toolchain_rel_path).replace("\\", "/")

def default_preset_file():
    return {
        "version": 2,
        "cmakeMinimumRequired": {
            "major": 3,
            "minor": 0,
            "patch": 0
        },
        "configurePresets": [
            {
                "name": "mct-default",
                "displayName": "MCT Default Config",
                "description": "Default build using vcpkg and Ninja generator",
                "generator": "Ninja",
                "binaryDir": "${sourceDir}",
                "cacheVariables": {}
            }
        ]
    }

def make_user_preset_file(toolchain_file: str = None):
    if settings.current["vcpkg"]["path"] is None:
        print_warning(f"WARNING: vcpkg path not set. Toolchain path will not be configured.'")
        toolchain_file = ""

    if toolchain_file is None:
        # print(f"{settings.current=}")
        toolchain_file = get_project_toolchain_path()
        print(f"{toolchain_file=}")

    if toolchain_file != "" and not os.path.isfile(toolchain_file):
        print_warning(f"WARNING: '{toolchain_file}' does not exist. Toolchain path will not be configured.")
        toolchain_file = ""

    return {
        "version": 2,
        "configurePresets": [
            {
                "name": "default-toolchain",
                "inherits": ["default"],
                "generator": "Ninja",
                "cacheVariables": {
                    "CMAKE_TOOLCHAIN_FILE": toolchain_file.replace("\\", "/"),
                }
            }
        ]
    }

def set_toolchain_file(
    p_dict: dict,
    names: Union[list, tuple] = ["default-toolchain"],
    toolchain_file: str = None
):
    if toolchain_file is None:
        toolchain_file = get_project_toolchain_path()
    for i in p_dict["configurePresets"]:
        if i["name"] in names:
            i["cacheVariables"]["CMAKE_TOOLCHAIN_FILE"] = toolchain_file.replace("\\", "/")



def make_user_preset(name: str, triplet: str = "", config: str = ""):   
    if config == "":
        return {
            "name": name,
            "inherits": ["default-toolchain"],
            "displayName": name,
            "description": f"MCT Preset for {name}",
            "binaryDir": f"${{sourceDir}}/b/{name}",
            "cacheVariables": {
                "VCPKG_TARGET_TRIPLET": triplet
            }
        }

    return {
        "name": name,
        "inherits": ["default-toolchain"],
        "displayName": name,
        "description": f"MCT Preset for {name}",
        "binaryDir": f"${{sourceDir}}/b/{name}",
        "cacheVariables": {
            "CMAKE_BUILD_TYPE": config.capitalize(),
            "VCPKG_TARGET_TRIPLET": triplet
        }
    }

def add_triplet(p_dict: dict, triplet: str, config: str = ""):
        if config == "":
            name=triplet
        else:
            name=f"{triplet}-{config}"
        if list_contains(lambda x: x["name"] == name, p_dict["configurePresets"]):
            print(f"'{name} aleady exists...'")
        else:
            p_dict["configurePresets"].append(make_user_preset(name, triplet, config))


def construct_user_toolchain_values(verbose: bool = True):
    for i in project.current['required_user_toolchain_values']:
        if i not in settings.current['toolchain']['user_toolchain_values'].keys():
            settings.current['toolchain']['user_toolchain_values'][str(i)] = None
            
        if verbose and settings.current['toolchain']['user_toolchain_values'][str(i)] is None:
            print_warning(f"WARNING: user toolchain value {i} is unset.")

def build_user_toolchain(path: str = None, verbose=True) -> str:
    if path is None:
        path = get_project_toolchain_path()


    global_include = get_global_vcpkg_include_path()
    global_path = get_global_vcpkg_toolchain_path()
    local_include = get_vcpkg_include_path()
    local_path = get_vcpkg_toolchain_path()
    retVal = f"# {path}" + textwrap.dedent(f"""
        # Project toolchain file generated by MCT. 
        # DO NOT EDIT! ALL CHANGES WILL BE OVERRIDDEN!
        # =======================================================================================================
        """) 

    if settings.current['toolchain']['use_global']:
        retVal += textwrap.dedent(f"""
            # Global toolchain (disabled by default):
            include({global_path}) #-global-toolchain
            set(GLOBAL_TRIPLET_INCLUDE_DIR {global_include}) #-global-include
            include_directories(${{GLOBAL_TRIPLET_INCLUDE_DIR}})
            """)
    
    if settings.current['toolchain']['use_local']:
        retVal += textwrap.dedent(f"""
            # Local toolchain:
            include({local_path}) #-local-toolchain
            set(LOCAL_TRIPLET_INCLUDE_DIR {local_include}) #-local-include
            include_directories(${{LOCAL_TRIPLET_INCLUDE_DIR}})
            """)
    
    retVal += "\n# User Toolchain Values:\n"
    construct_user_toolchain_values(verbose)
    for key, value in settings.current['toolchain']['user_toolchain_values'].items():
        if value is not None:
            retVal += f"set({key} {value})\n"


    retVal += "\n# Project Shared Includes:\n"
    for i in project.current['shared_toolchain_files']:
        retVal += f"include({settings.get_exec_path_fslashed(i)})\n"

       
    return path, retVal
def update_user_toolchain_file(root_dir: str = None, verbose=True):
    # toolchain_path, toolchain_out = build_user_toolchain()
    if (root_dir is None):
        toolchain_path, toolchain_out = build_user_toolchain(verbose=verbose)
    else:
        toolchain_path, toolchain_out = build_user_toolchain(get_custom_toolchain_path(str(root_dir)),verbose=verbose)


    toolchain_out_file = open(toolchain_path, "w")
    toolchain_out_file.write(toolchain_out)
    toolchain_out_file.close()