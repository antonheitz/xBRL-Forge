import logging

from lxml import etree
from typing import Callable, Dict, List

from .ContentDataclasses import AppliedTag, AppliedTagTree, BaseXbrlItem, ContentItem, ImageItem, ListItem, ParagraphItem, TableItem, TitleItem


logger = logging.getLogger(__name__)

XHTML_NAMESPACE: str = "http://www.w3.org/1999/xhtml"

def render_content(content_item: ContentItem, parent: etree.Element, add_text: Callable[[etree.Element, AppliedTagTree, str], None], recusive: Callable[[ContentItem, etree.Element], None], part_tags: List[AppliedTag] = []) -> None:
    logger.debug(f"Creating content elements for type {content_item.type}")
    match content_item.type:
        case ContentItem.TYPE_TITLE:
            title_item: TitleItem = content_item
            # levels 1 - 6 are available
            level = title_item.level
            if level < 1: level = 1
            if level > 6: level = 6
            title_attributes: Dict[str, str] = {}
            if title_item.classes:
                title_attributes["class"] = " ".join(title_item.classes)
            heading: etree.Element = etree.SubElement(parent, f"{{{XHTML_NAMESPACE}}}h{level}", title_attributes)
            tag_tree: AppliedTagTree = AppliedTag.create_tree(part_tags, len(title_item.content))
            add_text(heading, tag_tree, title_item.content)
        case ContentItem.TYPE_PARAGRAPH:
            paragraph_item: ParagraphItem = content_item
            paragraph_attributes: Dict[str, str] = {}
            if paragraph_item.classes:
                paragraph_attributes["class"] = " ".join(paragraph_item.classes)
            paragraph_element: etree.Element = etree.SubElement(parent, f"{{{XHTML_NAMESPACE}}}p", paragraph_attributes)
            tag_tree: AppliedTagTree = AppliedTag.create_tree(part_tags, len(paragraph_item.content))
            add_text(paragraph_element, tag_tree, paragraph_item.content)
        case ContentItem.TYPE_TABLE:
            table_item: TableItem = content_item
            # part tags are ignored for this item, a table can only be tagged as a whole or individual cells
            table_attributes: Dict[str, str] = {}
            if table_item.classes:
                table_attributes["class"] = " ".join(table_item.classes)
            table_element: etree.Element = etree.SubElement(parent, f"{{{XHTML_NAMESPACE}}}table", table_attributes)
            # create a row for every row in the item
            for row_item in table_item.rows:
                row_attributes: Dict[str, str] = {}
                if row_item.classes:
                    row_attributes["class"] = " ".join(row_item.classes)
                row_element: etree.Element = etree.SubElement(table_element, f"{{{XHTML_NAMESPACE}}}tr", row_attributes)
                # create a cell for every cell element, depending on header or not
                for cell_item in row_item.cells:
                    cell_attributes: Dict[str, str] = {}
                    if cell_item.colspan > 1:
                        cell_attributes["colspan"] = str(cell_item.colspan)
                    if cell_item.rowspan > 1:
                        cell_attributes["rowspan"] = str(cell_item.rowspan)
                    if cell_item.classes:
                        cell_attributes["class"] = " ".join(cell_item.classes)
                    if cell_item.header:
                        cell_element: etree.Element = etree.SubElement(row_element, f"{{{XHTML_NAMESPACE}}}th", cell_attributes)
                    else:
                        cell_element: etree.Element = etree.SubElement(row_element, f"{{{XHTML_NAMESPACE}}}td", cell_attributes)
                    # add content to cell
                    for cell_content_item in cell_item.content:
                        recusive(cell_content_item, cell_element)                    
        case ContentItem.TYPE_IMAGE:
            image_item: ImageItem = content_item
            # part tags are ignored for this item, a image can only be tagged as a whole
            image_attributes: Dict[str, str] = {
                "alt": "Image",
                "src": image_item.image_data
            }
            if image_item.alt_text:
                image_attributes["alt"] = image_item.alt_text
            if image_item.classes:
                image_attributes["class"] = " ".join(image_item.classes)
            image_element: etree.Element = etree.SubElement(
                parent, 
                f"{{{XHTML_NAMESPACE}}}img",
                image_attributes
            )
        case ContentItem.TYPE_LIST:
            list_item: ListItem = content_item
            # part tags are ignored for this item, a image can only be tagged as a whole or the content of each list element
            # the container element depends on ordered or unordered
            list_attributes: Dict[str, str] = {}
            if list_item.classes:
                list_attributes["class"] = " ".join(list_item.classes)
            if list_item.ordered:
                list_element: etree.Element = etree.SubElement(parent, f"{{{XHTML_NAMESPACE}}}ol", list_attributes)
            else:
                list_element: etree.Element = etree.SubElement(parent, f"{{{XHTML_NAMESPACE}}}ul", list_attributes)
            # add list items to the list element
            for list_content_item in list_item.elements:
                list_content_item_attributes: Dict[str, str] = {}
                if list_content_item.classes:
                    list_content_item_attributes["class"] = " ".join(list_content_item.classes)
                list_content_element: etree.Element = etree.SubElement(list_element, f"{{{XHTML_NAMESPACE}}}li", list_content_item_attributes)
                # add the content of the element to the list item elemnet
                for list_element_content_item in list_content_item.content:
                    recusive(list_element_content_item, list_content_element)
        case ContentItem.TYPE_BASE_XBRL:
            text_item: BaseXbrlItem = content_item
            if not parent.text:
                parent.text = ""
            parent.text += text_item.content
        case _:
            logger.error(f"Could not convert element of type '{content_item.type}' to XHTML.")