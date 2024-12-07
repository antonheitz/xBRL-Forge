from typing import Dict, List
import jsonschema
import os
import json

def validate_schema(data: dict, root_schema_id: str, schema_folder: str) -> None:
    store: Dict[str, dict] = _load_schema_folder(schema_folder)
    for id, schema in store.items():
        jsonschema.Draft202012Validator.check_schema(schema)
    root_schema: dict = store[root_schema_id]
    resolver = jsonschema.RefResolver(base_uri="", referrer=root_schema, store=store)
    validator = jsonschema.Draft202012Validator(root_schema, resolver=resolver)
    validator.validate(data)

def _load_schema_folder(schema_folder: str) -> Dict[str, dict]:
    json_files: List[str] = []
    for dir_path, dir_names, file_names in os.walk(schema_folder):
        for file_name in file_names:
            if file_name.split(".")[-1].lower() == "json":
                json_files.append(os.path.join(dir_path, file_name))
    schema_store: Dict[str, str] = {}
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            loaded_json: dict = json.load(f)
        if "$schema" in loaded_json and "$id" in loaded_json:
            schema_store[loaded_json["$id"]] = loaded_json
    return schema_store
