from dataclasses import dataclass
from typing import Dict, List, Tuple
import os
import shutil
import logging
import zipfile

logger = logging.getLogger(__name__)

class File:
    name: str
    content: str 
    contained_files: List['File'] 
    zip_extension: str

    def __init__(cls, name: str, content: str = None, contained_files: List['File'] = None, zip_extension: str = "zip"):
        cls.name = name
        cls.content = content
        cls.contained_files = [] if contained_files == None else contained_files
        cls.zip_extension = zip_extension

    def save_files(cls, folder_path: str, remove_existing_files: bool = False) -> None:
        new_path: str = os.path.join(folder_path, cls.name)
        if remove_existing_files:
            if os.path.isdir(new_path):
                shutil.rmtree(new_path)
            if os.path.isfile(new_path):
                os.remove(new_path)
        if cls.contained_files:
            os.mkdir(new_path)
            for file in cls.contained_files:
                file.save_files(new_path, remove_existing_files)
        else:
            with open(new_path, "w+") as f:
                f.write(cls.content)

    def create_package(cls, folder_path: str, remove_existing_package: bool = False) -> str:
        file_path: str = os.path.join(folder_path, f"{cls.name}.{cls.zip_extension}")
        if remove_existing_package:
            if os.path.isfile(file_path):
                os.remove(file_path)
        with zipfile.ZipFile(file_path, "w") as zip:
            for path, file in cls._list_files():
                zip.writestr(path, file.content)
        return file_path

    def _list_files(cls, prepend_path: str = None) -> List[Tuple[str, "File"]]:
        file_path: str = cls.name
        if prepend_path:
            file_path = os.path.join(prepend_path, file_path)
        file_list: List[Tuple[str, "File"]] = []
        if cls.content:
            file_list.append((file_path, cls))
        for child in cls.contained_files:
            file_list += child._list_files(file_path)
        return file_list

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
