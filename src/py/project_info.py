import os, shutil, json, subprocess
from typing import Union

from util import *
from util.json_class import JsonClass
import settings


class ProjectInfo(JsonClass):
    packages = {}

