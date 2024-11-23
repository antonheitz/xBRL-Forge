from dataclasses import dataclass
from lxml import etree

class reversor:
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return other.obj == self.obj

    def __lt__(self, other):
        return other.obj < self.obj

def xml_to_string(root: etree.Element, doctype: str = None) -> str:
    if not doctype:
        return etree.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True).decode("utf-8")
    else:
        return etree.tostring(root, encoding="utf-8", doctype=doctype, xml_declaration=True, pretty_print=True).decode("utf-8")