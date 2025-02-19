from typing import Dict, List
from .ContentDataclasses import ContentDocument, DocumentContext, DocumentUnit
from lxml import etree

XHTML_NAMESPACE: str = "http://www.w3.org/1999/xhtml"
XML_NAMESPACE: str = "http://www.w3.org/XML/1998/namespace"
IXBRL_NAMESPACE: str = "http://www.xbrl.org/2013/inlineXBRL"
LINK_NAMESPACE: str = "http://www.xbrl.org/2003/linkbase" 
XLINK_NAMESPACE: str = "http://www.w3.org/1999/xlink"
INSTANCE_NAMESPACE: str = "http://www.xbrl.org/2003/instance"
DIMENSIONS_NAMESPACE: str = "http://xbrl.org/2006/xbrldi"
XSI_NAMESPACE: str = "http://www.w3.org/2001/XMLSchema-instance"

class BaseProducer:
    content_document: ContentDocument
    tag_id_tracker: Dict[str, etree.Element]
    local_namespace: str
    local_namespace_prefix: str
    local_taxonomy_schema: str

    contexts: Dict[str, 'DocumentContext']
    units: Dict[str, 'DocumentUnit']

    def __init__(cls, document: ContentDocument, local_namespace: str = None, local_namespace_prefix: str = None, local_taxonomy_schema: str = None):
        cls.content_document = document
        cls.tag_id_tracker = {}
        cls.local_namespace = local_namespace
        cls.local_namespace_prefix = local_namespace_prefix
        cls.local_taxonomy_schema = local_taxonomy_schema

        cls.contexts = {}
        cls.units = {}

        for tag in cls.content_document._get_applied_tags():
            # check context
            tag_context: DocumentContext = tag.to_document_context()
            found_context_id: str = None
            for known_context_id, known_context in cls.contexts.items():
                if known_context.euqals(tag_context):
                    found_context_id = known_context_id
                    break
            if not found_context_id:
                found_context_id: str = f"c-{len(cls.contexts.keys())}"
                cls.contexts[found_context_id] = tag_context
            tag.context_id = found_context_id
            # check unit
            if tag.attributes.unit:
                tag_unit: DocumentUnit = tag.attributes.unit
                found_unit_id: str = None
                for known_unit_id, known_unit in cls.units.items():
                    if known_unit.equals(tag_unit):
                        found_unit_id = known_unit_id
                        break
                if not found_unit_id:
                    found_unit_id: str = f"u-{len(cls.units.keys())}"
                    cls.units[found_unit_id] = tag_unit
                tag.attributes.unit_ref = found_unit_id

    def _add_context_elements(cls, parent_element: etree._Element) -> None:
        for context_id, context in cls.contexts.items():
            context_element: etree._Element = etree.SubElement(parent_element, f"{{{INSTANCE_NAMESPACE}}}context", {"id":context_id})
            entity_element: etree._Element = etree.SubElement(context_element, f"{{{INSTANCE_NAMESPACE}}}entity")
            entity_identifier_element: etree._Element = etree.SubElement(
                entity_element, 
                f"{{{INSTANCE_NAMESPACE}}}identifier",
                {
                    "scheme": context.entity_scheme
                }
            )
            entity_identifier_element.text = context.entity
            period_element: etree._Element = etree.SubElement(context_element, f"{{{INSTANCE_NAMESPACE}}}period")
            if context.start_date:
                period_start_element: etree._Element = etree.SubElement(period_element, f"{{{INSTANCE_NAMESPACE}}}startDate")
                period_start_element.text = context.start_date
                period_end_element: etree._Element = etree.SubElement(period_element, f"{{{INSTANCE_NAMESPACE}}}endDate")
                period_end_element.text = context.end_date
            else:
                period_instant_element: etree._Element = etree.SubElement(period_element, f"{{{INSTANCE_NAMESPACE}}}instant")
                period_instant_element.text = context.end_date
            if len(context.dimensions):
                scenario_element: etree._Element = etree.SubElement(context_element, f"{{{INSTANCE_NAMESPACE}}}scenario")
                for dimension in context.dimensions:
                    if dimension.typed_member_value == None:
                        explicit_dimension_element: etree._Element = etree.SubElement(
                            scenario_element, 
                            f"{{{DIMENSIONS_NAMESPACE}}}explicitMember",
                            {
                                "dimension": dimension.axis.to_prefixed_name(
                                    cls.content_document.namespaces, 
                                    cls.local_namespace_prefix
                                )
                            }
                        )
                        explicit_dimension_element.text = dimension.member.to_prefixed_name(
                            cls.content_document.namespaces, 
                            cls.local_namespace_prefix
                        )
                    else:
                        typed_dimension_element: etree._Element = etree.SubElement(
                            scenario_element, 
                            f"{{{DIMENSIONS_NAMESPACE}}}typedMember",
                            {
                                "dimension": dimension.axis.to_prefixed_name(cls.content_document.namespaces, cls.local_namespace_prefix)
                            }
                        )
                        typed_member_element: etree._Element = etree.SubElement(
                            typed_dimension_element,
                            f"{{{dimension.member.namespace}}}{dimension.member.name}"
                        )
                        typed_member_element.text = dimension.typed_member_value

    def _add_unit_elements(cls, parent_element: etree._Element) -> None:
        for unit_id, unit in cls.units.items():
            unit_element: etree._Element = etree.SubElement(
                parent_element, 
                f"{{{INSTANCE_NAMESPACE}}}unit", 
                {"id": unit_id}
            )
            if unit.denominator:
                divide_element: etree._Element = etree.SubElement(unit_element, f"{{{INSTANCE_NAMESPACE}}}divide")
                numerator_element: etree._Element = etree.SubElement(divide_element, f"{{{INSTANCE_NAMESPACE}}}unitNumerator")
                numerator_measure_element: etree._Element = etree.SubElement(numerator_element, f"{{{INSTANCE_NAMESPACE}}}measure")
                numerator_measure_element.text = unit.numerator.to_prefixed_name(cls.content_document.namespaces)
                denominator_element: etree._Element = etree.SubElement(divide_element, f"{{{INSTANCE_NAMESPACE}}}unitDenominator")
                denominator_measure_element: etree._Element = etree.SubElement(denominator_element, f"{{{INSTANCE_NAMESPACE}}}measure")
                denominator_measure_element.text = unit.denominator.to_prefixed_name(cls.content_document.namespaces)
            else:
                measure_element: etree._Element = etree.SubElement(unit_element, f"{{{INSTANCE_NAMESPACE}}}measure")
                measure_element.text = unit.numerator.to_prefixed_name(cls.content_document.namespaces)
