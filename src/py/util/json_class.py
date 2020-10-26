from __future__ import annotations
from typing import List, Tuple, Union

import json


class JsonClass:
    json_attributes: Tuple[str] = ()

    def save_dict(self):
        return make_dict(self, self.json_attributes)

    def save_json_string(self, indent=4, **kwargs):
        return json.dumps(self.save_dict(), indent=indent, **kwargs)

    def save_json_file(self, filepath: str, indent=4, **kwargs):
        return json.dump(self.save_dict(), open(filepath, 'w'), indent=indent, **kwargs)


    def load_json_file(self, filepath: str):
        in_data = json.load(open(filepath, 'r'))
        self.load_dict(in_data)

    def load_json_string(self, p_str: str):
        in_data = json.loads(p_str)
        self.load_dict(in_data)

    def load_dict(self, p_dict: dict):
        for key, value in p_dict.items():
            setattr(self, key, value)


def make_dict(obj, attrs: Union[List[str], Tuple[str]]):
    retVal = {}
    for i in attrs:
        if hasattr(obj, i):
            attr = getattr(obj, i)
            if isinstance(attr, JsonClass):
                retVal[i] = attr.save_dict()
            else:
                retVal[i] = attr
        else:
            pass
            # print(f"ERROR: object '{str(obj)}' does not have attribute '{i}'...")

    return retVal