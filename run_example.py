import json

from src.xbrl_forge import create_xbrl, validate_input_data, load_input_data, convert_document

# example xhtml template
with open("examples/input_documents/xhtml_template.html", "r") as f:
    xthml_template = f.read()

# example esef file
with open("examples/input_documents/ESEF_example.json", "r") as f:
    esef_json = json.loads(f.read())
    validate_input_data(esef_json)
    esef_loaded = load_input_data(esef_json)

# example combination of different document types
with open("examples/input_documents/ixbrl_xhtml_example.json", "r") as f:
    ixbrl_xhtml_json = json.loads(f.read())
    validate_input_data(ixbrl_xhtml_json)
    ixbrl_xhtml_loaded = load_input_data(ixbrl_xhtml_json)
with open("examples/input_documents/xbrl_example.json", "r") as f:
    xbrl_json = json.loads(f.read())
    validate_input_data(xbrl_json)
    xbrl_loaded = load_input_data(xbrl_json)
loaded_docx_xhtml = convert_document("examples/file_conversions/Testing Docx document.docx")
    
# create example esef file
results_esef = create_xbrl([esef_loaded], xthml_template=xthml_template)
results_esef.save_files("examples/result", True)
results_esef.create_package("examples/result", True)

# create example xbrl file
results_esef = create_xbrl([xbrl_loaded])
results_esef.save_files("examples/result", True)
results_esef.create_package("examples/result", True)

# create example combined report
results = create_xbrl([esef_loaded, ixbrl_xhtml_loaded, xbrl_loaded, loaded_docx_xhtml], xthml_template=xthml_template)
results.save_files("examples/result", True)
results.create_package("examples/result", True)