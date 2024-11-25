from dataclasses import dataclass
from typing import Dict, List
import os
import shutil
import logging

logger = logging.getLogger(__name__)

class File:
    name: str
    content: str 
    contained_files: List['File'] 

    def __init__(cls, name: str, content: str = None, contained_files: List['File'] = None):
        cls.name = name
        cls.content = content
        cls.contained_files = [] if contained_files == None else contained_files

    def save_file(cls, folder_path: str, remove_existing_files: bool = False) -> None:
        new_path: str = os.path.join(folder_path, cls.name)
        if remove_existing_files:
            if os.path.isdir(new_path):
                shutil.rmtree(new_path)
            if os.path.isfile(new_path):
                os.remove(new_path)
        if cls.contained_files:
            os.mkdir(new_path)
            for file in cls.contained_files:
                file.save_file(new_path, remove_existing_files)
        else:
            with open(new_path, "w+") as f:
                f.write(cls.content)

@dataclass
class Tag:
    namespace: str
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Tag':
        return cls(
            namespace=data.get("namespace"),
            name=data.get("name")
        )
    
    def copy(cls) -> 'Tag':
        return cls.__class__(
            namespace=cls.namespace,
            name=cls.name
        )
    
    def to_uname(cls) -> str:
        return f"{{{cls.namespace}}}{cls.name}"

    def to_prefixed_name(cls, prefixes: Dict[str, str], local_taxonomy_prefix: str = None) -> str:
        if not cls.namespace:
            return f"{local_taxonomy_prefix}:{cls.name}"
        return f"{prefixes.get(cls.namespace, 'unknown')}:{cls.name}"
    
    def to_dict(cls) -> dict:
        return {
            "namespace": cls.namespace,
            "name": cls.name
        }
