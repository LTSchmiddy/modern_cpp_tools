import os, shutil, json, subprocess
from typing import Union

from util import *
from util.json_class import JsonClass
import settings

project_file_name = "mct_project_info.json"
project_file_path = lambda: settings.get_exec_path_fslashed(project_file_name)

current = None

def default_project():
    return {
        "packages": [],
        "custom_user_toolchain_values": {},
        "shared_toolchain_files": []
    }

def custom_user_toolchain_value_example():
    return {
        "EXAMPLE": {
            "desc": "description",
            "default": "default_value"
        }
    }

def load_project_file(filePath: str):
    global current
    
    current = default_project()
    settings.load_settings(filePath, current)
    
    # if len(current['custom_user_toolchain_values'].keys()) <= 0:
        # current['custom_user_toolchain_values'] = custom_user_toolchain_value_example()

def attempt_load_local_project():
    if not settings.is_local_project:
        print_warning("!!! If you see this message, you've encountered a bug of some sort.") 
        print_warning("The function 'attempt_load_local_project()' is being called in global mode, which obviously should not happen.")
        print_warning("Since we're not running as local project, there's no project info to load.")
        return


    load_project_file(project_file_path())
    print("Project info loaded.")