from typing import Dict, List
import mammoth
from lxml import etree
import re

from ..xbrl_generation.ContentDataclasses import ContentItem, ListElement, ListItem, TitleItem, ParagraphItem, ImageItem, TableRow, TableCell, TableItem
from .BaseLoader import BaseLoader

DATA_WRAPPER_NAME: str = "dataWrapper"

class DocxLoader(BaseLoader):

    def __init__(cls):
        super(DocxLoader, cls).__init__()

    def load_document(cls, path: str) -> List[ContentItem]:
        with open(path, "rb") as docx_content:
            result = mammoth.convert_to_html(docx_content)
        data = etree.fromstring(f"<{DATA_WRAPPER_NAME}>{result.value}</{DATA_WRAPPER_NAME}>")
        cls.content = cls._add_to_content(data)
        return cls.content

    def _add_to_content(cls, element: etree._Element) -> List[ContentItem]:
        content: List[ContentItem] = []
        if element.tag == DATA_WRAPPER_NAME:
            for child in element.getchildren():
                content += cls._add_to_content(child)
            return content
        # add paragraph (and image)
        if element.tag == "p":
            # if there is one child image, only add that one
            children: List[etree._Element] = element.getchildren()
            if children and children[0].tag == "img":
                image_element = children[0]
                content.append(ImageItem(
                    type=ContentItem.TYPE_IMAGE,
                    tags=[],
                    image_data=image_element.attrib.get("src", "")
                ))
            else:
                content.append(ParagraphItem(
                    type=ContentItem.TYPE_PARAGRAPH,
                    tags=[],
                    content=element.text
                ))
        # add title
        elif re.match(r"h[0-9]", element.tag):
            content.append(TitleItem(
                type=ContentItem.TYPE_TITLE,
                tags=[],
                content=element.text,
                level=int(element.tag[1]) 
            ))
        # add lists
        elif element.tag in ["ol", "ul"]:
            list_data: List[ListElement] = []
            list_children: List[etree._Element] = element.getchildren()
            for list_child_element in list_children:
                list_data_elemet: ListElement = ListElement([])
                if list_child_element.text:
                    list_data_elemet.content.append(ParagraphItem(
                        type=ContentItem.TYPE_PARAGRAPH,
                        tags=[],
                        content=list_child_element.text
                    ))
                for list_child_sub_child in list_child_element.getchildren():
                    list_data_elemet.content += cls._add_to_content(list_child_sub_child)
                list_data.append(list_data_elemet)
            content.append(ListItem(
                type=ContentItem.TYPE_LIST,
                tags=[],
                elements=list_data,
                ordered=element.tag[0] == "o"
            ))
        # add tables
        elif element.tag == "table":
            table_rows: List[TableRow] = []
            row_element: etree._Element
            for row_element in element.getchildren():
                row_data = TableRow([])
                cell_element: etree.Element
                for cell_element in row_element.getchildren():
                    cell_content: List[ContentItem] = []
                    if cell_element.text:
                        cell_content.append(ParagraphItem(
                            type=ContentItem.TYPE_PARAGRAPH,
                            tags=[],
                            content=cell_element.text
                        ))
                    sub_element: etree._Element
                    for sub_element in cell_element.getchildren():
                        cell_content += cls._add_to_content(sub_element)
                    row_data.cells.append(TableCell(
                        content=cell_content,
                        header=False,
                        rowspan=int(cell_element.attrib.get("rowspan", 1)),
                        colspan=int(cell_element.attrib.get("colspan", 1))
                    ))
                table_rows.append(row_data)
            content.append(TableItem(
                type=ContentItem.TYPE_TABLE,
                tags=[],
                rows=table_rows
            ))
        else:
            raise Exception(f"Unknown Tag: {element.tag}")
        return content