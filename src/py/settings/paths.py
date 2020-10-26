import os
from typing import Union
import settings



def get_global_exec_path(path):
    return os.path.join(settings.exec_dir, path)



def get_exec_path(path):
    if settings.project_dir is None:
        return get_global_exec_path(path)
    
    return os.path.join(settings.project_dir, path)



def get_exec_path_fslashed(path):
    return get_exec_path(path).replace('\\', '/')
