import sys
import os
import json
from colors import *
from .paths import *

exec_dir, exec_file = os.path.split(os.path.abspath(sys.argv[0]))

exec_dir = exec_dir.replace("\\", "/")

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    exec_dir = os.path.dirname(sys.executable)
# elif __file__:
    # exec_dir = os.path.dirname(__file__)

# If we're executing as the source version, the main .py file  is actually found in the `src` subdirectory
# of the project, and `exec_dir` is changed to reflect that. We'll create `exec_file_dir` in case we actually need the
# unmodified path to that script. Obviously, in build mode, these two values will be the same.
exec_file_dir = exec_dir

def is_build_version():
    return exec_file.endswith(".exe")


def is_source_version():
    return exec_file.endswith(".py")


if is_source_version():
    path_arr = exec_dir.split("/")
    exec_dir = "/".join(path_arr[: len(path_arr) - 2]).replace("/", "\\")

# print(f"Is Source: {is_source_version()}")
# print(f"Is Build: {is_build_version()}")
# print(f"Exec Dir: {exec_dir}")

global_file_name = "global_mct_settings.json"
local_file_name = "mct_settings.json"
global_settings_path = get_global_exec_path(global_file_name)


def local_project_check(start_path = os.getcwd().replace('\\', '/')) -> Union[tuple, None]:
    global local_file_name
    # Load the cwd, and make sure the slashing works cross-platform:
    def _r_check_dir(path):
        global local_file_name
        settings_path = os.path.join(path, local_file_name)
        if os.path.isfile(settings_path):
            return True, path, settings_path
        else:
            # Move the search path up a directory:
            new_path = "/".join(path.split("/")[:-1])
            # print(new_path)
            if len(new_path) == 0:
                return False, None, None
            else:
                return _r_check_dir(new_path)
    return _r_check_dir(start_path)

is_local_project, project_dir, local_settings_path = None, None, None

def update_local_status(start_path = os.getcwd().replace('\\', '/')):
    global is_local_project, project_dir, local_settings_path
    is_local_project, project_dir, local_settings_path = local_project_check(start_path)

def default_settings():
    return {
        "common": {
            "template_dir":  get_global_exec_path("new_cmake_templates"),
            "has_been_installed": False
            # "additional_template_dirs": []
        },
        "cmake": {
            "exec": "cmake",
        },
        "vcpkg": {
            "exec": "vcpkg",
            "use_external": False,
            "path": None,
            "repo_uri": "https://github.com/microsoft/vcpkg.git",
            "disable_metrics": True
        },
        "git": {
            "exec": "git"
        }

    }

s_globals = default_settings()
current = default_settings()


def load_settings(path: str = global_settings_path, settings_dict: dict = current):

    def recursive_load_list(main: list, loaded: list):
        for i in range(0, max(len(main), len(loaded))):
            # Found in both:
            if i < len(main) and i < len(loaded):
                if isinstance(loaded[i], dict):
                    recursive_load_dict(main[i], loaded[i])
                elif isinstance(loaded[i], list):
                    recursive_load_list(main[i], loaded[i])
                else:
                    main[i] = loaded[i]
            # Found in main only:
            elif i < len(loaded):
                main.append(loaded[i])


    def recursive_load_dict(main: dict, loaded: dict):
        new_update_dict = {}
        for key, value in main.items():
            if not (key in loaded):
                continue
            if isinstance(value, dict):
                recursive_load_dict(value, loaded[key])
            elif isinstance(value, list):
                recursive_load_list(value, loaded[key])
            else:
                new_update_dict[key] = loaded[key]
        
        # Load settings added to file:
        for key, value in loaded.items():
            if not (key in main):
                new_update_dict[key] = loaded[key]

        main.update(new_update_dict)

    # load preexistent settings file
    if os.path.exists(global_settings_path) and os.path.isfile(global_settings_path):
        try:
            imported_settings = json.load(open(path, "r"))
            # current.update(imported_settings)
            recursive_load_dict(settings_dict, imported_settings)
        except json.decoder.JSONDecodeError as e:
            print (color(f"CRITICAL ERROR IN LOADING SETTINGS: {e}", fg='red'))
            print (color("Using default settings...", fg='yellow'))

    # settings file not found
    else:
        save_settings()


def save_settings(path: str = global_settings_path, settings_dict: dict = current):
    outfile = open(path, "w")
    json.dump(settings_dict, outfile, indent=4)
    outfile.close()


