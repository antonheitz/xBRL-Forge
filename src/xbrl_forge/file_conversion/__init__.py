import os
from typing import Dict, List

from ..xbrl_generation.ContentDataclasses import ContentDocument, ContentItem
from ..xbrl_generation.InputData import InputData
from .BaseLoader import BaseLoader
from .DocxLoader import DocxLoader

DOCUMENT_LOADERS: Dict[str, BaseLoader] = {
    "docx": DocxLoader()
}

def doc_to_data(path: str, lang: str = "en") -> InputData:
    filename: str = ".".join(os.path.split(path)[-1].split(".")[:-1])
    filetype: str = path.split(".")[-1].lower()
    # load data based on filetype
    # get loading object
    loader: BaseLoader = DOCUMENT_LOADERS.get(filetype, None)
    if not loader:
        raise Exception(f"File Type {filetype} was not implemented yet.")
    content_data: List[ContentItem] = loader.load_document(path)
    # create report object
    report_data: ContentDocument = ContentDocument(
        name=filename,
        taxonomy_schema="",
        lang=lang,
        xhtml=True,
        priority=0,
        namespaces={},
        content=content_data
    )
    return InputData(taxonomy=None, reports=[report_data])