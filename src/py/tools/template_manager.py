import os, json, settings, shutil, util
from argparse import Namespace

def get_template_list():
    return os.listdir(settings.current['common']['template_dir'])


def init_template(template: str, path: str):
    util.mkdir_if_missing(path)

    template_location = os.path.join(settings.current['common']['template_dir'], template)

    shutil.copytree(
        src=template_location, 
        dst=path,
        symlinks=True,
        dirs_exist_ok=True
    )
    

