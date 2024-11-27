import json

from src.xbrl_forge import create_xbrl, load_data

with open("examples/stylesheet.css", "r") as f:
    style_data = f.read()
with open("examples/ESEF-ixbrl.json", "r") as f:
    data = load_data(json.loads(f.read()))
with open("examples/ESEF-ixbrl-2.json", "r") as f:
    data2 = load_data(json.loads(f.read()))

results = create_xbrl([data, data2], styles=style_data)
results.save_files("examples/result", True)
results.create_package("examples/result", True)

with open("examples/xbrl.json", "r") as f:
    data_xbrl = load_data(json.loads(f.read()))

results_xbrl = create_xbrl([data_xbrl])
results_xbrl.save_files("examples/result", True)
results_xbrl.create_package("examples/result", True)