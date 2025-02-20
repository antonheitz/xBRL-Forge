from typing import Dict, Tuple
from lxml import etree
import logging
import math

from .ElementRender import render_content

from .PackageDataclasses import File
from .ContentDataclasses import AppliedTagTree, ContentDocument, ContentItem
from .BaseProducer import BaseProducer, INSTANCE_NAMESPACE, LINK_NAMESPACE, XLINK_NAMESPACE, XML_NAMESPACE, XSI_NAMESPACE, DIMENSIONS_NAMESPACE
from .utils import xml_to_string

logger = logging.getLogger(__name__)

class XbrlProducer(BaseProducer):

    def __init__(cls, document: ContentDocument, local_namespace: str = None, local_namespace_prefix: str = None, local_taxonomy_schema: str = None):
        super().__init__(
            document=document,
            local_namespace=local_namespace,
            local_namespace_prefix=local_namespace_prefix,
            local_taxonomy_schema=local_taxonomy_schema
        )

    def create_xbrl(cls) -> File:
        # Populate Namespaces
        namespace_map = {
            None: INSTANCE_NAMESPACE,
            "xml": XML_NAMESPACE,
            "link": LINK_NAMESPACE,
            "xlink": XLINK_NAMESPACE,
            "xsi": XSI_NAMESPACE,
            "xbrldi": DIMENSIONS_NAMESPACE
        }
        if cls.local_namespace:
            namespace_map[cls.local_namespace_prefix] = cls.local_namespace
        for namespace, prefix in cls.content_document.namespaces.items():
            namespace_map[prefix] = namespace

        # create base xbrl element
        root_element: etree._Element = etree.Element(
            f"{{{INSTANCE_NAMESPACE}}}xbrl",
            nsmap=namespace_map
        )

        #TODO: xsi:schemaLocation="http://mycompany.com/xbrl/taxonomy 102-01-SpecExample.xsd"

        # add schema ref
        cls.schema_url = cls.content_document.taxonomy_schema if cls.content_document.taxonomy_schema else cls.local_taxonomy_schema
        schema_ref: etree._Element = etree.SubElement(
            root_element, 
            f"{{{LINK_NAMESPACE}}}schemaRef",
            {
                f"{{{XLINK_NAMESPACE}}}href": cls.schema_url,
                f"{{{XLINK_NAMESPACE}}}type": "simple"
            }
        )
              
        # add contexts to header
        cls._add_context_elements(root_element)
        
        # Add Units
        cls._add_unit_elements(root_element)
        
        # Add Facts
        for content in cls.content_document.content:
            cls._convert_element(content, root_element)

        return File(name=f"{cls.content_document.name}.xbrl", content=xml_to_string(root_element))
    
    def _convert_element(cls, content_item: ContentItem, root_element: etree.Element) -> None:
        # check tags on structure
        tags = [tag for tag in content_item.tags if not tag.end_index and not tag.start_index]
        # create xbrl tag
        for tag in tags:
            applicable_namespace: str = cls.local_namespace
            if tag.namespace:
                applicable_namespace = tag.namespace
            # numeric fact
            if tag.attributes.unit_ref:
                new_element: etree._Element = etree.SubElement(
                    root_element,
                    f"{{{applicable_namespace}}}{tag.name}",
                    {
                        "contextRef": tag.context_id,
                        "unitRef": tag.attributes.unit_ref,
                        "decimals": str(tag.attributes.decimals)
                    }
                )
                if tag.attributes.nil:
                    new_element.attrib[f"{{{XSI_NAMESPACE}}}nil"] = "true"
                tmp_element: etree._Element = etree.Element("tmp")
                cls._rec_render_content(content_item, tmp_element)
                value = float(tmp_element.text) * (10**tag.attributes.scale)
                new_element.text = str(value)
            # otherwise it must be non-numeric
            else:
                # if it is not a enum
                if not tag.attributes.enumeration_values:
                    # get previous is if known
                    tag_id_base = f"{applicable_namespace}_{tag.name}_{tag.context_id}"
                    tag_element: etree._Element = cls.tag_id_tracker.get(tag_id_base, None)
                    if tag_element == None:
                        tag_element: etree._Element = etree.SubElement(
                            root_element,
                            f"{{{applicable_namespace}}}{tag.name}",
                            {
                                "contextRef": tag.context_id
                            }
                        )
                        cls.tag_id_tracker[tag_id_base] = tag_element
                    if tag.attributes.nil:
                        tag_element.attrib[f"{{{XSI_NAMESPACE}}}nil"] = "true"
                    cls._rec_render_content(
                        content_item,
                        tag_element
                    )
                # enumerations value
                else:
                    enum_tag_element: etree._Element = etree.SubElement(
                        root_element,
                        f"{{{applicable_namespace}}}{tag.name}",
                        {
                            "contextRef": tag.context_id
                        }
                    )
                    enum_tag_element.text = " ".join([enum.value(cls.local_namespace) for enum in tag.attributes.enumeration_values])
    
    def _rec_render_content(cls, content_item: ContentItem, tag_element: etree.Element) -> None:
        render_content(
            content_item,
            tag_element,
            cls._add_text,
            cls._rec_render_content
        )
                
    def _add_text(cls, element: etree.Element, tag_tree: AppliedTagTree, content: str) -> None:
        start_text: str = content[tag_tree.item.start_index:tag_tree.item.end_index]
        if tag_tree.children:
            start_text = content[tag_tree.item.start_index:tag_tree.children[0].item.start_index]
        element.text = start_text
        for child_index, child_tree in enumerate(tag_tree.children):
            current_element, child_element = cls._create_ixbrl_tag(child_tree.item, element)
            cls._add_text(child_element, child_tree, content)
            # if it is not the last element
            if child_index < len(tag_tree.children) - 1:
                child_element.tail = content[child_tree.item.end_index:tag_tree.children[child_index + 1].item.start_index]
            else:
                child_element.tail = content[child_tree.item.end_index:tag_tree.item.end_index]
