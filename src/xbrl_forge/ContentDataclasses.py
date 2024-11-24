from dataclasses import dataclass
import logging
from typing import Dict, List

from .PackageDataclasses import Tag
from .utils import reversor

logger = logging.getLogger(__name__)

@dataclass
class ContentDocument:
    name: str
    taxonomy_schema: str
    lang: str
    inline: bool
    priority: int
    namespaces: Dict[str, str]
    contexts: Dict[str, 'DocumentContext']
    units: Dict[str, 'DocumentUnit']
    content: List['ContentItem']
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ContentDocument':
        return cls(
            name=data.get("name"),
            taxonomy_schema=data.get("taxonomy_schema"),
            lang=data.get("lang"),
            inline=data.get("inline", True),
            priority=data.get("priority", 100),
            namespaces=data.get("namespaces"),
            contexts={context_id:DocumentContext.from_dict(context_data) for context_id, context_data in data.get("contexts", {}).items()},
            units={unit_id:DocumentUnit.from_dict(unit_data) for unit_id, unit_data in data.get("units", {}).items()},
            content=[ContentItem.from_dict(item_data) for item_data in data.get("content")]
        )
    
    def to_dict(cls) -> dict:
        return {
            "name": cls.name,
            "taxonomy_schema": cls.taxonomy_schema,
            "lang": cls.lang,
            "inline": cls.inline,
            "priority": cls.priority,
            "namespaces": cls.namespaces,
            "contexts": {context_id:context.to_dict() for context_id, context in cls.contexts.items()},
            "units": {unit_id:unit.to_dict() for unit_id, unit in cls.units.items()},
            "content": [content_item.to_dict() for content_item in cls.content],
        }

@dataclass
class DocumentContext:
    entity: str
    entity_scheme: str
    end_date: str
    start_date: str
    dimensions: List['DocumentDimension']

    @classmethod
    def from_dict(cls, data: dict) -> 'DocumentContext':
        return cls(
            entity=data.get("entity"),
            entity_scheme=data.get("entity_scheme"),
            end_date=data.get("end_date"),
            start_date=data.get("start_date", None),
            dimensions=[DocumentDimension.from_dict(dimension) for dimension in data.get("dimensions", [])]
        )
    
    def to_dict(cls) -> dict:
        return {
            "entity": cls.entity,
            "entity_scheme": cls.entity_scheme,
            "end_date": cls.end_date,
            "start_date": cls.start_date,
            "dimensions": [dimension.to_dict() for dimension in cls.dimensions]
        }

@dataclass
class DocumentDimension:
    axis: 'Tag'
    member: 'Tag'

    @classmethod
    def from_dict(cls, data: dict) -> 'DocumentDimension':
        return cls(
            axis=Tag.from_dict(data.get("axis", {})),
            member=Tag.from_dict(data.get("member", {}))
        )
    
    def to_dict(cls) -> dict:
        return {
            "axis": cls.axis.to_dict(),
            "member": cls.member.to_dict()
        }

@dataclass
class DocumentUnit:
    numerator: 'Tag'
    denominator: 'Tag'

    @classmethod
    def from_dict(cls, data: dict) -> 'DocumentUnit':
        return cls(
            numerator=Tag.from_dict(data.get("numerator", {})),
            denominator=Tag.from_dict(data.get("denominator", {})) if data.get("denominator", False) else None
        )

    def to_dict(cls) -> dict:
        return {
            "numerator": cls.numerator.to_dict(),
            "denominator": cls.denominator.to_dict() if cls.denominator else None
        }

class IXBRL_TAG_TYPES:
    NUMERIC: str = "NUMERIC"
    NONNUMERIC: str = "NONNUMERIC"
    
@dataclass
class TagAttributes:
    escape: bool
    decimals: int
    scale: int
    unit: str
    format: Tag
    sign: bool

    @classmethod
    def from_dict(cls, data: dict) -> 'TagAttributes':
        return cls(
            escape=data.get("escape", False),
            decimals=data.get("decimals", 0),
            scale=data.get("scale", 0),
            unit=data.get("unit", ""),
            format=Tag.from_dict(data.get("format", {})),
            sign=data.get("sign", False)
        )
    
    def copy(cls) -> 'TagAttributes':
        return cls.__class__(
            escape=cls.escape,
            decimals=cls.decimals,
            scale=cls.scale,
            unit=cls.unit,
            format=cls.format.copy(),
            sign=cls.sign
        )
    
    def to_dict(cls) -> dict:
        return {
            "escape": cls.escape,
            "decimals": cls.decimals,
            "scale": cls.scale,
            "unit": cls.unit,
            "format": cls.format.to_dict(),
            "sign": cls.sign
        }

@dataclass
class AppliedTag(Tag):
    type: str
    context_id: str
    attributes: TagAttributes
    start_index: int = None
    end_index: int = None

    @classmethod
    def from_dict(cls, data: dict) -> 'AppliedTag':
        return cls(
            namespace=data.get("namespace"),
            name=data.get("name"),
            type=data.get("type"),
            context_id=data.get("context_id"),
            attributes=TagAttributes.from_dict(data.get("attributes", {})),
            start_index=data.get("start_index", None),
            end_index=data.get("end_index", None)
        )

    def contains_tag(cls, compare_tag: 'AppliedTag') -> bool:
        return cls.start_index <= compare_tag.start_index and compare_tag.end_index <= cls.end_index

    def find_intercept(cls, compare_tag: 'AppliedTag') -> int:
        #  |---------------------|         
        #        |--------------------|
        #                        x this index
        if compare_tag.start_index < cls.end_index and cls.end_index < compare_tag.end_index:
            return cls.end_index
        return -1
    
    def split(cls, index: int) -> List['AppliedTag']:
        splitted_tag = cls.__class__(
                namespace=cls.namespace,
                name=cls.name,
                type=cls.type,
                context_id=cls.context_id,
                attributes=cls.attributes.copy(),
                start_index=index,
                end_index=cls.end_index
            )
        cls.end_index = index
        return splitted_tag
        
    def to_dict(cls) -> dict:
        return {
            "namespace": cls.namespace,
            "name": cls.name,
            "type": cls.type,
            "context_id": cls.context_id,
            "attributes": cls.attributes.to_dict(),
            "start_index": cls.start_index,
            "end_index": cls.end_index
        }
    
    @staticmethod
    def _sort(tags: List['AppliedTag']) -> List['AppliedTag']:
        return sorted(tags, key=lambda x: (x.start_index, reversor(x.end_index), x.type))

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
        tree_wrapper: AppliedTagTree = AppliedTagTree(AppliedTag("", "", "", "", {}, 0, content_len), [], True)
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

class CONTENT_ITEM_TYPES:
    TITLE: str = "TITLE"
    PARAGRAPH: str = "PARAGRAPH"
    TABLE: str = "TABLE"
    IMAGE: str = "IMAGE"
    LIST: str = "LIST"
    BASE_XBRL: str = "BASE_XBRL"

@dataclass
class ContentItem:
    type: str
    tags: List[AppliedTag]

    @classmethod
    def from_dict(cls, data: dict) -> 'ContentItem':
        match data.get("type"):
            case CONTENT_ITEM_TYPES.TITLE:
                return TitleItem.from_dict(data)
            case CONTENT_ITEM_TYPES.PARAGRAPH:
                return ParagraphItem.from_dict(data)
            case CONTENT_ITEM_TYPES.TABLE:
                return TableItem.from_dict(data)
            case CONTENT_ITEM_TYPES.IMAGE:
                return ImageItem.from_dict(data)
            case CONTENT_ITEM_TYPES.LIST:
                return ListItem.from_dict(data)
            case CONTENT_ITEM_TYPES.BASE_XBRL:
                return BaseXbrlItem.from_dict(data)
            case _:
                logger.error(f"Content Item Type '{data.get("type")}' is not implemented yet.")
                return cls(
                    data.get("type"), 
                    [AppliedTag.from_dict(tag_data) for tag_data in data.get("tags", [])]
                )

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
    def to_dict(cls) -> dict:
        return {
            "cells": [cell.to_dict() for cell in cls.cells]
        }

@dataclass
class TableCell:
    content: List[ContentItem]
    header: bool

    @classmethod
    def from_dict(cls, data: dict) -> 'TableCell':
        return cls(
            content=[ContentItem.from_dict(content_data) for content_data in data.get("content", [])],
            header=data.get("header", False)
        )
    
    def to_dict(cls) -> dict:
        return {
            "content": [item.to_dict() for item in cls.content],
            "header": cls.header
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
        
    def to_dict(cls) -> dict:
        return {
            "type": cls.type,
            "content": cls.content,
            "tags": [tag.to_dict() for tag in cls.tags]
        }