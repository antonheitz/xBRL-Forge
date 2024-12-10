from typing import List
from docx2python import docx2python

from ..xbrl_generation.ContentDataclasses import ContentItem
from .BaseLoader import BaseLoader

class DocxLoader(BaseLoader):

    def __init__(cls):
        super(cls)

    def load_document(cls, path: str) -> List[ContentItem]:
        with docx2python(path) as docx:
            
        return cls.content