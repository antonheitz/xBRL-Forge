# Python Api

`xbrl-forge` is a Python package designed to streamline the creation of XBRL (eXtensible Business Reporting Language) files. This guide will walk you through its primary functions and how to use them effectively.

## Table of Contents

1. [Installation](#installation)
2. [Key Functions](#key-functions)
    - [validate_input_data](#validate_input_data)
    - [load_input_data](#load_input_data)
    - [create_xbrl](#create_xbrl)
    - [convert_document](#convert_document)
3. [Example Workflow](#example-workflow)
4. [Conclusion](#conclusion)

---

## Installation

Python 3 is needed.

To use `xbrl-forge`, install it via pip:

```bash
pip install xbrl-forge
```

For more detailed logging, set the log level via the environment variable `XBRL_FORGE_LOGGING`, this defaults to `WARNING`. In some cases `INFO` will help since it produces more detailed logs.

---

## Key Functions

### `validate_input_data`

#### Description

This function ensures that the input data is formatted correctly and adheres to the necessary structure for creating XBRL files.

The input data schema is available with descriptions of every key and value [here](../src/xbrl_forge/schemas/input).

#### Parameters

- `data` (dict): The input data to be validated.

#### Returns

The function will not return anything. It will throw an error if the data is not correct according to the schemas.

#### Usage

```python
from xbrl_forge import validate_input_data

validate_input_data(data)
```

### `load_input_data`

#### Description

This function loads and preprocesses input data, preparing it for XBRL file generation.

#### Parameters

- `data` (dict): The raw input data.

#### Returns

- `InputData`: A python object resembing the necessary structure and functions.

#### Usage

```python
from xbrl_forge import load_input_data

data = load_input_data(data)
```

### `create_xbrl`

#### Description

Generates an XBRL file based on the validated input data.

#### Parameters

- `input_data_list` (List of `InputData` Objects): The input data to be transformed into an XBRL file.
- `xthml_template` (str): Optional XHTML template as string. This must use the XHTML namespace and must provide at least the XHTML tags `head`, `title`, `body` and a `div` inside the body with the id value `xhtml-content-root` (this will be used to place the content).

#### Returns

- `File` (a custom File object): An object that containes the xbrl structures ready for saving. It can save and package the information via the object functions `save_files(folder_path)` and `create_package(folder_path)`.

#### Usage

```python
from xbrl_forge import create_xbrl

results = create_xbrl([loaded_data_a, loaded_data_b], style="body { padding: 5px; }")
```

### `convert_document`

#### Description

Generates the ready-to-tag report template from the contents and structures of a other file type. 
Currently supported input formats:
 - docx

#### Parameters

- `document_path` (str): The path to the source document.

#### Returns

- `InputData` (`InputData` Object): The Data structures contained in the object resemble the strucures and information of the source document. With the `to_dict()` function of the object it can be easily prepared for extenal tools to edit (for example as JSON) and the result loaded back in the object via the `load_input_data` function described above.

#### Usage

```python
from xbrl_forge import convert_document

results = convert_document(path_to_source_file)
```

---

## Example Workflow

Here is a complete example that ties the key functions together:

```python
from xbrl_forge import create_xbrl, validate_input_data, load_input_data

# lets say we have 2 data jsons from 2 different systems, data_a and data_b

# validate both data sets
validate_input_data(data_a)
validate_input_data(data_b)

# load data objects
loaded_data_a = load_input_data(data_a)
loaded_data_b = load_input_data(data_b)

# run generation
results = create_xbrl([loaded_data_a, loaded_data_b])

# save either the files
results.save_files("result_folder")
# or the package
results.create_package("result_folder")
```

---

## Conclusion

The `xbrl-forge` package simplifies the process of working with XBRL files by providing tools to validate the input, preprocess, and generate XBRL documents. By following this guide, you can integrate these functions into your workflow and streamline your reporting processes.

For more details, check the documentation or raise issues for support.
