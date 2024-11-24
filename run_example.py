import json

from src.xbrl_forge import create_xbrl

with open("examples/stylesheet.css", "r") as f:
    style_data = f.read()
with open("examples/ESEF-ixbrl.json", "r") as f:
    data = json.loads(f.read())

results = create_xbrl(data, styles=style_data)
results.save_file("examples/result", True)

with open("examples/xbrl.json", "r") as f:
    data_xbrl = json.loads(f.read())

results_xbrl = create_xbrl(data_xbrl)
results_xbrl.save_file("examples/result", True)