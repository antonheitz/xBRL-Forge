from dataclasses import dataclass
from typing import Dict, List

from .PackageDataclasses import Tag



@dataclass
class TaxonomyDocument:
    prefix: str
    metadata: 'TaxonomyMetadata'
    namespaces: Dict[str, str]
    schema_imports: Dict[str, str]
    elements: List['TaxonomyElement']
    linkbase_imports: Dict[str, str]
    arc_roles_import: Dict[str, str]
    roles: List['TaxonomyRole']
    labels: Dict[str, List['LabelElement']]

    @property
    def rewrite_path(cls) -> List[str]:
        return [cls.metadata.publisher_url, "xbrl", cls.metadata.publication_date]

    @property
    def namespace(cls) -> str:
        return f"http://{'/'.join(cls.rewrite_path)}"
    
    @property
    def files_base_name(cls) -> str:
        return f"{cls.prefix}_{cls.metadata.publication_date}"

    @property
    def schema_url(cls) -> str:
        return f"{cls.namespace}/{cls.files_base_name}.xsd"
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TaxonomyDocument':
        return cls(
            prefix=data.get("prefix"), 
            metadata=TaxonomyMetadata.from_dict(data.get("metadata", {})),
            namespaces=data.get("namespaces", {}),
            schema_imports=data.get("schema_imports", {}),
            elements=[TaxonomyElement.from_dict(element_data) for element_data in data.get("elements", [])],
            linkbase_imports=data.get("linkbase_imports", {}),
            arc_roles_import=data.get("arc_roles_import", {}),
            roles=[TaxonomyRole.from_dict(role_data) for role_data in data.get("roles", [])],
            labels={labels_lang:[LabelElement.from_dict(label_element) for label_element in labels_data] for labels_lang, labels_data in data.get("labels", {}).items()}
        )

    def to_dict(cls) -> dict:
        return {
            "prefix": cls.prefix,
            "metadata": cls.metadata.to_dict(),
            "namespaces": cls.namespaces,
            "schema_imports": cls.schema_imports,
            "linkbase_imports": cls.linkbase_imports,
            "elements": [element.to_dict() for element in cls.elements],
            "arc_roles_import": cls.arc_roles_import,
            "roles": [role.to_dict() for role in cls.roles],
            "labels": {labels_lang:[label_element.to_dict() for label_element in labels_data] for labels_lang, labels_data in cls.labels.items()}
        }

@dataclass
class TaxonomyMetadata:
    name: str
    description: str
    publisher: str
    publisher_url: str
    publication_date: str
    publisher_country: str
    entrypoints: List['Entrypoint']

    @classmethod
    def from_dict(cls, data: dict) -> 'TaxonomyMetadata':
        return cls(
            name=data.get("name"),
            description=data.get("description"), 
            publisher=data.get("publisher"),
            publisher_url=data.get("publisher_url"),
            publisher_country=data.get("publisher_country"),
            publication_date=data.get("publication_date"),
            entrypoints=[Entrypoint.from_dict(entrypoint) for entrypoint in data.get("entrypoints", [])]
        )

    def to_dict(cls) -> dict:
        return {
            "name": cls.name,
            "description": cls.description,
            "publisher": cls.publisher,
            "publisher_url": cls.publisher_url,
            "publisher_country": cls.publisher_country,
            "publication_date": cls.publication_date,
            "entrypoint": [entrypoint.to_dict() for entrypoint in cls.entrypoints]
        }

@dataclass
class Entrypoint:
    name: str
    description: str
    documents: List[str]
    language: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Entrypoint':
        return cls(
            name=data.get("name"),
            description=data.get("description"),
            documents=data.get("documents", []),
            language=data.get("language")
        )

    def to_dict(cls) -> dict:
        return {
            "name": cls.name,
            "description": cls.description,
            "documents": cls.documents,
            "language": cls.language
        }
    
@dataclass
class TaxonomyElement:
    balance: str
    period_type: str
    name: str
    nillable: bool
    abstract: bool
    substitution_group: Tag
    type: Tag

    @classmethod
    def from_dict(cls, data: dict) -> 'TaxonomyElement':
        return cls(
            balance=data.get("balance"),
            period_type=data.get("period_type"),
            name=data.get("name"),
            nillable=data.get("nillable"),
            abstract=data.get("abstract"),
            substitution_group=Tag.from_dict(data.get("substitution_group", {})),
            type=Tag.from_dict(data.get("type", {})),
        )

    def to_dict(cls) -> dict:
        return {
            "balance": cls.balance,
            "period_type": cls.period_type,
            "name": cls.name,
            "nillable": cls.nillable,
            "abstract": cls.abstract,
            "substitution_group": cls.substitution_group.to_dict(),
            "type": cls.type.to_dict()
        }

@dataclass
class TaxonomyRole:
    role_name: str
    role_id: str
    role_uri: str
    schema_location: str
    presentation_linkbase: List['PresentationElement']
    definition_linkbase: List['DefinitionElement']
    calculation_linkbase: List['CalculationElement']

    @classmethod
    def from_dict(cls, data: dict) -> 'TaxonomyRole':
        return cls(
            role_name=data.get("role_name"),
            role_id=data.get("role_id"),
            role_uri=data.get("role_uri"),
            schema_location=data.get("schema_location"),
            presentation_linkbase=[PresentationElement.from_dict(element) for element in data.get("presentation_linkbase", [])],
            definition_linkbase=[DefinitionElement.from_dict(element) for element in data.get("definition_linkbase", [])],
            calculation_linkbase=[CalculationElement.from_dict(element) for element in data.get("calculation_linkbase", [])]
        )

    def uri(cls, taxonomy_namespace: str) -> str:
        if not cls.role_uri:
            return f"{taxonomy_namespace.rstrip('/')}/roles/{cls.role_id}"
        return cls.role_uri
    
    def href(cls, file_base_name: str) -> str:
        if not cls.schema_location:
            return f"{file_base_name}.xsd#{cls.role_id}"
        return f"{cls.schema_location}#{cls.role_id}"

    def to_dict(cls) -> dict:
        return {
            "role_name": cls.role_name,
            "role_id": cls.role_id,
            "schema_location": cls.schema_location,
            "presentation_linkbase": [element.to_dict() for element in cls.presentation_linkbase],
            "definition_linkbase": [element.to_dict() for element in cls.definition_linkbase],
            "calculation_linkbase": [element.to_dict() for element in cls.calculation_linkbase]
        }

@dataclass
class LinkbaseElement:
    element_id: str
    schema_location: str
    arc_role: str
    children: List['LinkbaseElement']

    @classmethod
    def from_dict(cls, data: dict) -> 'LinkbaseElement':
        return cls(
            element_id=data.get("element_id"),
            schema_location=data.get("schema_location"),
            arc_role=data.get("arc_role"),
            children=[LinkbaseElement.from_dict(child) for child in data.get("children", [])]
        )
    
    def to_dict(cls) -> dict:
        return {
            "element_id": cls.element_id,
            "schema_location": cls.schema_location,
            "arc_role": cls.arc_role,
            "children": [child.to_dict() for child in cls.children]
        }
    
@dataclass
class PresentationElement(LinkbaseElement):
    order: int
    preferred_label: str
    children: List['PresentationElement']

    @classmethod
    def from_dict(cls, data: dict) -> 'PresentationElement':
        return cls(
            element_id=data.get("element_id"),
            schema_location=data.get("schema_location"),
            arc_role=data.get("arc_role"),
            order=data.get("order", 0),
            preferred_label=data.get("preferred_label"),
            children=[PresentationElement.from_dict(child) for child in data.get("children", [])]
        )

    def to_dict(cls) -> dict:
        return {
            "element_id": cls.element_id,
            "schema_location": cls.schema_location,
            "arc_role": cls.arc_role,
            "order": cls.order,
            "preferred_label": cls.preferred_label,
            "children": [child.to_dict() for child in cls.children]
        }

@dataclass
class CalculationElement(LinkbaseElement):
    weight: int
    children: List['CalculationElement']

    @classmethod
    def from_dict(cls, data: dict) -> 'CalculationElement':
        return cls(
            element_id=data.get("element_id"),
            schema_location=data.get("schema_location"),
            arc_role=data.get("arc_role"),
            weight=data.get("weight", 0),
            children=[CalculationElement.from_dict(child) for child in data.get("children", [])]
        )

    def to_dict(cls) -> dict:
        return {
            "element_id": cls.element_id,
            "schema_location": cls.schema_location,
            "arc_role": cls.arc_role,
            "weight": cls.weight,
            "children": [child.to_dict() for child in cls.children]
        }
    
@dataclass
class DefinitionElement(LinkbaseElement):
    context_element: str
    closed: bool
    children: List['DefinitionElement']

    @classmethod
    def from_dict(cls, data: dict) -> 'DefinitionElement':
        return cls(
            element_id=data.get("element_id"),
            schema_location=data.get("schema_location"),
            arc_role=data.get("arc_role"),
            context_element=data.get("context_element"),
            closed=data.get("closed"),
            children=[DefinitionElement.from_dict(child) for child in data.get("children", [])]
        )

    def to_dict(cls) -> dict:
        return {
            "element_id": cls.element_id,
            "schema_location": cls.schema_location,
            "arc_role": cls.arc_role,
            "context_element": cls.context_element,
            "closed": cls.closed,
            "children": [child.to_dict() for child in cls.children]
        }

@dataclass
class LabelElement:
    element_id: str
    schema_location: str
    lables: List['LabelData']
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LabelElement':
        return cls(
            element_id=data.get("element_id"),
            schema_location=data.get("schema_location"),
            lables=[LabelData.from_dict(label_data) for label_data in data.get("lables", [])]
        )
    
    def to_dict(cls) -> dict:
        return {
            "element_id": cls.element_id,
            "schema_location": cls.schema_location,
            "labels": [label_data.to_dict() for label_data in cls.lables]
        }

@dataclass
class LabelData:
    label_role: str
    label: str

    @classmethod
    def from_dict(cls, data: dict) -> 'LabelData':
        return cls(
            label_role=data.get("label_role"),
            label=data.get("label")
        )
    
    def to_dict(cls) -> dict:
        return {
            "label_role": cls.label_role,
            "label": cls.label
        }