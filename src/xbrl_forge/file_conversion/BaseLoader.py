from typing import List

from ..xbrl_generation.ContentDataclasses import ContentItem

class BaseLoader():
    content: List[ContentItem]

    def __init__(cls):
        cls.content = []

    def load_document(cls, path: str) -> List[ContentItem]:
        return cls.content