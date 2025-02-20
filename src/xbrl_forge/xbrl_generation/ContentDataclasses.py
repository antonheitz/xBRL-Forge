from dataclasses import dataclass
import logging
from typing import Dict, List, Set, Tuple

from .PackageDataclasses import Tag
from .utils import reversor

logger = logging.getLogger(__name__)

@dataclass
class ContentDocument:
    name: str
    taxonomy_schema: str
    lang: str
    xhtml: bool
    priority: int
    namespaces: Dict[str, str]
    content: List['ContentItem']
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ContentDocument':
        return cls(
            name=data.get("name"),
            taxonomy_schema=data.get("taxonomy_schema"),
            lang=data.get("lang"),
            xhtml=data.get("xhtml", True),
            priority=data.get("priority", 100),
            namespaces=data.get("namespaces"),
            content=[ContentItem.from_dict(item_data) for item_data in data.get("content")]
        )

    @classmethod
    def combine(cls, document_list: List["ContentDocument"]) -> "ContentDocument":
        # sort list by priority
        document_list.sort(key=lambda doc: doc.priority, reverse=True)
        # calculate base attributes if not net by document with highest priority
        taxonomy_schemas: List[str] = [doc.taxonomy_schema for doc in document_list]
        taxonomy_schema: str = taxonomy_schemas[0]
        if None in taxonomy_schemas:
            taxonomy_schema = None
        namespaces: Dict[str, str] = {}
        for doc_namespaces in [doc.namespaces for doc in document_list]:
            if doc_namespaces:
                namespaces.update(doc_namespaces)
        # merge content of each document
        content: List['ContentItem'] = []
        for document in document_list:
            for content_item in document.content:
                content.append(content_item)
        return cls(
            name=document_list[0].name,
            taxonomy_schema=taxonomy_schema,
            lang=document_list[0].lang,
            xhtml=any([doc.xhtml for doc in document_list]),
            priority=document_list[0].priority,
            namespaces=namespaces,
            content=content
        )
    
    def _get_applied_tags(cls) -> List['AppliedTag']:
        tags: List['AppliedTag'] = []
        for content_element in cls.content:       
            tags += content_element._get_applied_tags()
        return tags

    def to_dict(cls) -> dict:
        return {
            "name": cls.name,
            "taxonomy_schema": cls.taxonomy_schema,
            "lang": cls.lang,
            "xhtml": cls.xhtml,
            "priority": cls.priority,
            "namespaces": cls.namespaces,
            "content": [content_item.to_dict() for content_item in cls.content],
        }

@dataclass
class DocumentContext:
    entity: str
    entity_scheme: str
    end_date: str
    start_date: str
    dimensions: List['DocumentDimension']
    
    def euqals(cls, compare_context: "DocumentContext") -> bool:
        if cls.entity != compare_context.entity:
            return False
        if cls.entity_scheme != compare_context.entity_scheme:
            return False
        if cls.end_date != compare_context.end_date:
            return False
        if cls.start_date != compare_context.start_date:
            return False
        if not DocumentDimension.equal_dimensions(cls.dimensions, compare_context.dimensions):
            return False
        return True

@dataclass
class DocumentDimension:
    axis: 'Tag'
    member: 'Tag'
    typed_member_value: str

    @classmethod
    def from_dict(cls, data: dict) -> 'DocumentDimension':
        return cls(
            axis=Tag.from_dict(data.get("axis", {})),
            member=Tag.from_dict(data.get("member", {})),
            typed_member_value=data.get("typed_member_value", None)
        )
    
    def copy(cls) -> 'DocumentDimension':
        return cls.__class__(
            axis=cls.axis.copy(),
            member=cls.member.copy(),
            typed_member_value=cls.typed_member_value
        )
    
    def to_dict(cls) -> dict:
        return {
            "axis": cls.axis.to_dict(),
            "member": cls.member.to_dict(),
            "typed_member_value": cls.typed_member_value
        }

    @staticmethod
    def equal_dimensions(dimensions_a: List["DocumentDimension"], dimensions_b: List["DocumentDimension"]) -> bool:
        axis_unames_a: Dict[str, DocumentDimension] = {dim.axis.to_uname():dim for dim in dimensions_a}
        axis_unames_b: Dict[str, DocumentDimension] = {dim.axis.to_uname():dim for dim in dimensions_b}
        if set(axis_unames_a.keys()) != set(axis_unames_b.keys()):
            return False
        for axis in axis_unames_a.keys():
            if axis_unames_a[axis].typed_member_value != axis_unames_b[axis].typed_member_value:
                return False
            if axis_unames_a[axis].member.to_uname() != axis_unames_b[axis].member.to_uname():
                return False
        return True

@dataclass
class DocumentUnit:
    numerator: 'Tag'
    denominator: 'Tag'
    unit_id: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'DocumentUnit':
        return cls(
            numerator=Tag.from_dict(data.get("numerator", {})),
            denominator=Tag.from_dict(data.get("denominator", {})) if data.get("denominator", False) else None
        )
    
    def copy(cls) -> 'DocumentUnit':
        return cls.__class__(
            numerator=cls.numerator.copy(),
            denominator=cls.denominator.copy() if cls.denominator else None,
            unit_id=cls.unit_id
        )

    def equals(cls, compare_unit: "DocumentUnit") -> bool:
        # compare numerator
        numerator_a: str = None
        if cls.numerator:
            numerator_a = cls.numerator.to_uname()
        numerator_b: str = None
        if compare_unit.numerator:
            numerator_b = compare_unit.numerator.to_uname()
        if numerator_a != numerator_b:
            return False
        # compare denonimator
        denominator_a: str = None
        if cls.denominator:
            denominator_a = cls.denominator.to_uname()
        denominator_b: str = None
        if compare_unit.denominator:
            denominator_b = compare_unit.denominator.to_uname()
        if denominator_a != denominator_b:
            return False
        return True
    
    def to_dict(cls) -> dict:
        return {
            "numerator": cls.numerator.to_dict(),
            "denominator": cls.denominator.to_dict() if cls.denominator else None
        }

@dataclass
class EnumerationValue(Tag):

    @classmethod
    def from_dict(cls, data: dict) -> 'EnumerationValue':
        return cls(
            name = data.get("name"),
            namespace = data.get("namespace")
        )
    
    def value(cls, extension_namespace: str) -> str:
        if cls.namespace:
            return f"{cls.namespace}#{cls.name}"
        return f"{extension_namespace}#{cls.name}"

    def copy(cls) -> 'EnumerationValue':
        return cls.__class__(
            name=cls.name,
            namespace=cls.namespace
        )

    def to_dict(cls) -> dict:
        return {
            "name": cls.name,
            "namespace": cls.namespace
        }

@dataclass
class TagAttributes:
    # only non-numeric
    escape: bool
    enumeration_values: List['EnumerationValue']
    # both
    format: Tag
    nil: bool
    # only numeric
    decimals: int
    scale: int
    unit: DocumentUnit
    sign: bool
    # will be filled automatically
    unit_ref: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'TagAttributes':
        return cls(
            escape=data.get("escape", False),
            enumeration_values=[EnumerationValue.from_dict(d) for d in data.get("enumeration_values", [])],
            format=Tag.from_dict(data.get("format")) if "format" in data and data["format"] else None,
            nil=data.get("nil", False),
            decimals=data.get("decimals", 0),
            scale=data.get("scale", 0),
            unit=DocumentUnit.from_dict(data.get("unit")) if "unit" in data and data["unit"] else None,
            sign=data.get("sign", False)
        )
    
    def copy(cls) -> 'TagAttributes':
        return cls.__class__(
            escape=cls.escape,
            enumeration_values=[ev.copy() for ev in cls.enumeration_values],
            format=cls.format.copy() if cls.format else None,
            nil=cls.nil,
            decimals=cls.decimals,
            scale=cls.scale,
            unit=cls.unit.copy() if cls.unit else None,
            sign=cls.sign
        )
    
    def to_dict(cls) -> dict:
        return {
            "escape": cls.escape,
            "enumeration_values": [ev.to_dict() for ev in cls.enumeration_values],
            "format": cls.format.to_dict() if cls.format else None,
            "nil": cls.nil,
            "decimals": cls.decimals,
            "scale": cls.scale,
            "unit": cls.unit.to_dict() if cls.unit else None,
            "sign": cls.sign
        }

@dataclass
class AppliedTag(Tag):
    attributes: TagAttributes
    entity: str
    entity_scheme: str
    start_date: str
    end_date: str
    dimensions: List['DocumentDimension']
    start_index: int = None
    end_index: int = None
    # this is generated while the production of the file
    context_id: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'AppliedTag':
        return cls(
            namespace=data.get("namespace"),
            name=data.get("name"),
            attributes=TagAttributes.from_dict(data.get("attributes", {})),
            entity=data.get("entity"),
            entity_scheme=data.get("entity_scheme"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            dimensions=[DocumentDimension.from_dict(dd) for dd in data.get("dimensions", [])],
            start_index=data.get("start_index", None),
            end_index=data.get("end_index", None)
        )
    
    @classmethod
    def empty(cls, start_index: int = 0, end_index: int = 0) -> 'AppliedTag':
        return cls(
            namespace="",
            name="",
            attributes={},
            entity="",
            entity_scheme="",
            start_date="",
            end_date="",
            dimensions=[],
            start_index=start_index,
            end_index=end_index
        )
    
    def to_document_context(cls) -> DocumentContext:
        return DocumentContext(
            entity=cls.entity,
            entity_scheme=cls.entity_scheme,
            end_date=cls.end_date,
            start_date=cls.start_date,
            dimensions=cls.dimensions
        )

    def contains_tag(cls, compare_tag: 'AppliedTag') -> bool:
        return cls.start_index <= compare_tag.start_index and compare_tag.end_index <= cls.end_index

    def find_intercept(cls, compare_tag: 'AppliedTag') -> int:
        #  |---------------------|         cls
        #        |--------------------|    compare tag
        #                        x this index
        if compare_tag.start_index < cls.end_index and cls.end_index < compare_tag.end_index:
            return cls.end_index
        return -1
    
    def split(cls, index: int) -> List['AppliedTag']:
        splitted_tag = cls.__class__(
                namespace=cls.namespace,
                name=cls.name,
                attributes=cls.attributes.copy(),
                entity=cls.entity,
                entity_scheme=cls.entity_scheme,
                start_date=cls.start_date,
                end_date=cls.end_date,
                dimensions=[dd.copy() for dd in cls.dimensions],
                start_index=index,
                end_index=cls.end_index,
                context_id=cls.context_id
            )
        cls.end_index = index
        return splitted_tag
        
    def to_dict(cls) -> dict:
        return {
            "namespace": cls.namespace,
            "name": cls.name,
            "attributes": cls.attributes.to_dict(),
            "entity": cls.entity,
            "entity_scheme": cls.entity_scheme,
            "start_date": cls.start_date,
            "end_date": cls.end_date,
            "dimensions": [dd.to_dict() for dd in cls.dimensions],
            "start_index": cls.start_index,
            "end_index": cls.end_index
        }
    
    @staticmethod
    def _sort(tags: List['AppliedTag']) -> List['AppliedTag']:
        return sorted(tags, key=lambda x: (x.start_index, reversor(x.end_index), x.attributes.unit != None))

    @staticmethod
    def create_tree(tags: List['AppliedTag'], content_len: int) -> 'AppliedTagTree':
        tags = AppliedTag._sort(tags)
        current_index: int = 0
        while current_index < len(tags):
            current_tag: AppliedTag = tags[current_index]
            new_tags: List[AppliedTag] = []
            for comparison_tag in tags[current_index + 1:]:
                intercept_index: int = current_tag.find_intercept(comparison_tag)
                if intercept_index != -1:
                    new_tags.append(comparison_tag.split(intercept_index))
            tags += new_tags
            tags = AppliedTag._sort(tags)
            current_index += 1
        tree_wrapper: AppliedTagTree = AppliedTagTree(
            AppliedTag.empty(end_index=content_len), 
            [], 
            True
        )
        for tag in tags:
            tree_wrapper.add_tag(tag)
        return tree_wrapper

@dataclass
class AppliedTagTree:
    item: AppliedTag
    children: List['AppliedTagTree']
    wrapper: bool = False

    def add_tag(cls, new_tag: AppliedTag) -> None:
        # check if it needs to be added to a subchild or granchild (recursive)
        for tag in cls.children:
            if tag.item.contains_tag(new_tag):
                tag.add_tag(new_tag)
                return
        # if not a subchild, add as new child to this one
        cls.children.append(AppliedTagTree(new_tag, []))

@dataclass(kw_only=True)
class ContentItem:
    type: str
    tags: List[AppliedTag]

    TYPE_TITLE: str = "TITLE"
    TYPE_PARAGRAPH: str = "PARAGRAPH"
    TYPE_TABLE: str = "TABLE"
    TYPE_IMAGE: str = "IMAGE"
    TYPE_LIST: str = "LIST"
    TYPE_BASE_XBRL: str = "BASE_XBRL"

    @classmethod
    def from_dict(cls, data: dict) -> 'ContentItem':
        match data.get("type"):
            case cls.TYPE_TITLE:
                return TitleItem.from_dict(data)
            case cls.TYPE_PARAGRAPH:
                return ParagraphItem.from_dict(data)
            case cls.TYPE_TABLE:
                return TableItem.from_dict(data)
            case cls.TYPE_IMAGE:
                return ImageItem.from_dict(data)
            case cls.TYPE_LIST:
                return ListItem.from_dict(data)
            case cls.TYPE_BASE_XBRL:
                return BaseXbrlItem.from_dict(data)
            case _:
                logger.error(f"Content Item Type '{data.get('type')}' is not implemented yet.")
                return cls(
                    data.get("type"), 
                    [AppliedTag.from_dict(tag_data) for tag_data in data.get("tags", [])]
                )

    def update_tags_elements(cls, element_update_map: Dict[str, str]) -> None:
        raise Exception(f"The function update_tags_elements was not implemented for the content type {cls.type}.")

    def _get_applied_tags(cls) -> List[AppliedTag]:
        raise Exception(f"The function _get_applied_tags was not implemented for the content type {cls.type}.")

    def to_dict(cls) -> dict:
        return {
            "type": cls.type,
            "tags": [tag.to_dict() for tag in cls.tags]
        }

@dataclass
class TitleItem(ContentItem):
    content: str
    level: int

    @classmethod
    def from_dict(cls, data: dict) -> 'TitleItem':
        return cls(
            type=data.get("type"),
            content=data.get("content"),
            level=data.get("level"),
            tags=[AppliedTag.from_dict(tag_data) for tag_data in data.get("tags", [])]
        )
    
    def update_tags_elements(cls, element_update_map: Dict[str, str]) -> None:
        for tag in cls.tags:
            if not tag.namespace and tag.name in element_update_map:
                tag.name = element_update_map[tag.name]

    def _get_applied_tags(cls) -> List[AppliedTag]:
        return cls.tags

    def to_dict(cls) -> dict:
        return {
            "type": cls.type,
            "content": cls.content,
            "level": cls.level,
            "tags": [tag.to_dict() for tag in cls.tags]
        }
    
@dataclass
class ParagraphItem(ContentItem):
    content: str

    @classmethod
    def from_dict(cls, data: dict) -> 'TitleItem':
        return cls(
            type=data.get("type"),
            content=data.get("content"),
            tags=[AppliedTag.from_dict(tag_data) for tag_data in data.get("tags", [])]
        )

    def update_tags_elements(cls, element_update_map: Dict[str, str]) -> None:
        for tag in cls.tags:
            if not tag.namespace and tag.name in element_update_map:
                tag.name = element_update_map[tag.name]

    def _get_applied_tags(cls) -> List[AppliedTag]:
        return cls.tags

    def to_dict(cls) -> dict:
        return {
            "type": cls.type,
            "content": cls.content,
            "tags": [tag.to_dict() for tag in cls.tags]
        }
    
@dataclass
class TableItem(ContentItem):
    rows: List['TableRow']

    @classmethod
    def from_dict(cls, data: dict) -> 'TitleItem':
        return cls(
            type=data.get("type"),
            rows=[TableRow.from_dict(row_data) for row_data in data.get("rows", [])],
            tags=[AppliedTag.from_dict(tag_data) for tag_data in data.get("tags", [])]
        )

    def update_tags_elements(cls, element_update_map: Dict[str, str]) -> None:
        for tag in cls.tags:
            if not tag.namespace and tag.name in element_update_map:
                tag.name = element_update_map[tag.name]
        for row in cls.rows:
            row.update_tags_elements(element_update_map)

    def _get_applied_tags(cls) -> List[AppliedTag]:
        tags: List[AppliedTag] = cls.tags
        for row in cls.rows:
            tags += row._get_applied_tags()
        return tags
    
    def to_dict(cls) -> dict:
        return {
            "type": cls.type,
            "rows": [row.to_dict() for row in cls.rows],
            "tags": [tag.to_dict() for tag in cls.tags]
        }

@dataclass
class TableRow:
    cells: List['TableCell']

    @classmethod
    def from_dict(cls, data: dict) -> 'TableRow':
        return cls(
            cells=[TableCell.from_dict(cell_data) for cell_data in data.get("cells", [])]
        )
    
    def update_tags_elements(cls, element_update_map: Dict[str, str]) -> None:
        for cell in cls.cells:
            cell.update_tags_elements(element_update_map)

    def _get_applied_tags(cls) -> List[AppliedTag]:
        tags: List[AppliedTag] = []
        for cell in cls.cells:
            tags += cell._get_applied_tags()
        return tags

    def to_dict(cls) -> dict:
        return {
            "cells": [cell.to_dict() for cell in cls.cells]
        }

@dataclass
class TableCell:
    content: List[ContentItem]
    header: bool
    rowspan: int
    colspan: int

    @classmethod
    def from_dict(cls, data: dict) -> 'TableCell':
        return cls(
            content=[ContentItem.from_dict(content_data) for content_data in data.get("content", [])],
            header=data.get("header", False),
            rowspan=data.get("rowspan", 1),
            colspan=data.get("colspan", 1)
        )
    
    def update_tags_elements(cls, element_update_map: Dict[str, str]) -> None:
        for content_item in cls.content:
            content_item.update_tags_elements(element_update_map)

    def _get_applied_tags(cls) -> List[AppliedTag]:
        tags: List[AppliedTag] = []
        for content_element in cls.content:
            tags += content_element._get_applied_tags()
        return tags
    
    def to_dict(cls) -> dict:
        return {
            "content": [item.to_dict() for item in cls.content],
            "header": cls.header,
            "rowspan": cls.rowspan,
            "colspan": cls.colspan
        }


@dataclass
class ImageItem(ContentItem):
    image_data: str

    @classmethod
    def from_dict(cls, data: dict) -> 'TitleItem':
        return cls(
            type=data.get("type"),
            image_data=data.get("image_data"),
            tags=[AppliedTag.from_dict(tag_data) for tag_data in data.get("tags", [])]
        )
    
    def update_tags_elements(cls, element_update_map: Dict[str, str]) -> None:
        for tag in cls.tags:
            if not tag.namespace and tag.name in element_update_map:
                tag.name = element_update_map[tag.name]

    def _get_applied_tags(cls) -> List[AppliedTag]:
        return cls.tags

    def to_dict(cls) -> dict:
        return {
            "type": cls.type,
            "image_data": cls.image_data,
            "tags": [tag.to_dict() for tag in cls.tags]
        }
    
@dataclass
class ListItem(ContentItem):
    elements: List['ListElement']
    ordered: bool

    @classmethod
    def from_dict(cls, data: dict) -> 'ListItem':
        return cls(
            type=data.get("type"),
            elements=[ListElement.from_dict(element_data) for element_data in data.get("elements", [])],
            ordered=data.get("ordered", False),
            tags=[AppliedTag.from_dict(tag_data) for tag_data in data.get("tags", [])]
        )

    def update_tags_elements(cls, element_update_map: Dict[str, str]) -> None:
        for tag in cls.tags:
            if not tag.namespace and tag.name in element_update_map:
                tag.name = element_update_map[tag.name]
        for element in cls.elements:
            element.update_tags_elements(element_update_map)

    def _get_applied_tags(cls) -> List[AppliedTag]:
        tags: List[AppliedTag] = cls.tags
        for list_element in cls.elements:
            tags += list_element._get_applied_tags()
        return tags
    
    def to_dict(cls) -> dict:
        return {
            "type": cls.type,
            "elements": [element.to_dict() for element in cls.elements],
            "ordered": cls.ordered,
            "tags": [tag.to_dict() for tag in cls.tags]
        }
    
@dataclass
class ListElement:
    content: List[ContentItem]

    @classmethod
    def from_dict(cls, data: dict) -> 'ListElement':
        return cls(
            content=[ContentItem.from_dict(element_content) for element_content in data.get("content", [])]
        )

    def update_tags_elements(cls, element_update_map: Dict[str, str]) -> None:
        for content_item in cls.content:
            content_item.update_tags_elements(element_update_map)

    def _get_applied_tags(cls) -> List[AppliedTag]:
        tags: List[AppliedTag] = []
        for content_element in cls.content:
            tags += content_element._get_applied_tags()
        return tags

    def to_dict(cls) -> dict:
        return {
            "content": [content_item.to_dict() for content_item in cls.content]
        }
    
@dataclass
class BaseXbrlItem(ContentItem):
    content: str

    @classmethod
    def from_dict(cls, data: dict) -> 'BaseXbrlItem':
        return cls(
            type=data.get("type"),
            content=data.get("content"),
            tags=[AppliedTag.from_dict(tag_data) for tag_data in data.get("tags", [])]
        )

    def update_tags_elements(cls, element_update_map: Dict[str, str]) -> None:
        for tag in cls.tags:
            if not tag.namespace and tag.name in element_update_map:
                tag.name = element_update_map[tag.name]
        
    def _get_applied_tags(cls) -> List[AppliedTag]:
        return cls.tags
    
    def to_dict(cls) -> dict:
        return {
            "type": cls.type,
            "content": cls.content,
            "tags": [tag.to_dict() for tag in cls.tags]
        }