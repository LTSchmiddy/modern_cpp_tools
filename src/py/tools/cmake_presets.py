import os, textwrap, sys

from typing import Union
import settings
from util import *

vcpkg_toolchain_rel_path = "scripts/buildsystems/vcpkg.cmake"
project_toolchain_rel_path = "mct-toolchain.cmake"

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
                "name": "default",
                "displayName": "Default Config",
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


def get_project_toolchain(path: str = None) -> str:
    if path is None:
        path = get_project_toolchain_path()

    if os.path.isfile(path):
        toolchain_in_file = open(path, 'r')
        toolchain_in = toolchain_in_file.read()
        toolchain_in_file.close()
        return toolchain_in
    else:
        global_include = get_global_vcpkg_include_path()
        global_path = get_global_vcpkg_toolchain_path()
        local_include = get_vcpkg_include_path()
        local_path = get_vcpkg_toolchain_path()
        return f"# {path}" + textwrap.dedent("""
            # Project toolchain file generated by MCT. 
            #
            # The lines ending with the comments `#-global-toolchain`, `#-global-include`, `#-local-toolchain`, and `#-local-include` include the toolchains
            # for the global and local copies of vcpkg. If MCT needs to update where these files are located, these 
            # comments are used to locate these include statements in the file.
            #
            # Don't remove these comments or add anything after them, or else MCT will not detect the comments. 
            # If the comments are not detected, these include lines be added (commented out) to the top of the file.
            #
            # Additionally, don't include anything else on these lines, otherwise MCT may remove your changes. 
            # You may, however comment one of the lines out to disable that toolchain. MCT will watch for this and
            # preserve that commented state if it needs to changes the paths.
            #
            # Otherwise, you may edit these file however you wish.
            # =======================================================================================================
            
            # Global toolchain is disabled by default:
            # include({global_path}) #-global-toolchain
            # set(GLOBAL_TRIPLET_INCLUDE_DIR {global_include}) #-global-include
            # include_directories(${GLOBAL_TRIPLET_INCLUDE_DIR})
            
            # Local toolchain:
            include({local_path}) #-local-toolchain
            set(LOCAL_TRIPLET_INCLUDE_DIR {local_include})`#-local-include
            include_directories(${LOCAL_TRIPLET_INCLUDE_DIR})
            
        """)

def _process_toolchain_string(line: str, path: str, local: bool) -> str:
        line_indent = line[:len(line) - len(line.lstrip())]
        commented = line.lstrip().startswith("#")

        return f"{line_indent}{af.tget(commented, '# ', '')}"\
            f"include(\"{path}\") #-{af.tget(local, 'local', 'global')}-toolchain"

def _process_include_string(line: str, path: str, local: bool) -> str:
        line_indent = line[:len(line) - len(line.lstrip())]
        commented = line.lstrip().startswith("#")

        return f"{line_indent}{af.tget(commented, '# ', '')}"\
            f"set({af.tget(local, 'LOCAL', 'GLOBAL')}_TRIPLET_INCLUDE_DIR {path}) #-{af.tget(local, 'local', 'global')}-include"
            

def _insert_missing_toolchain(line_list: list, path: str, local: bool):
    for i in range(0, len(line_list)):
        line = line_list[i]

        if line.lstrip().startswith("#"):
            continue
        
        line_list.insert(i, textwrap.dedent(f"""
            # {af.tget(local, 'local', 'global').capitalize()} toolchain was missing. Replacing here:
            {_process_toolchain_string("#", path, local)}
        """))

        break

def _insert_missing_include(line_list: list, path: str, local: bool):
    for i in range(0, len(line_list)):
        line = line_list[i]

        if line.lstrip().startswith("#"):
            continue
        
        line_list.insert(i, textwrap.dedent(f"""
            # {af.tget(local, 'local', 'global').capitalize()} toolchain was missing. Replacing here:
            {_process_include_string("#", path, local)}
        """))

        break

        

def update_project_toolchain_file(
    root_dir: str = None,
    local_vcpkg_tc_path: str = None,
    global_vcpkg_tc_path: str = None,
    local_vcpkg_include_path: str = None,
    global_vcpkg_include_path: str = None
):
    
    if local_vcpkg_tc_path is None:
        # print(f"{settings.current=}")
        local_vcpkg_tc_path = get_vcpkg_toolchain_path()
    
    if global_vcpkg_tc_path is None:
        # print(f"{settings.current=}")
        global_vcpkg_tc_path = get_global_vcpkg_toolchain_path()
        
    if local_vcpkg_include_path is None:
        # print(f"{settings.current=}")
        local_vcpkg_include_path = get_vcpkg_include_path()
    
    if global_vcpkg_include_path is None:
        # print(f"{settings.current=}")
        global_vcpkg_include_path = get_global_vcpkg_include_path()


    toolchain_path, toolchain_lines = None, None
    if (root_dir is None):
        toolchain_path, toolchain_lines = get_project_toolchain_path(), get_project_toolchain().split("\n")
    else:
        toolchain_path, toolchain_lines = get_custom_toolchain_path(str(root_dir)), get_project_toolchain(get_custom_toolchain_path(str(root_dir))).split("\n")
    
    found_global_toolchain = False
    found_local_toolchain = False
    
    found_global_include = False
    found_local_include = False

    for i in range(0, len(toolchain_lines)):
        line = toolchain_lines[i]
        
        # Handle global file:
        if line.rstrip().endswith("#-global-toolchain"):
            toolchain_lines[i] = _process_toolchain_string(line, global_vcpkg_tc_path, False)
            found_global_toolchain = True
        
        # Handle local file:
        if line.rstrip().endswith("#-local-toolchain"):
            toolchain_lines[i] = _process_toolchain_string(line, local_vcpkg_tc_path, True)
            found_local_toolchain = True
            
        if line.rstrip().endswith("#-global-include"):
            toolchain_lines[i] = _process_include_string(line, global_vcpkg_include_path, False)
            found_global_include = True
        
        # Handle local file:
        if line.rstrip().endswith("#-local-include"):
            toolchain_lines[i] = _process_include_string(line, local_vcpkg_include_path, True)
            found_local_include = True
    
    if not found_global_toolchain:
        _insert_missing_toolchain(toolchain_lines, global_vcpkg_tc_path, False)

    if not found_local_toolchain:
        _insert_missing_toolchain(toolchain_lines, local_vcpkg_tc_path, True)
        
    if not found_global_include:
        _insert_missing_include(toolchain_lines, global_vcpkg_include_path, True)
    
    if not found_local_include:
        _insert_missing_include(toolchain_lines, local_vcpkg_include_path, True)
    
    toolchain_out = "\n".join(toolchain_lines)

    # print(f"{toolchain_path}")

    toolchain_out_file = open(toolchain_path, "w")
    toolchain_out_file.write(toolchain_out)
    toolchain_out_file.close()