from re import sub
from typing import List, Union

import os, subprocess

from util import *
from colors import *
import settings
from settings import get_exec_path



class PackageEntry(json_class.JsonClass):
    json_attributes = ['name', 'version']
    name: str
    version: str
    
    def __init__(self, name: str="", version:str=""):
        self.name = name
        self.version = version


class PackageList(json_class.JsonClass):
    json_attributes = ['original_triplet', 'package_list']
    
    original_triplet: str
    packages: List[PackageEntry]
    
    def __init__(self, original_triplet:str="", packages:List[PackageEntry]=[]):
        self.original_triplet = original_triplet
        self.packages = packages

    
    @property
    def package_list(self):
        return [i.save_dict() for i in self.packages]
    
    
    @package_list.setter
    def package_list(self, value: List[dict]):
        self.packages = [PackageEntry.new_from_dict(i) for i in value]
        
    def get_install_args(self, triplet: Union[str, None]=None) -> List[str]:
        if triplet is None or triplet == "":
            return [i.name for i in self.packages]
        
        if triplet == "_original":
            return [f"{i.name}:{self.original_triplet}" for i in self.packages]
        
        else:
            return [f"{i.name}:{triplet}" for i in self.packages]


def jsonize_lists(pkgs: List[PackageList]) -> List[dict]:
    return [i.save_dict() for i in pkgs]
    
    
def dejsonize_lists(pkgs: List[dict]) -> List[PackageList]:
    return [PackageList.new_from_dict(i) for i in pkgs]

__all__ = (
    'PackageEntry',
    'PackageList',
    'jsonize_lists',
    'dejsonize_lists'
)