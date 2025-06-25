import json
import logging

from typing import Dict, List, Tuple
from lxml import etree

from .utils import xml_to_string
from .TaxonomyDataclasses import CalculationElement, DefinitionElement, PresentationElement, TaxonomyDocument
from .PackageDataclasses import File
from .._version import version_comment


logger = logging.getLogger(__name__)

TAXONOMY_PACKAGE_NAMESPACE: str = "http://xbrl.org/2016/taxonomy-package"
TAXONOMY_PACKAGE_PREFIX: str = "tp"
XML_NAMESPACE: str = "http://www.w3.org/XML/1998/namespace"
XML_PREFIX: str = "xml"
XSI_NAMESPACE: str = "http://www.w3.org/2001/XMLSchema-instance"
XSI_PREFIX: str = "xsi"
LINKBASE_NAMESPACE: str = "http://www.xbrl.org/2003/linkbase"
LINKBASE_PREFIX: str = "link"
XLINK_NAMESPACE: str = "http://www.w3.org/1999/xlink"
XLINK_PREFIX: str = "xlink"
XBRLI_NAMESPACE: str = "http://www.xbrl.org/2003/instance"
XBRLI_PREFIX: str = "xbrli"
SCHEMA_NAMESPACE: str = "http://www.w3.org/2001/XMLSchema"
SCHEMA_PREFIX: str = "xs"
XBRLDT_NAMESPACE: str = "http://xbrl.org/2005/xbrldt"
XBRLDT_PREFIX: str = "xbrldt"

class TaxonomyProducer:
    taxonomy_document: TaxonomyDocument

    def __init__(cls, document: TaxonomyDocument):
        cls.taxonomy_document = document

    def create_files(cls, reports_folder: File = None, package_extension: str = "zip") -> File:
        # create base folder structure
        root_folder = File(name=f'{"_".join(cls.taxonomy_document.metadata.name.split())}', zip_extension=package_extension)
        if reports_folder:
            root_folder.contained_files.append(reports_folder)
        # create taxonomy files
        taxonomy_folder = root_folder
        for part in cls.taxonomy_document.rewrite_path:
            parent_folder = taxonomy_folder
            taxonomy_folder = File(name=part)
            parent_folder.contained_files.append(taxonomy_folder)
        cls._create_taxonomy_files(taxonomy_folder)
        # create meta information
        meta_inf_folder = File(name="META-INF", contained_files=cls._create_meta_inf_files(package_extension if reports_folder else None))
        root_folder.contained_files.append(meta_inf_folder)
        return root_folder

    def _create_meta_inf_files(cls, package_extension: str = None) -> List[File]:
        # create catalog file
        catalog_namespace: str = "urn:oasis:names:tc:entity:xmlns:xml:catalog"
        catalog_namespace_map = {
            None: catalog_namespace
        }
        catalog_root: etree.Element = etree.Element(f"{{{catalog_namespace}}}catalog", nsmap=catalog_namespace_map)
        rewrite_element: etree.Element = etree.SubElement(
            catalog_root,
            f"{{{catalog_namespace}}}rewriteURI",
            {
                "rewritePrefix": f"../{'/'.join(cls.taxonomy_document.rewrite_path)}/",
                "uriStartString": f"{cls.taxonomy_document.namespace}/"
            }
        ) 

        # create taxonomyPackage file
        tp_namespace_map = {
            TAXONOMY_PACKAGE_PREFIX: TAXONOMY_PACKAGE_NAMESPACE,
            XSI_PREFIX: XSI_NAMESPACE,
            XML_PREFIX: XML_NAMESPACE
        }
        taxonomy_package_element: etree.Element = etree.Element(
            f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}taxonomyPackage",
            {
                f"{{{XML_NAMESPACE}}}lang": "en",
                f"{{{XSI_NAMESPACE}}}schemaLocation": "http://xbrl.org/2016/taxonomy-package http://www.xbrl.org/2016/taxonomy-package.xsd"
            },
            nsmap=tp_namespace_map
        ) 
        version_comment(taxonomy_package_element, 0)
        identifier_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}identifier"
        )
        identifier_element.text = cls.taxonomy_document.namespace
        name_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}name"
        )
        name_element.text = cls.taxonomy_document.metadata.name
        description_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}description"
        )
        description_element.text = cls.taxonomy_document.metadata.description
        version_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}version"
        )
        version_element.text = cls.taxonomy_document.metadata.publication_date
        publisher_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}publisher"
        )
        publisher_element.text = cls.taxonomy_document.metadata.publisher
        publisherUrl_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}publisherURL"
        )
        publisherUrl_element.text = cls.taxonomy_document.metadata.publisher_url
        publisherCountry_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}publisherCountry"
        )
        publisherCountry_element.text = cls.taxonomy_document.metadata.publisher_country
        publicationdate_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}publicationDate"
        )
        publicationdate_element.text = cls.taxonomy_document.metadata.publication_date
        entrypoints_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}entryPoints"
        )
        for entrypoint in cls.taxonomy_document.metadata.entrypoints:
            entrypoint_element: etree.Element = etree.SubElement(
                entrypoints_element,
                f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}entryPoint"
            )
            ep_name_element: etree.Element = etree.SubElement(
                entrypoint_element,
                f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}name"
            )
            ep_name_element.text = entrypoint.name
            ep_description_element: etree.Element = etree.SubElement(
                entrypoint_element,
                f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}description"
            )
            ep_description_element.text = entrypoint.description
            for entrypoint_document in [cls.taxonomy_document.schema_url] + entrypoint.documents:
                ep_document_element: etree.Element = etree.SubElement(
                    entrypoint_element,
                    f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}entryPointDocument",
                    {
                        "href": entrypoint_document
                    }
                )
            ep_langs_element: etree.Element = etree.SubElement(
                entrypoint_element,
                f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}languages"
            )
            ep_lang_element: etree.Element = etree.SubElement(
                ep_langs_element,
                f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}language"
            )
            ep_lang_element.text = entrypoint.language

        return_files: List[File] = [
            File(
                name="catalog.xml", 
                content=xml_to_string(
                    catalog_root, 
                    doctype='<!DOCTYPE catalog PUBLIC "-//OASIS//DTD Entity Resolution XML Catalog V1.0//EN" "http://www.oasis-open.org/committees/entity/release/1.0/catalog.dtd">'
                )
            ),
            File(
                name="taxonomyPackage.xml", 
                content=xml_to_string(
                    taxonomy_package_element
                )
            )
        ]

        if package_extension:
            supported_package_extensions: Dict[str, str] = {
                "zip": "https://xbrl.org/report-package/2023",
                "xbri": "https://xbrl.org/report-package/2023/xbri",
                "xbr": "https://xbrl.org/report-package/2023/xbr"
            }
            return_files.append(File(
                name="reportPackage.json",
                content=json.dumps({
                    "documentInfo": {
                        "documentType": supported_package_extensions.get(package_extension)
                    }
                })
            ))
        return return_files

    def _create_taxonomy_files(cls, taxonomy_folder: File) -> None:
        logger.debug(f"Creating taxonomy schema for namespace {cls.taxonomy_document.namespace}")
        cls._create_schema(taxonomy_folder)
        presentation_linkbase_filename: str = f"{cls.taxonomy_document.files_base_name}_pre.xml"
        logger.debug(f"Creating presentation linkbase {presentation_linkbase_filename}")
        cls._create_linkbase(
            presentation_linkbase_filename,
            taxonomy_folder,
            cls._create_presentation()
        )
        calculation_linkbase_filename: str = f"{cls.taxonomy_document.files_base_name}_cal.xml"
        logger.debug(f"Creating calculation linkbase {calculation_linkbase_filename}")
        cls._create_linkbase(
            calculation_linkbase_filename,
            taxonomy_folder,
            cls._create_calculation()
        )
        definition_linkbase_filename: str = f"{cls.taxonomy_document.files_base_name}_def.xml"
        logger.debug(f"Creating defintion linkbase {definition_linkbase_filename}")
        cls._create_linkbase(
            definition_linkbase_filename,
            taxonomy_folder,
            cls._create_definition()
        )
        for labels_lang in cls.taxonomy_document.labels:
            label_linkbase_filename: str = f"{cls.taxonomy_document.files_base_name}_lab-{labels_lang}.xml"
            logger.debug(f"Creating label linkbase language {labels_lang} {label_linkbase_filename}")
            cls._create_linkbase(
                label_linkbase_filename,
                taxonomy_folder,
                cls._create_label_linkbase(labels_lang)   
            )

    def _create_schema(cls, taxonomy_folder: File) -> None:
        # create base structure
        namespace_map = {
            cls.taxonomy_document.prefix: cls.taxonomy_document.namespace,
            XLINK_PREFIX: XLINK_NAMESPACE,
            LINKBASE_PREFIX: LINKBASE_NAMESPACE,
            XBRLI_PREFIX: XBRLI_NAMESPACE,
            SCHEMA_PREFIX: SCHEMA_NAMESPACE
        }
        for namespace, prefix in cls.taxonomy_document.namespaces.items():
            namespace_map[prefix] = namespace
        schema_root: etree.Element = etree.Element(
            f"{{{SCHEMA_NAMESPACE}}}schema",
            {
                "targetNamespace": cls.taxonomy_document.namespace
            },
            nsmap=namespace_map
        )
        version_comment(schema_root, 0)
        # import schemas
        for import_schema_ns, import_schema_location in cls.taxonomy_document.schema_imports.items():
            logger.debug(f"Creating import element for schema {import_schema_ns}")
            schema_import_element: etree.Element = etree.SubElement(
                schema_root,
                f"{{{SCHEMA_NAMESPACE}}}import",
                {
                    "schemaLocation": import_schema_location,
                    "namespace": import_schema_ns
                }
            )
        # creat annotation elements
        annotation_element: etree.Element = etree.SubElement(
            schema_root,
            f"{{{SCHEMA_NAMESPACE}}}annotation"
        )
        appinfo_element: etree.Element = etree.SubElement(
            annotation_element,
            f"{{{SCHEMA_NAMESPACE}}}appinfo"
        )
        # import taxonomy linkbases
        linkbases: Dict[str, str] = {
            f"{cls.taxonomy_document.files_base_name}_pre.xml": "http://www.xbrl.org/2003/role/presentationLinkbaseRef",
            f"{cls.taxonomy_document.files_base_name}_def.xml": "http://www.xbrl.org/2003/role/definitionLinkbaseRef",
            f"{cls.taxonomy_document.files_base_name}_cal.xml": "http://www.xbrl.org/2003/role/calculationLinkbaseRef"
        }
        for lang in cls.taxonomy_document.labels:
            linkbases[f"{cls.taxonomy_document.files_base_name}_lab-{lang}.xml"] = "http://www.xbrl.org/2003/role/labelLinkbaseRef"
        linkbases.update(cls.taxonomy_document.linkbase_imports)
        for linkbase_href, linkbase_role in linkbases.items():
            logger.debug(f"Creating linkbase reference to {linkbase_href}")
            linkbase_ref_attributes = {
                f"{{{XLINK_NAMESPACE}}}arcrole": "http://www.w3.org/1999/xlink/properties/linkbase",
                f"{{{XLINK_NAMESPACE}}}href": linkbase_href,
                f"{{{XLINK_NAMESPACE}}}type": "simple"
            }
            if linkbase_role:
                linkbase_ref_attributes[f"{{{XLINK_NAMESPACE}}}role"] = linkbase_role
            linkbase_element: etree.Element = etree.SubElement(
                appinfo_element,
                f"{{{LINKBASE_NAMESPACE}}}linkbaseRef",
                linkbase_ref_attributes
            )
        # add roles
        for role in cls.taxonomy_document.roles:
            if not role.schema_location:
                logger.debug(f"Creating taxonomy role {role.uri(cls.taxonomy_document.namespace)}")
                role_element: etree.Element = etree.SubElement(
                    appinfo_element,
                    f"{{{LINKBASE_NAMESPACE}}}roleType",
                    {
                        "id": role.role_id,
                        "roleURI": role.uri(cls.taxonomy_document.namespace)
                    }
                )
                role_name_element: etree.Element = etree.SubElement(
                    role_element,
                    f"{{{LINKBASE_NAMESPACE}}}definition"
                )
                role_name_element.text = role.role_name
                if role.presentation_linkbase:
                    role_link_element: etree.Element = etree.SubElement(
                        role_element,
                        f"{{{LINKBASE_NAMESPACE}}}usedOn"
                    )
                    role_link_element.text = "link:presentationLink"
                if role.calculation_linkbase:
                    role_link_element: etree.Element = etree.SubElement(
                        role_element,
                        f"{{{LINKBASE_NAMESPACE}}}usedOn"
                    )
                    role_link_element.text = "link:calculationLink"
                if role.definition_linkbase:
                    role_link_element: etree.Element = etree.SubElement(
                        role_element,
                        f"{{{LINKBASE_NAMESPACE}}}usedOn"
                    )
                    role_link_element.text = "link:definitionLink"
                role_link_element: etree.Element = etree.SubElement(
                    role_element,
                    f"{{{LINKBASE_NAMESPACE}}}usedOn"
                )
                role_link_element.text = "link:labelLink"
        # add taxonomy elements
        for element_data in cls.taxonomy_document.elements:
            logger.debug(f"Creating taxonomy element {element_data.to_uname(cls.taxonomy_document.namespace)}")
            attributes: Dict[str, str] = {
                    "id": element_data.name,
                    "name": element_data.name,
                    "nillable": "true" if element_data.nillable else "false",
                    "type": element_data.type.to_prefixed_name(cls.taxonomy_document.namespaces)
            }
            if element_data.substitution_group:
                attributes["substitutionGroup"] = element_data.substitution_group.to_prefixed_name(cls.taxonomy_document.namespaces)
            if element_data.period_type:
                attributes[f"{{{XBRLI_NAMESPACE}}}periodType"] = element_data.period_type
            if element_data.abstract:
                attributes["abstract"] = "true"
            if element_data.balance:
                attributes[f"{{{XBRLI_NAMESPACE}}}balance"] = element_data.balance
            if element_data.typed_domain_ref:
                attributes[f"{{{XBRLDT_NAMESPACE}}}typedDomainRef"] = element_data.typed_domain_ref.to_url()
            element_element: etree.Element = etree.SubElement(
                schema_root,
                f"{{{SCHEMA_NAMESPACE}}}element",
                attributes
            ) 
        taxonomy_folder.contained_files.append(File(f"{cls.taxonomy_document.files_base_name}.xsd", content=xml_to_string(schema_root)))

    def _create_linkbase(cls, name: str, taxonomy_folder: File, content_data: Tuple[List[etree.Element], List[str]]) -> None:
        content_elements, used_arcroles = content_data
        namespace_map = {
            LINKBASE_PREFIX: LINKBASE_NAMESPACE,
            XSI_PREFIX: XSI_NAMESPACE,
            XLINK_PREFIX: XLINK_NAMESPACE,
            XML_PREFIX: XML_NAMESPACE
        }
        linkbase_root: etree.Element = etree.Element(
            f"{{{LINKBASE_NAMESPACE}}}linkbase",
            {
                f"{{{XSI_NAMESPACE}}}schemaLocation": "http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd"
            },
            nsmap=namespace_map
        )
        version_comment(linkbase_root, 0)
        # import arc roles if needed
        for arc_role_uri, arc_role_href in cls.taxonomy_document.arc_roles_import.items():
            if arc_role_uri in used_arcroles:
                logger.debug(f"Importing role to linkbase {arc_role_uri}")
                arcrole_ref_element: etree.Element = etree.SubElement(
                    linkbase_root,
                    f"{{{LINKBASE_NAMESPACE}}}arcroleRef",
                    {
                        "arcroleURI": arc_role_uri,
                        f"{{{XLINK_NAMESPACE}}}href": arc_role_href,
                        f"{{{XLINK_NAMESPACE}}}type": "simple"
                    }
                )
        # add content of linkbase
        for content_element in content_elements:
            linkbase_root.append(content_element)
        taxonomy_folder.contained_files.append(File(name, content=xml_to_string(linkbase_root)))

    def _create_presentation(cls) -> Tuple[List[etree.Element], List[str]]:
        # create presentation Linkbase content
        content_elements: List[etree.Element] = []
        used_arc_roles: List[str] = []
        for role_data in cls.taxonomy_document.roles:
            if role_data.presentation_linkbase:
                logger.debug(f"Creating presentation for role {role_data.uri(cls.taxonomy_document.namespace)}")
                role_ref_element: etree.Element = etree.Element(
                    f"{{{LINKBASE_NAMESPACE}}}roleRef",
                    {
                        "roleURI": role_data.uri(cls.taxonomy_document.namespace),
                        f"{{{XLINK_NAMESPACE}}}href": role_data.href(cls.taxonomy_document.files_base_name),
                        f"{{{XLINK_NAMESPACE}}}type": "simple"
                    }
                ) 
                content_elements.append(role_ref_element)
                presentation_link_element: etree.Element = etree.Element(
                    f"{{{LINKBASE_NAMESPACE}}}presentationLink",
                    {
                        f"{{{XLINK_NAMESPACE}}}role": role_data.uri(cls.taxonomy_document.namespace),
                        f"{{{XLINK_NAMESPACE}}}type": "extended"
                    }
                )
                # add elements to the presentation linkbase
                locators: Dict[str, str] = {}
                for child in role_data.presentation_linkbase:
                    locators, child_arc_roles = cls._add_presentation_item(
                        child, 
                        presentation_link_element, 
                        locators
                    )
                    used_arc_roles += child_arc_roles
                content_elements.append(presentation_link_element)
        return content_elements, used_arc_roles
        
    def _add_presentation_item(cls, presentation_element: PresentationElement, parent_element: etree.Element, locators: Dict[str, str], parent_element_locator: str = None) -> Tuple[Dict[str, str], List[str]]:
        used_arcroles: List[str] = []
        element_label, locators = cls._add_element_locator(
            parent_element,
            presentation_element.schema_location,
            presentation_element.element_id,
            locators
        )
        if parent_element_locator:
            arc_attributes = {
                f"{{{XLINK_NAMESPACE}}}type": "arc",
                f"{{{XLINK_NAMESPACE}}}from": parent_element_locator,
                f"{{{XLINK_NAMESPACE}}}to": element_label,
                f"{{{XLINK_NAMESPACE}}}arcrole": presentation_element.arc_role,
                "order": str(presentation_element.order)
            }
            if presentation_element.arc_role:
                used_arcroles.append(presentation_element.arc_role)
            if presentation_element.preferred_label:
                arc_attributes["preferredLabel"] = presentation_element.preferred_label
            presentation_arc_element: etree.Element = etree.SubElement(
                parent_element,
                f"{{{LINKBASE_NAMESPACE}}}presentationArc",
                arc_attributes
            )
        for child in presentation_element.children:
            locators, child_arc_roles = cls._add_presentation_item(
                child, 
                parent_element, 
                locators,
                element_label
            )
            used_arcroles += child_arc_roles
        return locators, used_arcroles
    
    def _create_calculation(cls) -> Tuple[List[etree.Element], List[str]]:
        # create calculation Linkbase
        content_elements: List[etree.Element] = []
        used_arc_roles: List[str] = []
        for role_data in cls.taxonomy_document.roles:
            if role_data.calculation_linkbase:
                logger.debug(f"Creating calculation for role {role_data.uri(cls.taxonomy_document.namespace)}")
                role_ref_element: etree.Element = etree.Element(
                    f"{{{LINKBASE_NAMESPACE}}}roleRef",
                    {
                        "roleURI": role_data.uri(cls.taxonomy_document.namespace),
                        f"{{{XLINK_NAMESPACE}}}href": role_data.href(cls.taxonomy_document.files_base_name),
                        f"{{{XLINK_NAMESPACE}}}type": "simple"
                    }
                ) 
                content_elements.append(role_ref_element)
                calculation_link_element: etree.Element = etree.Element(
                    f"{{{LINKBASE_NAMESPACE}}}calculationLink",
                    {
                        f"{{{XLINK_NAMESPACE}}}role": role_data.uri(cls.taxonomy_document.namespace),
                        f"{{{XLINK_NAMESPACE}}}type": "extended"
                    }
                )
                # add elements to the calculation linkbase
                locators: Dict[str, str] = {}
                for child in role_data.calculation_linkbase:
                    locators, child_arc_roles = cls._add_calculation_item(
                        child, 
                        calculation_link_element, 
                        locators
                    )
                    used_arc_roles += child_arc_roles
                content_elements.append(calculation_link_element)
        return content_elements, used_arc_roles

    def _add_calculation_item(cls, calculation_element: CalculationElement, parent_element: etree.Element, locators: Dict[str, str], parent_element_locator: str = None) -> Tuple[Dict[str, str], List[str]]:
        used_arcroles: List[str] = []
        element_label, locators = cls._add_element_locator(
            parent_element,
            calculation_element.schema_location,
            calculation_element.element_id,
            locators
        )
        if parent_element_locator:
            arc_attributes = {
                f"{{{XLINK_NAMESPACE}}}type": "arc",
                f"{{{XLINK_NAMESPACE}}}from": parent_element_locator,
                f"{{{XLINK_NAMESPACE}}}to": element_label,
                f"{{{XLINK_NAMESPACE}}}arcrole": calculation_element.arc_role,
                "weight": str(calculation_element.weight)
            }
            if calculation_element.arc_role:
                used_arcroles.append(calculation_element.arc_role)
            calculation_arc_element: etree.Element = etree.SubElement(
                parent_element,
                f"{{{LINKBASE_NAMESPACE}}}calculationArc",
                arc_attributes
            )
        for child in calculation_element.children:
            locators, child_arc_roles = cls._add_calculation_item(
                child, 
                parent_element, 
                locators,
                element_label
            )
            used_arcroles += child_arc_roles
        return locators, used_arcroles

    def _create_definition(cls) -> Tuple[List[etree.Element], List[str]]:
        # create definition Linkbase
        content_elements: List[etree.Element] = []
        used_arc_roles: List[str] = []
        for role_data in cls.taxonomy_document.roles:
            if role_data.definition_linkbase:
                logger.debug(f"Creating definition for role {role_data.uri(cls.taxonomy_document.namespace)}")
                role_ref_element: etree.Element = etree.Element(
                    f"{{{LINKBASE_NAMESPACE}}}roleRef",
                    {
                        "roleURI": role_data.uri(cls.taxonomy_document.namespace),
                        f"{{{XLINK_NAMESPACE}}}href": role_data.href(cls.taxonomy_document.files_base_name),
                        f"{{{XLINK_NAMESPACE}}}type": "simple"
                    }
                )
                content_elements.append(role_ref_element)
                definition_link_element: etree.Element = etree.Element(
                    f"{{{LINKBASE_NAMESPACE}}}definitionLink",
                    {
                        f"{{{XLINK_NAMESPACE}}}role": role_data.uri(cls.taxonomy_document.namespace),
                        f"{{{XLINK_NAMESPACE}}}type": "extended"
                    }
                )
                # add elements to the calculation linkbase
                locators: Dict[str, str] = {}
                for child in role_data.definition_linkbase:
                    locators, child_arc_roles = cls._add_definition_item(
                        child, 
                        definition_link_element, 
                        locators
                    )
                    used_arc_roles += child_arc_roles
                content_elements.append(definition_link_element)
        return content_elements, used_arc_roles
    
    def _add_definition_item(cls, definition_element: DefinitionElement, parent_element: etree.Element, locators: Dict[str, str], parent_element_locator: str = None) -> Tuple[Dict[str, str], List[str]]:
        used_arcroles: List[str] = []
        element_label, locators = cls._add_element_locator(
            parent_element,
            definition_element.schema_location,
            definition_element.element_id,
            locators
        )
        if parent_element_locator:
            nsmp = {
                XBRLDT_PREFIX: XBRLDT_NAMESPACE
            }
            arc_attributes = {
                f"{{{XLINK_NAMESPACE}}}type": "arc",
                f"{{{XLINK_NAMESPACE}}}from": parent_element_locator,
                f"{{{XLINK_NAMESPACE}}}to": element_label,
                f"{{{XLINK_NAMESPACE}}}arcrole": definition_element.arc_role
            }
            if definition_element.arc_role:
                used_arcroles.append(definition_element.arc_role)
            if definition_element.closed != None:
                arc_attributes[f"{{{XBRLDT_NAMESPACE}}}closed"] = "true" if definition_element.closed else "false"
            if definition_element.context_element != None:
                arc_attributes[f"{{{XBRLDT_NAMESPACE}}}contextElement"] = definition_element.context_element
            definition_arc_element: etree.Element = etree.SubElement(
                parent_element,
                f"{{{LINKBASE_NAMESPACE}}}definitionArc",
                arc_attributes,
                nsmap=nsmp
            )
        for child in definition_element.children:
            locators, child_arc_roles = cls._add_definition_item(
                child, 
                parent_element, 
                locators,
                element_label
            )
            used_arcroles += child_arc_roles
        return locators, used_arcroles

    def _create_label_linkbase(cls, labels_lang: str) -> Tuple[List[etree.Element], List[str]]:
        label_elements = cls.taxonomy_document.labels[labels_lang]
        label_link_element: etree.Element = etree.Element(
            f"{{{LINKBASE_NAMESPACE}}}labelLink",
            {
                f"{{{XLINK_NAMESPACE}}}role": "http://www.xbrl.org/2003/role/link",
                f"{{{XLINK_NAMESPACE}}}type": "extended"
            }
        )
        locators: Dict[str, str] = {}
        label_id: int = 0
        for label_element_data in label_elements:
            locator_label, locators = cls._add_element_locator(
                label_link_element,
                label_element_data.schema_location,
                label_element_data.element_id,
                locators
            )
            for label_data in label_element_data.labels:
                label_label: str = f"label_{label_id}"
                label_id += 1
                label_element: etree.Element = etree.SubElement(
                    label_link_element,
                    f"{{{LINKBASE_NAMESPACE}}}label",
                    {
                        f"{{{XLINK_NAMESPACE}}}label": label_label,
                        f"{{{XLINK_NAMESPACE}}}role": label_data.label_role,
                        f"{{{XLINK_NAMESPACE}}}type": "resource",
                        f"{{{XML_NAMESPACE}}}lang": labels_lang
                    }
                )
                label_element.text = label_data.label
                label_arc_element: etree.Element = etree.SubElement(
                    label_link_element,
                    f"{{{LINKBASE_NAMESPACE}}}labelArc",
                    {
                        f"{{{XLINK_NAMESPACE}}}type": "arc",
                        f"{{{XLINK_NAMESPACE}}}from": locator_label,
                        f"{{{XLINK_NAMESPACE}}}to": label_label,
                        f"{{{XLINK_NAMESPACE}}}arcrole": "http://www.xbrl.org/2003/arcrole/concept-label",
                        "priority": "100"
                    }
                )
        return [label_link_element], []
        
    def _add_element_locator(cls, parent_element: etree.Element, schema_location: str, element_id: str, located_elements_elements: Dict[str, str]) -> None:
        if schema_location:
            locator_href = f"{schema_location}#{element_id}"
        else:
            locator_href = f"{cls.taxonomy_document.files_base_name}.xsd#{element_id}"
        if locator_href in located_elements_elements:
            return located_elements_elements[locator_href], located_elements_elements
        locator_label: str = f"locator_{len(located_elements_elements.keys())}"
        element_locator: etree.Element = etree.SubElement(
            parent_element,
            f"{{{LINKBASE_NAMESPACE}}}loc",
            {
                f"{{{XLINK_NAMESPACE}}}type": "locator",
                f"{{{XLINK_NAMESPACE}}}href": locator_href,
                f"{{{XLINK_NAMESPACE}}}label": locator_label
            }
        )
        located_elements_elements[locator_href] = locator_label
        return locator_label, located_elements_elements