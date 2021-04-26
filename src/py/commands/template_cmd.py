from re import sub
from typing import Union

import sys, os, subprocess, argparse

from util import *
from colors import *
import settings
from settings import get_exec_path, get_exec_path_fslashed

from tools import vcpkg, cmake_presets, template_manager

from commands import CommandBase


class AddTemplateCommand(CommandBase):
    cmd: str = "add-template"
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Adds common files from a template, to quickstart CMake projects"
    )

    def setup_args(self):
        self.argparser.add_argument(
            "-t",
            "--template",
            choices=template_manager.get_template_list(),
            type=str,
            default="default"
        )
        # Select Destination Dir:
        self.argparser.add_argument(
            "-p",
            "--path",
            type=str,
            default="./"
        )

    def process(self, args: argparse.Namespace):
        template_manager.init_template(args.template, args.path)


        # user_presets["configurePresets"].append(cmake_presets.make_user_preset("x64-windows", "debug"))
