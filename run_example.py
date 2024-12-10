import json

from src.xbrl_forge import create_xbrl, validate_input_data, load_input_data, convert_document

with open("examples/input_documents/stylesheet.css", "r") as f:
    style_data = f.read()
with open("examples/input_documents/ESEF-ixbrl.json", "r") as f:
    data_json = json.loads(f.read())
    validate_input_data(data_json)
    data = load_input_data(data_json)
with open("examples/input_documents/ESEF-ixbrl-2.json", "r") as f:
    data2_json = json.loads(f.read())
    validate_input_data(data2_json)
    data2 = load_input_data(data2_json)
with open("examples/input_documents/xbrl.json", "r") as f:
    data_xbrl_json = json.loads(f.read())
    validate_input_data(data_xbrl_json)
    data_xbrl = load_input_data(data_xbrl_json)

results = create_xbrl([data, data2, data_xbrl], styles=style_data)
results.save_files("examples/result", True)
results.create_package("examples/result", True)

loaded_docx = convert_document("examples/file_conversions/Testing document.docx")
loaded_docx_dict = loaded_docx.to_dict()
validate_input_data(loaded_docx_dict)
with open("examples/result/docx_conversion.json", "w+") as f:
    f.write(json.dumps(loaded_docx_dict))
docx_result = create_xbrl([loaded_docx])
docx_result.save_files("examples/result", True)