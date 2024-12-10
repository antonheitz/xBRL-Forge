# Document Conversion

'xbrl-forge' lets you create the data structure 'InputData' for iXBRL reports by importing the contents and strucures of other files.

## Contents

1. [Supported File Types](#supported-file-types)
2. [How to Convert](#how-to-convert)

## Supported File types

Currently following input data types are supported:
 - Word (.docx)

## How to Convert

Please make sure the package is installed.

All you need is the path of the file to be converted.

```python
from xbrl_forge import convert_document

input_data = convert_document(filepath)
```

This will return an InputData Object which can be modified (either as a python object or as a dict by calling its .to_dict() function) and then used to create the xBRL files.

