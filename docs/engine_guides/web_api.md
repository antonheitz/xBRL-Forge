# Web (REST) API

`xbrl-forge` has a built-in Webserver. Learn here how to use it to communicate with it!

## Table of Contents

1. [Installation](#installation)
2. [Endpoints](#endpoints)
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

To start the build-in web-server just run following command:

```bash
python3 -m xbrl_forge
```

This will start the webserver on port `8000`. To change the port, simple put your desired port into an environment variable called `XBRL_FORGE_PORT`.

For more detailed logging, set the log level via the environment variable `XBRL_FORGE_LOGGING`, this defaults to `WARNING`. In some cases `INFO` will help since it produces more detailed logs.

---

## Endpoints

### `/convert_document`

#### Description

This enpoint Generates the ready-to-tag report template from the contents and structures of a other file type. 

Currently supported input formats:
 - docx

#### Parameters (multipart/form-data)

 - `document`: The binary source document.

#### Returns

 - `InputData` (JSON): The Data structures contained in the object resemble the strucures and information of the source document.

#### Usage

```python
import requests

result = requests.post(
    "http://localhost:8000/convert_document", 
    files={'document': open(path_to_source_file, 'rb')}
)
input_data_dict = result.json()
```

### `/validate_input_data`

#### Description

This endpoint ensures that the input data is formatted correctly and adheres to the necessary structure for creating XBRL files.

The input data schema is available with descriptions of every key and value [here](../src/xbrl_forge/schemas/input).

#### Parameters

 - `input_data` (JSON as string): The proposed data structure as JSON string.

#### Returns

 - `ValidationResult` (JSON): The validation results for the provided data structure, containing two keys `valid` (boolean, `true` if valid, `false` if not) and `message` (string) giving detailes on the validation.

#### Usage

```python
import requests, json

result = requests.post(
    "http://localhost:8000/validate_input_data", 
    data={'input_data': json.dumps(proposed_data_structure)}
)

validation_result = result.json()
```

### `/create_xbrl`

#### Description

Endpoint to generates the (i)xBRL file based on the input data Object(s) and optiontal XHTML Template.

#### Parameters

 - `input_data_list` (JSON as string): A list of `InputData` JSON objects (1 to N) that will be combined intoop a report/taxonomy package.
 - `xthml_template` (string, optional): Optional XHTML template as string. This must use the XHTML namespace and must provide at least the XHTML tags `head`, `title`, `body` and a `div` inside the body with the id value `xhtml-content-root` (this will be used to place the content).

#### Returns

 - `Package` (File): A Binary ZIP file containings reports and the taxonomy.

#### Usage

```python
import requests, json, re

result = requests.post(
    "http://localhost:8000/create_xbrl", 
    data={
        'input_data_list': json.dumps([input_data_1, input_data_2]),
        'xhtml_template': None # this can be a string with an xhtml template
    }
)

header_info = result.headers['content-disposition']
filename = re.findall("filename=(.+)", header_info)[0]

open(filename, 'wb').write(result.content)
```

---

## Example Workflow

Here is a complete example that ties the endpoints together. This assumes the default port `8000` is used:

```python
import requests, json, re

url = "http://localhost:8000"
docx_file = "examples/file_conversions/Testing Docx document.docx"

conversion_result = requests.post(
    url + "/convert_document", 
    files={'document': open(docx_file, 'rb')}
)
data = conversion_result.json()

# this is where you would edit the data structures & "tag" the information

validate_result = requests.post(
    url + "/validate_input_data", 
    data={'input_data': json.dumps(data)}
)
validate_result_dict = validate_result.json()
if not validate_result_dict.get("valid"):
    print("Validation failed with message:")
    print(validate_result_dict.get("message"))

create_package_request = requests.post(
    url + "/create_xbrl", 
    data={'input_data_list': json.dumps([data]), 'xhtml_template': None}
)

cd_header = create_package_request.headers['content-disposition']
filename = re.findall("filename=(.+)", cd_header)[0]

open(filename, 'wb').write(create_package_request.content)
```

---

## Conclusion

The `xbrl-forge` package simplifies the process of working with XBRL files by providing tools to validate the input, preprocess, and generate XBRL documents. By following this guide, you can integrate these functions into your workflow and streamline your reporting processes.

For more details, check the documentation or raise issues for support.
