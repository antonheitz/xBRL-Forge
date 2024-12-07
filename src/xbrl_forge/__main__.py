from typing import List
import argparse
import os
import json

from __init__ import create_xbrl, validate_input_data, load_input_data

# parse CLI arguments
parser = argparse.ArgumentParser(description="xBRL Forge CLI")
parser.add_argument("-if", "--input-files", nargs="+", required=True)
parser.add_argument("-sf", "--style-file", default=None)
parser.add_argument("-of", "--output-folder", required=True)
parser.add_argument("-p", "--package", action="store_true")
args = parser.parse_args()

# read and validate input files
loaded_dicts: List[dict] = []
for file_path in [os.path.abspath(fp) for fp in args.input_files]:
    with open(file_path, "r", encoding="utf-8") as f:
        data: dict = json.load(f)
    validate_input_data(data)
    loaded_dicts.append(data)

# load input files
input_data = [load_input_data(input_dict) for input_dict in loaded_dicts]

# load style file
style_data = None
if args.style_file:
    with open(os.path.abspath(args.style_file), "r", encoding="utf-8") as f:
        style_data = f.read()

# run generation
result = create_xbrl(input_data, styles=style_data)

if args.package:
    result.create_package(os.path.abspath(args.output_folder), False)
else:
    result.save_files(os.path.abspath(args.output_folder), False)