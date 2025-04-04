from typing import Dict, Tuple
from lxml import etree
import logging


from .ElementRender import render_content

from .PackageDataclasses import File
from .ContentDataclasses import AppliedTag, AppliedTagTree, ContentDocument, ContentItem
from .BaseProducer import BaseProducer, XHTML_NAMESPACE, XML_NAMESPACE, IXBRL_NAMESPACE, LINK_NAMESPACE, XLINK_NAMESPACE, INSTANCE_NAMESPACE, DIMENSIONS_NAMESPACE, XSI_NAMESPACE
from .utils import xml_to_string
from .HtmlTemplate import get_xhtml_template

logger = logging.getLogger(__name__)

class HtmlProducer(BaseProducer):
    ixbrl: bool
    xhtml_template: str

    def __init__(cls, document: ContentDocument, xthml_template: str = "", local_namespace: str = None, local_namespace_prefix: str = None, local_taxonomy_schema: str = None):
        super().__init__(
            document=document, 
            local_namespace=local_namespace, 
            local_namespace_prefix=local_namespace_prefix,
            local_taxonomy_schema=local_taxonomy_schema
        )
        cls.ixbrl = len(cls.contexts) > 0
        cls.xhtml_template = xthml_template

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
                "xbrldi": DIMENSIONS_NAMESPACE,
                "xsi": XSI_NAMESPACE
            })
            if cls.local_namespace:
                namespace_map[cls.local_namespace_prefix] = cls.local_namespace
            for namespace, prefix in cls.content_document.namespaces.items():
                namespace_map[prefix] = namespace

        # Create basic XHTML strucure
        xhtml_root, xhtml_body, xhtml_content_root = get_xhtml_template(
            name = cls.content_document.name,
            namespace_map = namespace_map,
            xhtml_template = cls.xhtml_template
        )

        if cls.ixbrl:
            # create ixbrl header information
            ixbrl_header_container: etree._Element = etree.SubElement(xhtml_body, f"{{{XHTML_NAMESPACE}}}div", {"style":"display:none;"})
            cls.ixbrl_header: etree._Element = etree.SubElement(ixbrl_header_container, f"{{{IXBRL_NAMESPACE}}}header")
            cls.ixbrl_hidden: etree._Element = None
            ixbrl_references: etree._Element = etree.SubElement(cls.ixbrl_header, f"{{{IXBRL_NAMESPACE}}}references", {f"{{{XML_NAMESPACE}}}lang": cls.content_document.lang})
            cls.schema_url = cls.content_document.taxonomy_schema if cls.content_document.taxonomy_schema else cls.local_taxonomy_schema
            schema_ref: etree._Element = etree.SubElement(
                ixbrl_references, 
                f"{{{LINK_NAMESPACE}}}schemaRef",
                {
                    f"{{{XLINK_NAMESPACE}}}href": cls.schema_url,
                    f"{{{XLINK_NAMESPACE}}}type": "simple"
                }
            )
            ixbrl_resources: etree._Element = etree.SubElement(cls.ixbrl_header, f"{{{IXBRL_NAMESPACE}}}resources")
        
            # add contexts to header
            cls._add_context_elements(ixbrl_resources)
            
            # Add Units
            cls._add_unit_elements(ixbrl_resources)
            
        # Add html contents
        for content in cls.content_document.content:
            cls._convert_element(content, xhtml_content_root)

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
        render_content(
            content_item,
            parent,
            cls._add_text_with_tags_to_element,
            cls._convert_element,
            part_tags
        )

    def _create_ixbrl_tag(cls, tag: AppliedTag, parent: etree.Element) -> Tuple[etree.Element, etree.Element]:
        prefixed_name: str = tag.to_prefixed_name(cls.content_document.namespaces, cls.local_namespace_prefix)
        tag_id_base = f'{prefixed_name.replace(":", "_")}_{tag.context_id}_-_'
        id_number: int = 0
        # get previous is if known
        previous_element: etree._Element = None
        if tag_id_base in cls.tag_id_tracker:
            previous_element = cls.tag_id_tracker[tag_id_base]
            id_number = int(previous_element.attrib["id"].split("_")[-1]) + 1
        # add tag
        # if the tag attributes contain a unit, then it must be a numeric tag
        if tag.attributes.unit_ref:
            new_element: etree._Element = etree.SubElement(
                parent,
                f"{{{IXBRL_NAMESPACE}}}nonFraction",
                {
                    "id": f"{tag_id_base}{id_number}",
                    "name": prefixed_name,
                    "contextRef": tag.context_id,
                    "unitRef": tag.attributes.unit_ref,
                    "scale": str(tag.attributes.scale),
                    "decimals": str(tag.attributes.decimals)
                }
            )
            if tag.attributes.sign:
                new_element.attrib["sign"] = "-"
            if tag.attributes.format:
                new_element.attrib["format"] = tag.attributes.format.to_prefixed_name(cls.content_document.namespaces)
            if tag.attributes.nil:
                new_element.attrib[f"{{{XSI_NAMESPACE}}}nil"] = "true"
        # otherwise it must be a non-numeric tag
        else:
            # if its not an enum, it can be tagged inline
            if not tag.attributes.enumeration_values:
                if previous_element == None:
                    new_element = etree.SubElement(
                        parent,
                        f"{{{IXBRL_NAMESPACE}}}nonNumeric",
                        {
                            "id": f"{tag_id_base}{id_number}",
                            "name": prefixed_name,
                            "contextRef": tag.context_id
                        }
                    )
                    if tag.attributes.escape:
                        new_element.attrib["escape"] = "true"
                    if tag.attributes.format:
                        new_element.attrib["format"] = tag.attributes.format.to_prefixed_name(cls.content_document.namespaces)
                    if tag.attributes.nil:
                        new_element.attrib[f"{{{XSI_NAMESPACE}}}nil"] = "true"
                else:
                    previous_element.attrib["continuedAt"] = f"{tag_id_base}{id_number}"
                    new_element = etree.SubElement(
                        parent,
                        f"{{{IXBRL_NAMESPACE}}}continuation",
                        {
                            "id": f"{tag_id_base}{id_number}"
                        }
                    )
            # enumerations
            else:
                # check if the hidden element already exists
                if cls.ixbrl_hidden == None:
                    cls.ixbrl_hidden = etree.SubElement(
                        cls.ixbrl_header,
                        f"{{{IXBRL_NAMESPACE}}}hidden"
                    )
                hidden_tag_element: etree._Element = etree.SubElement(
                    cls.ixbrl_hidden,
                    f"{{{IXBRL_NAMESPACE}}}nonNumeric",
                    {
                        "id": f"{tag_id_base}{id_number}",
                        "name": prefixed_name,
                        "contextRef": tag.context_id
                    }
                )
                # add enum values
                hidden_tag_element.text = " ".join([enum.value(cls.local_namespace) for enum in tag.attributes.enumeration_values])
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
