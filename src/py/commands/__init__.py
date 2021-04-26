import sys, os, argparse

class CommandBase:
    cmd: str = ""
    argparser: argparse.ArgumentParser = argparse.ArgumentParser(description="Base Arg Parser")
    parse: bool = True

    def __init__(self):
        self.setup_args()

    def setup_args(self):
        pass
    
    def run(self, args_list: list):
        if self.parse:
            return self.process(self.argparser.parse_args(args_list))
        else:
            return self.process(None)

    def process(self, args: argparse.Namespace):
        pass


def get_commands():
    retVal = {}

    for i in CommandBase.__subclasses__():
        retVal[i.cmd] = i
    
    return retVal

def get_command_desc():
    retVal = {}

    for i in CommandBase.__subclasses__():
        retVal[i.cmd] = i.argparser.description
    
    return retVal


# Importing all commands here:
from .packages_cmd import *
from .project_cmd import *
from .template_cmd import *
