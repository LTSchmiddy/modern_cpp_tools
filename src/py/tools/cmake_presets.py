import os, textwrap, sys

from pathlib import Path
from typing import Union
import settings
import project
from util import *

toolchain_message_color = "orange"

vcpkg_toolchain_rel_path = "scripts/buildsystems/vcpkg.cmake"
project_toolchain_rel_path = "mct_user_toolchain.cmake"

vcpkg_include_rel_path = "installed/${VCPKG_TARGET_TRIPLET}/include"
vcpkg_include_rel_path_template = lambda triplet: f"installed/{triplet}/include"


# Absolute Paths:
get_vcpkg_toolchain_path = lambda: os.path.join(
    settings.current["vcpkg"]["path"], vcpkg_toolchain_rel_path
).replace("\\", "/")
get_global_vcpkg_toolchain_path = lambda: os.path.join(
    settings.s_globals["vcpkg"]["path"], vcpkg_toolchain_rel_path
).replace("\\", "/")

get_vcpkg_include_path = lambda: os.path.join(
    settings.current["vcpkg"]["path"], vcpkg_include_rel_path
).replace("\\", "/")
get_global_vcpkg_include_path = lambda: os.path.join(
    settings.s_globals["vcpkg"]["path"], vcpkg_include_rel_path
).replace("\\", "/")

get_vcpkg_include_path_template = lambda triplet: os.path.join(
    settings.current["vcpkg"]["path"], vcpkg_include_rel_path_template(triplet)
).replace("\\", "/")
get_global_vcpkg_include_path_template = lambda triplet: os.path.join(
    settings.s_globals["vcpkg"]["path"], vcpkg_include_rel_path_template(triplet)
).replace("\\", "/")

get_project_toolchain_path = lambda: os.path.join(
    settings.project_dir, project_toolchain_rel_path
).replace("\\", "/")
get_custom_toolchain_path = lambda path: os.path.join(
    path, project_toolchain_rel_path
).replace("\\", "/")

mct_default_preset_name = "mct-default"
mct_default_user_preset_name = "mct-user-default"


def default_preset_file():
    return {
        "version": 2,
        "cmakeMinimumRequired": {"major": 3, "minor": 0, "patch": 0},
        "configurePresets": [
            {
                "name": mct_default_preset_name,
                "displayName": "MCT Default Config",
                "generator": "Ninja",
                "description": "Default build using vcpkg and Ninja generator",
                "binaryDir": "${sourceDir}/build",
                "cacheVariables": {},
            }
        ],
        "buildPresets": [],
    }


def make_user_preset_file(toolchain_file: str = None):
    if settings.current["vcpkg"]["path"] is None:
        print_warning(
            f"WARNING: vcpkg path not set. Toolchain path will not be configured.'"
        )
        toolchain_file = ""

    if toolchain_file is None:
        # print(f"{settings.current=}")
        toolchain_file = get_project_toolchain_path()
        print(f"{toolchain_file=}")

    if toolchain_file != "" and not os.path.isfile(toolchain_file):
        print_warning(
            f"WARNING: '{toolchain_file}' does not exist. Toolchain path will not be configured."
        )
        toolchain_file = ""

    return {
        "version": 2,
        "configurePresets": [
            {
                "name": mct_default_user_preset_name,
                "binaryDir": "${sourceDir}/build",
                "generator": "Ninja",
                "cacheVariables": {
                    "CMAKE_TOOLCHAIN_FILE": toolchain_file.replace("\\", "/"),
                },
            }
        ],
        "buildPresets": [],
    }


def set_toolchain_file(
    p_dict: dict,
    names: Union[list, tuple] = [mct_default_user_preset_name],
    toolchain_file: str = None,
):
    if toolchain_file is None:
        toolchain_file = get_project_toolchain_path()
    for i in p_dict["configurePresets"]:
        if i["name"] in names:
            i["cacheVariables"]["CMAKE_TOOLCHAIN_FILE"] = toolchain_file.replace(
                "\\", "/"
            )


def make_user_config_preset(
    name: str,
    triplet: str = "",
    build_type: str = "",
    append_inherits: list[str] = [],
    *,
    prepend_inherits: list[str] = [],
    inherits: list[str] = [mct_default_user_preset_name, mct_default_preset_name],

):
    retVal = {
        "name": name,
        "inherits": append_inherits + inherits + prepend_inherits,
        "displayName": name,
        "description": f"MCT Configure Preset for {name}",
        "binaryDir": f"${{sourceDir}}/build/{name}",
        "cacheVariables": {},
    }

    if triplet != "":
        retVal["cacheVariables"]["VCPKG_TARGET_TRIPLET"] = triplet
    
    if build_type != "":
        retVal["cacheVariables"]["CMAKE_BUILD_TYPE"] = build_type

    return retVal


def make_user_build_preset(name: str, configurePreset: str = ""):
    return {
        "name": name,
        "displayName": name,
        "description": f"MCT Build Preset for {name}",
        "configurePreset": configurePreset,
    }


def add_user_triplet(p_dict: dict, triplet: str, build_type: str = "", create_build_preset: bool = True, verbose: bool = True):
    if build_type == "":
        name = triplet
    else:
        # Finding/creating the template preset for the triplet:
        name = f"{triplet}-{build_type}"
        if not list_contains(lambda x: x["name"] == triplet, p_dict["configurePresets"]):
            add_user_triplet(p_dict, triplet, "", False, False)

    # Adding config preset
    if list_contains(lambda x: x["name"] == name, p_dict["configurePresets"]):
        if verbose: print(f"'{name} configure preset aleady exists...'")
    else:
        if build_type == "":
            p_dict["configurePresets"].append(
                make_user_config_preset(name, triplet, build_type)
            )
        else:
            p_dict["configurePresets"].append(
                make_user_config_preset(name, "", build_type, inherits=[triplet])
            )

    if create_build_preset:
        # Adding build preset
        if list_contains(lambda x: x["name"] == name, p_dict["buildPresets"]):
            if verbose: print(f"'{name} build preset aleady exists...'")
        else:
            p_dict["buildPresets"].append(make_user_build_preset(name, name))


def construct_user_toolchain_values(verbose: bool = True):
    for i in project.current["required_user_toolchain_values"]:
        if i not in settings.current["toolchain"]["user_toolchain_values"].keys():
            settings.current["toolchain"]["user_toolchain_values"][str(i)] = None

        if (
            verbose
            and settings.current["toolchain"]["user_toolchain_values"][str(i)] is None
        ):
            print_warning(f"WARNING: user toolchain value {i} is unset.")


def build_user_toolchain(path: str = None, verbose=True) -> str:
    if path is None:
        path = get_project_toolchain_path()

    global_include = get_global_vcpkg_include_path()
    global_path = get_global_vcpkg_toolchain_path()
    local_include = get_vcpkg_include_path()
    local_path = get_vcpkg_toolchain_path()
    retVal = f"# {path}" + textwrap.dedent(
        f"""
        # Project toolchain file generated by MCT. 
        # DO NOT EDIT! ALL CHANGES WILL BE OVERRIDDEN!
        # =======================================================================================================
        """
    )

    if settings.current["toolchain"]["use_global"]:
        retVal += textwrap.dedent(
            f"""
            # Global toolchain (disabled by default):
            include({global_path}) #-global-toolchain
            set(GLOBAL_TRIPLET_INCLUDE_DIR {global_include}) #-global-include
            include_directories(${{GLOBAL_TRIPLET_INCLUDE_DIR}})
            """
        )

    if settings.current["toolchain"]["use_local"]:
        retVal += textwrap.dedent(
            f"""
            # Local toolchain:
            include({local_path}) #-local-toolchain
            set(LOCAL_TRIPLET_INCLUDE_DIR {local_include}) #-local-include
            include_directories(${{LOCAL_TRIPLET_INCLUDE_DIR}})
            """
        )

    retVal += "\n# User Toolchain Values:\n"
    construct_user_toolchain_values(verbose)
    for key, value in settings.current["toolchain"]["user_toolchain_values"].items():
        if value is not None:
            if isinstance(value, str):
                retVal += f"set({key} \"{value}\")\n"
            else:
                retVal += f"set({key} {value})\n"
                
    retVal += "\n# Project Shared Includes:\n"
    for i in project.current["shared_toolchain_files"]:
        path_str = str(Path(i).resolve().absolute()).replace("\\", "\\\\")
        retVal += f"include(\"{path_str}\")\n"

    retVal += "\n# Private Includes:\n"
    for i in settings.current["toolchain"]["private_toolchain_files"]:
        path_str = str(Path(i).resolve().absolute()).replace("\\", "\\\\")
        retVal += f"include(\"{path_str}\")\n"

    return path, retVal


def update_user_toolchain_file(root_dir: str = None, verbose=True):
    # toolchain_path, toolchain_out = build_user_toolchain()
    if root_dir is None:
        toolchain_path, toolchain_out = build_user_toolchain(verbose=verbose)
    else:
        toolchain_path, toolchain_out = build_user_toolchain(
            get_custom_toolchain_path(str(root_dir)), verbose=verbose
        )

    toolchain_out_file = open(toolchain_path, "w")
    toolchain_out_file.write(toolchain_out)
    toolchain_out_file.close()
