from lxml import etree
from importlib.metadata import version, PackageNotFoundError


def retrieve_version() -> str:
    try:
        return version(__package__)
    except PackageNotFoundError:
        return "non-packaged"
    
def version_comment(parent: etree._Element, index: int = None) -> None:
    comment: etree._Comment = etree.Comment(f"https://github.com/antonheitz/xBRL-Forge - Version {retrieve_version()}")
    if index == None:
        parent.append(comment)
    else:
        parent.insert(index, comment)