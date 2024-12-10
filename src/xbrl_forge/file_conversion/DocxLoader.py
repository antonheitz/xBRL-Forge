from typing import Dict, List
from docx2python import docx2python
from docx2python.depth_collector import Par
from base64 import b64encode

from ..xbrl_generation.ContentDataclasses import ContentItem, CONTENT_ITEM_TYPES, TitleItem, ParagraphItem, ImageItem
from .BaseLoader import BaseLoader

class DocxLoader(BaseLoader):

    def __init__(cls):
        super(DocxLoader, cls).__init__()
        cls.heading_styles: Dict[str, int] = {
            "Heading1": 1,
            "Heading2": 2
        }

    def load_document(cls, path: str) -> List[ContentItem]:
        with docx2python(path) as docx_content:
            for body_section in docx_content.body_pars:
                cls._add_content_section(body_section, docx_content.images)
        return cls.content
    
    def _add_content_section(cls, section: List[List[List[Par]]], images: Dict[str, bytes]) -> None:
        for body_sub_section in section:
            for body_par_list in body_sub_section:
                for par in body_par_list:
                    par_content: str = "".join([run.text for run in par.runs])
                    if par_content[:4] == "----" and par_content[-4:] == "----":
                        # Image
                        image_name: str = par_content[4:-4].replace("media/", "")
                        image_data: bytes = images[image_name]
                        image_data_b64: str = b64encode(image_data).decode("utf-8")
                        image_format: str = image_name.split(".")[-1].lower()
                        cls.content.append(ImageItem(
                            type=CONTENT_ITEM_TYPES.IMAGE,
                            image_data=f'data:image/{image_format};base64,{image_data_b64}',
                            tags=[]
                        ))
                    elif par.style in cls.heading_styles:
                        # Title in document
                        cls.content.append(TitleItem(
                            type=CONTENT_ITEM_TYPES.TITLE,
                            content=par_content,
                            level=cls.heading_styles.get(par.style, 1),
                            tags=[]
                        ))
                    elif par.style == "ListParagraph":
                        # list element
                        #print(par)
                        pass
                    else:
                        #print(f'"{par.style}"')
                        print(par)
                        # default to paragraph
                        cls.content.append(ParagraphItem(
                            type=CONTENT_ITEM_TYPES.PARAGRAPH,
                            content="".join([run.text for run in par.runs]),
                            tags=[]
                        ))