from typing import Dict, Tuple
from lxml import etree
import logging

from .PackageDataclasses import File
from .HtmlDataclasses import AppliedTag, AppliedTagTree, ContentDocument, ContentItem, CONTENT_ITEM_TYPES, ImageItem, ListItem, ParagraphItem, TableItem, TitleItem, IXBRL_TAG_TYPES
from .utils import xml_to_string

logger = logging.getLogger(__name__)

XHTML_NAMESPACE: str = "http://www.w3.org/1999/xhtml"
XML_NAMESPACE: str = "http://www.w3.org/XML/1998/namespace"
IXBRL_NAMESPACE: str = "http://www.xbrl.org/2013/inlineXBRL"
LINK_NAMESPACE: str = "http://www.xbrl.org/2003/linkbase" 
XLINK_NAMESPACE: str = "http://www.w3.org/1999/xlink"
INSTANCE_NAMESPACE: str = "http://www.xbrl.org/2003/instance"
DIMENSIONS_NAMESPACE: str = "http://xbrl.org/2006/xbrldi"

class HtmlProducer:
    content_document: ContentDocument
    tag_id_tracker: Dict[str, etree.Element]
    ixbrl: bool
    styles: str
    local_namespace: str
    local_namespace_prefix: str
    local_taxonomy_schema: str

    def __init__(cls, document: ContentDocument, styles: str = "", local_namespace: str = None, local_namespace_prefix: str = None, local_taxonomy_schema: str = None):
        cls.content_document = document
        cls.tag_id_tracker = {}
        cls.ixbrl = len(cls.content_document.contexts.keys()) > 0
        cls.styles = styles
        cls.local_namespace = local_namespace
        cls.local_namespace_prefix = local_namespace_prefix
        cls.local_taxonomy_schema = local_taxonomy_schema

    def create_html(cls) -> File:
        # Populate Namespaces
        namespace_map = {
            None: XHTML_NAMESPACE,
            "xml": XML_NAMESPACE,
        }

        if cls.ixbrl:
            namespace_map.update({
                "ix": IXBRL_NAMESPACE,
                "link": LINK_NAMESPACE,
                "xlink": XLINK_NAMESPACE,
                "xbrli": INSTANCE_NAMESPACE,
                "xbrldi": DIMENSIONS_NAMESPACE
            })
            namespace_map[cls.local_namespace_prefix] = cls.local_namespace
            for namespace, prefix in cls.content_document.namespaces.items():
                namespace_map[prefix] = namespace

        # Create basic XHTML strucure
        xhtml_root: etree.Element = etree.Element(f"{{{XHTML_NAMESPACE}}}html", nsmap=namespace_map)
        xhtml_head: etree.Element = etree.SubElement(xhtml_root, f"{{{XHTML_NAMESPACE}}}head")
        xhtml_title: etree.Element = etree.SubElement(xhtml_head, f"{{{XHTML_NAMESPACE}}}title")
        xhtml_title.text = cls.content_document.name
        xhtml_body: etree.Element = etree.SubElement(xhtml_root, f"{{{XHTML_NAMESPACE}}}body")
       
        # add basic style information
        xhtml_style: etree.Element = etree.SubElement(xhtml_head, f"{{{XHTML_NAMESPACE}}}style", {"type": "text/css"})
        xhtml_style.text = cls.styles

        if cls.ixbrl:
            # create ixbrl header information
            ixbrl_header_container: etree.Element = etree.SubElement(xhtml_body, f"{{{XHTML_NAMESPACE}}}div", {"style":"display:none;"})
            ixbrl_header: etree.Element = etree.SubElement(ixbrl_header_container, f"{{{IXBRL_NAMESPACE}}}header")
            ixbrl_references: etree.Element = etree.SubElement(ixbrl_header, f"{{{IXBRL_NAMESPACE}}}references", {f"{{{XML_NAMESPACE}}}lang": cls.content_document.lang})
            schema_url = cls.content_document.taxonomy_schema if cls.content_document.taxonomy_schema else cls.local_taxonomy_schema
            schema_ref: etree.Element = etree.SubElement(
                ixbrl_references, 
                f"{{{LINK_NAMESPACE}}}schemaRef",
                {
                    f"{{{XLINK_NAMESPACE}}}href": schema_url,
                    f"{{{XLINK_NAMESPACE}}}type": "simple"
                }
            )
            ixbrl_resources: etree.Element = etree.SubElement(ixbrl_header, f"{{{IXBRL_NAMESPACE}}}resources")
        
            # add contexts to header
            for context_id, context in cls.content_document.contexts.items():
                context_element: etree.Element = etree.SubElement(ixbrl_resources, f"{{{INSTANCE_NAMESPACE}}}context", {"id":context_id})
                entity_element: etree.Element = etree.SubElement(context_element, f"{{{INSTANCE_NAMESPACE}}}entity")
                entity_identifier_element: etree.Element = etree.SubElement(
                    entity_element, 
                    f"{{{INSTANCE_NAMESPACE}}}identifier",
                    {
                        "scheme": context.entity_scheme
                    }
                )
                entity_identifier_element.text = context.entity
                period_element: etree.Element = etree.SubElement(context_element, f"{{{INSTANCE_NAMESPACE}}}period")
                if context.start_date:
                    period_start_element: etree.Element = etree.SubElement(period_element, f"{{{INSTANCE_NAMESPACE}}}startDate")
                    period_start_element.text = context.start_date
                    period_end_element: etree.Element = etree.SubElement(period_element, f"{{{INSTANCE_NAMESPACE}}}endDate")
                    period_end_element.text = context.end_date
                else:
                    period_instant_element: etree.Element = etree.SubElement(period_element, f"{{{INSTANCE_NAMESPACE}}}instant")
                    period_instant_element.text = context.end_date
                if len(context.dimensions):
                    scenario_element: etree.Element = etree.SubElement(context_element, f"{{{INSTANCE_NAMESPACE}}}scenario")
                    for dimension in context.dimensions:
                        dimension_element: etree.Element = etree.SubElement(
                            scenario_element, 
                            f"{{{DIMENSIONS_NAMESPACE}}}explicitMember",
                            {
                                "dimension": dimension.axis.to_prefixed_name(cls.content_document.namespaces, cls.local_namespace_prefix)
                            }
                        )
                        dimension_element.text = dimension.member.to_prefixed_name(cls.content_document.namespaces, cls.local_namespace_prefix)

            # Add Units
            for unit_id, unit in cls.content_document.units.items():
                unit_element: etree.Element = etree.SubElement(ixbrl_resources, f"{{{INSTANCE_NAMESPACE}}}unit", {"id": unit_id})
                if unit.denominator:
                    divide_element: etree.Element = etree.SubElement(unit_element, f"{{{INSTANCE_NAMESPACE}}}divide")
                    numerator_element: etree.Element = etree.SubElement(divide_element, f"{{{INSTANCE_NAMESPACE}}}unitNumerator")
                    numerator_measure_element: etree.Element = etree.SubElement(numerator_element, f"{{{INSTANCE_NAMESPACE}}}measure")
                    numerator_measure_element.text = unit.numerator.to_prefixed_name(cls.content_document.namespaces)
                    denominator_element: etree.Element = etree.SubElement(divide_element, f"{{{INSTANCE_NAMESPACE}}}unitDenominator")
                    denominator_measure_element: etree.Element = etree.SubElement(denominator_element, f"{{{INSTANCE_NAMESPACE}}}measure")
                    denominator_measure_element.text = unit.denominator.to_prefixed_name(cls.content_document.namespaces)
                else:
                    measure_element: etree.Element = etree.SubElement(unit_element, f"{{{INSTANCE_NAMESPACE}}}measure")
                    measure_element.text = unit.numerator.to_prefixed_name(cls.content_document.namespaces)

        # Add html contents
        body_wrapper: etree.Element = etree.SubElement(xhtml_body, f"{{{XHTML_NAMESPACE}}}div", {"class": "main"})
        for content in cls.content_document.content:
            cls._convert_element(content, body_wrapper)

        return File(name=f"{cls.content_document.name}.html", content=xml_to_string(xhtml_root))
    
    def _convert_element(cls, content_item: ContentItem, parent: etree.Element) -> None:
        # check if tags are applied to the whole structure
        complete_tags = [tag for tag in content_item.tags if not tag.end_index and not tag.start_index]
        for tag in complete_tags:
            parent, new_element = cls._create_ixbrl_tag(tag, parent)
            parent = new_element
        # prepare part tags for the application to the text
        part_tags = [tag for tag in content_item.tags if tag.end_index or tag.start_index]
        # add content based on type
        match content_item.type:
            case CONTENT_ITEM_TYPES.TITLE:
                title_item: TitleItem = content_item
                # levels 1 - 6 are available
                level = title_item.level
                if level < 1: level = 1
                if level > 6: level = 6
                heading: etree.Element = etree.SubElement(parent, f"{{{XHTML_NAMESPACE}}}h{level}")
                tag_tree: AppliedTagTree = AppliedTag.create_tree(part_tags, len(title_item.content))
                cls._add_text_with_tags_to_element(heading, tag_tree, title_item.content)
            case CONTENT_ITEM_TYPES.PARAGRAPH:
                paragraph_item: ParagraphItem = content_item
                paragraph_element: etree.Element = etree.SubElement(parent, f"{{{XHTML_NAMESPACE}}}p")
                tag_tree: AppliedTagTree = AppliedTag.create_tree(part_tags, len(paragraph_item.content))
                cls._add_text_with_tags_to_element(paragraph_element, tag_tree, paragraph_item.content)
            case CONTENT_ITEM_TYPES.TABLE:
                table_item: TableItem = content_item
                # part tags are ignored for this item, a table can only be tagged as a whole or individual cells
                table_element: etree.Element = etree.SubElement(parent, f"{{{XHTML_NAMESPACE}}}table")
                # create a row for every row in the item
                for row_item in table_item.rows:
                    row_element: etree.Element = etree.SubElement(table_element, f"{{{XHTML_NAMESPACE}}}tr")
                    # create a cell for every cell element, depending on header or not
                    for cell_item in row_item.cells:
                        if cell_item.header:
                            cell_element: etree.Element = etree.SubElement(row_element, f"{{{XHTML_NAMESPACE}}}th")
                        else:
                            cell_element: etree.Element = etree.SubElement(row_element, f"{{{XHTML_NAMESPACE}}}td")
                        # add content to cell
                        for cell_content_item in cell_item.content:
                            cls._convert_element(cell_content_item, cell_element)                    
            case CONTENT_ITEM_TYPES.IMAGE:
                image_item: ImageItem = content_item
                # part tags are ignored for this item, a image can only be tagged as a whole
                image_element: etree.Element = etree.SubElement(
                    parent, 
                    f"{{{XHTML_NAMESPACE}}}img",
                    {
                        "src": image_item.image_data,
                        "alt": "image"
                    }
                )
            case CONTENT_ITEM_TYPES.LIST:
                list_item: ListItem = content_item
                # part tags are ignored for this item, a image can only be tagged as a whole or the content of each list element
                # the container element depends on ordered or unordered
                if list_item.ordered:
                    list_element: etree.Element = etree.SubElement(parent, f"{{{XHTML_NAMESPACE}}}ol")
                else:
                    list_element: etree.Element = etree.SubElement(parent, f"{{{XHTML_NAMESPACE}}}ul")
                # add list items to the list element
                for list_content_item in list_item.elements:
                    list_content_element: etree.Element = etree.SubElement(list_element, f"{{{XHTML_NAMESPACE}}}li")
                    # add the content of the element to the list item elemnet
                    for list_element_content_item in list_content_item.content:
                        cls._convert_element(list_element_content_item, list_content_element)
            case _:
                logger.error(f"Could not convert element of type '{content_item.type}' to XHTML.")

    def _create_ixbrl_tag(cls, tag: AppliedTag, parent: etree.Element) -> Tuple[etree.Element, etree.Element]:
        prefixed_name: str = tag.to_prefixed_name(cls.content_document.namespaces, cls.local_namespace_prefix)
        tag_id_base = f"{prefixed_name.replace(":", "_")}_{tag.context_id}_-_"
        id_number: int = 0
        # get previous is if known
        previous_element: etree.Element = None
        if tag_id_base in cls.tag_id_tracker:
            previous_element = cls.tag_id_tracker[tag_id_base]
            id_number = int(previous_element.attrib["id"].split("_")[-1]) + 1
        # add tag
        match tag.type:
            case IXBRL_TAG_TYPES.NONNUMERIC:
                if previous_element == None:
                    new_element = etree.SubElement(
                        parent,
                        f"{{{IXBRL_NAMESPACE}}}nonNumeric",
                        {
                            "id": f"{tag_id_base}{id_number}",
                            "name": prefixed_name,
                            "contextRef": tag.context_id,
                            "escape": "true" if tag.attributes.escape else "false"
                        }
                    )
                else:
                    previous_element.attrib["continuedAt"] = f"{tag_id_base}{id_number}"
                    new_element = etree.SubElement(
                        parent,
                        f"{{{IXBRL_NAMESPACE}}}continuation",
                        {
                            "id": f"{tag_id_base}{id_number}"
                        }
                    )
            case IXBRL_TAG_TYPES.NUMERIC:
                new_element = etree.SubElement(
                    parent,
                    f"{{{IXBRL_NAMESPACE}}}nonFraction",
                    {
                        "id": f"{tag_id_base}{id_number}",
                        "name": prefixed_name,
                        "contextRef": tag.context_id,
                        "unitRef": tag.attributes.unit,
                        "scale": str(tag.attributes.scale),
                        "decimals": str(tag.attributes.decimals),
                        "format": tag.attributes.format.to_prefixed_name(cls.content_document.namespaces)
                    }
                )
                if tag.attributes.sign:
                    new_element.attrib["sign"] = "-"
            case _:
                logger.error(f"Could not create tag for '{tag.name}' in Namespace '{tag.namespace}' with type '{tag.type}'.")
                new_element = parent
        # add element to known ids
        cls.tag_id_tracker[tag_id_base] = new_element
        return parent, new_element
    
    def _add_text_with_tags_to_element(cls, element: etree.Element, tag_tree: AppliedTagTree, content: str) -> None:
        start_text: str = content[tag_tree.item.start_index:tag_tree.item.end_index]
        if tag_tree.children:
            start_text = content[tag_tree.item.start_index:tag_tree.children[0].item.start_index]
        element.text = start_text
        for child_index, child_tree in enumerate(tag_tree.children):
            current_element, child_element = cls._create_ixbrl_tag(child_tree.item, element)
            cls._add_text_with_tags_to_element(child_element, child_tree, content)
            # if it is not the last element
            if child_index < len(tag_tree.children) - 1:
                child_element.tail = content[child_tree.item.end_index:tag_tree.children[child_index + 1].item.start_index]
            else:
                child_element.tail = content[child_tree.item.end_index:tag_tree.item.end_index]
