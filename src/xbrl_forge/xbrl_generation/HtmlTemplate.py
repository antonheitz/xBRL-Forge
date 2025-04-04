from typing import Dict, Tuple
from lxml import etree
from .BaseProducer import XHTML_NAMESPACE
from copy import deepcopy
import logging

logger = logging.getLogger(__name__)

XHTML_CONTENT_ROOT_ID: str = "xhtml-content-root"

DEFAULT_TEMPLATE: str = """
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>DEFAULT_TEMPLATE</title>
    <style type="text/css">
        body { background-color: gray; padding-left: 10px; padding-right: 10px; padding-top: 0px; padding-bottom: 0px; font-size: 16px; }
        #xhtml-content-root { background-color: white; box-shadow: 5px 5px 5px black; padding: 10px; width: 90%; }
        h1 { border-bottom: 1px solid black; font-size: 20px; }
        h2, h3, h4, h5, h6 {}
        p {}
        table, th, td { border: 1px solid black; border-collapse: collapse; padding: 5px; }
        img { width: 100%; height: auto; }
        ul {}
        ol { list-style-type: lower-alpha; }
        li {}
    </style>
</head>
<body>
    <div id="xhtml-content-root"></div>
</body>
</html>
"""

def get_xhtml_template(name: str, namespace_map: Dict[str, str], xhtml_template: str) -> Tuple[etree._Element, etree._Element, etree._Element]:
    # try to use provided template, else use default
    if xhtml_template:
        logger.debug("Trying to load custom XHTML Template...")
        try:
            return _load_template(name, namespace_map, xhtml_template)
        except Exception as e:
            logger.error(f"Could not use provided custom XHTML Template: {str(e)}")
    logger.debug("Using default XHTML Template...")
    return _load_template(name, namespace_map, DEFAULT_TEMPLATE)

def _load_template(name: str, namespace_map: Dict[str, str], xhtml_template: str) -> Tuple[etree._Element, etree._Element, etree._Element]:
    template_root: etree._Element = etree.fromstring(xhtml_template)
    xhtml_root: etree._Element = etree.Element(f"{{{XHTML_NAMESPACE}}}html", nsmap=namespace_map)
    child: etree._Element
    for child in template_root:
        xhtml_root.append(child)
    xhtml_body: etree._Element = xhtml_root.find("body", { None: XHTML_NAMESPACE })
    xhtml_title: etree._Element = xhtml_root.find(".//title", { None: XHTML_NAMESPACE })
    xhtml_title.text = name
    xhtml_content_root: etree._Element = xhtml_root.find(".//div[@id='xhtml-content-root']", { None: XHTML_NAMESPACE })
    return xhtml_root, xhtml_body, xhtml_content_root
