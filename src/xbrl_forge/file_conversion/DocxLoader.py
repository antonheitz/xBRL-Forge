import mammoth
import re
import logging

from typing import List
from lxml import etree

from .BaseLoader import BaseLoader
from ..xbrl_generation.ContentDataclasses import ContentItem, ListElement, ListItem, TitleItem, ParagraphItem, ImageItem, TableRow, TableCell, TableItem


logger = logging.getLogger(__name__)

DATA_WRAPPER_NAME: str = "dataWrapper"

class DocxLoader(BaseLoader):

    def __init__(cls):
        super(DocxLoader, cls).__init__()

    def load_document(cls, path: str) -> List[ContentItem]:
        logger.debug(f"Loading conversion document {path}")
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
                logger.debug(f"Creating ContentItem {ContentItem.TYPE_IMAGE}")
                content.append(ImageItem.new(
                    image_data=image_element.attrib.get("src", ""),
                    alt_text="Image"
                ))
            else:
                logger.debug(f"Creating ContentItem {ContentItem.TYPE_PARAGRAPH}")
                content.append(ParagraphItem.new(
                    content=element.text
                ))
        # add title
        elif re.match(r"h[0-9]", element.tag):
            logger.debug(f"Creating ContentItem {ContentItem.TYPE_TITLE}")
            content.append(TitleItem.new(
                content=element.text,
                level=int(element.tag[1]) 
            ))
        # add lists
        elif element.tag in ["ol", "ul"]:
            logger.debug(f"Creating ContentItem {ContentItem.TYPE_LIST}")
            list_data: List[ListElement] = []
            list_children: List[etree._Element] = element.getchildren()
            for list_child_element in list_children:
                logger.debug("Creating ListElement")
                list_data_elemet: ListElement = ListElement.new(content=[])
                if list_child_element.text:
                    logger.debug(f"Creating ContentItem {ContentItem.TYPE_PARAGRAPH}")
                    list_data_elemet.content.append(ParagraphItem.new(
                        content=list_child_element.text
                    ))
                for list_child_sub_child in list_child_element.getchildren():
                    list_data_elemet.content += cls._add_to_content(list_child_sub_child)
                list_data.append(list_data_elemet)
            content.append(ListItem.new(
                elements=list_data,
                ordered=element.tag[0] == "o"
            ))
        # add tables
        elif element.tag == "table":
            logger.debug(f"Creating ContentItem {ContentItem.TYPE_TABLE}")
            table_rows: List[TableRow] = []
            row_element: etree._Element
            for row_element in element.getchildren():
                logger.debug("Creating TableRow")
                row_data = TableRow.new(cells=[])
                cell_element: etree.Element
                for cell_element in row_element.getchildren():
                    logger.debug("Creating TableCell")
                    cell_content: List[ContentItem] = []
                    if cell_element.text:
                        logger.debug(f"Creating ContentItem {ContentItem.TYPE_PARAGRAPH}")
                        cell_content.append(ParagraphItem.new(
                            content=cell_element.text
                        ))
                    sub_element: etree._Element
                    for sub_element in cell_element.getchildren():
                        cell_content += cls._add_to_content(sub_element)
                    row_data.cells.append(TableCell.new(
                        content=cell_content,
                        header=False,
                        rowspan=int(cell_element.attrib.get("rowspan", 1)),
                        colspan=int(cell_element.attrib.get("colspan", 1))
                    ))
                table_rows.append(row_data)
            content.append(TableItem.new(
                rows=table_rows
            ))
        else:
            raise Exception(f"Unknown Tag: {element.tag}")
        return content