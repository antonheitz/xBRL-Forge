from .xbrl_generation import generate
from .xbrl_generation.PackageDataclasses import File

def create_xbrl(data: dict, styles: str = None) -> File:
    return generate(data, styles)