from typing import Dict, List
from lxml import etree

from .utils import xml_to_string
from .TaxonomyDataclasses import CalculationElement, DefinitionElement, PresentationElement, TaxonomyDocument, TaxonomyElement
from .PackageDataclasses import File, Tag

class TaxonomyProducer:
    taxonomy_document: TaxonomyDocument

    def __init__(cls, document: TaxonomyDocument):
        cls.taxonomy_document = document

    def create_files(cls, reports: List[File] = None) -> File:
        # create base folder structure
        root_folder = File(name=f"{"_".join(cls.taxonomy_document.metadata.name.split())}")
        if reports:
            reports_folder = File(name="reports", contained_files=reports)
            root_folder.contained_files.append(reports_folder)
        # create taxonomy files
        taxonomy_folder = root_folder
        for part in cls.taxonomy_document.rewrite_path:
            parent_folder = taxonomy_folder
            taxonomy_folder = File(name=part)
            parent_folder.contained_files.append(taxonomy_folder)
        cls._create_taxonomy_files(taxonomy_folder)
        # create meta information
        meta_inf_folder = File(name="META-INF", contained_files=cls._create_meta_inf_files())
        root_folder.contained_files.append(meta_inf_folder)
        return root_folder

    def _create_meta_inf_files(cls) -> List[File]:
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
        tp_namespace: str = "http://xbrl.org/2016/taxonomy-package"
        xsi_namespace: str = "http://www.w3.org/2001/XMLSchema-instance"
        xml_namespace: str = "http://www.w3.org/XML/1998/namespace"
        tp_namespace_map = {
            "tp": tp_namespace,
            "xsi": xsi_namespace,
            "xml": xml_namespace
        }
        taxonomy_package_element: etree.Element = etree.Element(
            f"{{{tp_namespace}}}taxonomyPackage",
            {
                f"{{{xml_namespace}}}lang": "en",
                f"{{{xsi_namespace}}}schemaLocation": "http://xbrl.org/2016/taxonomy-package http://www.xbrl.org/2016/taxonomy-package.xsd"
            },
            nsmap=tp_namespace_map
        ) 
        identifier_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{tp_namespace}}}identifier"
        )
        identifier_element.text = cls.taxonomy_document.namespace
        name_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{tp_namespace}}}name"
        )
        name_element.text = cls.taxonomy_document.metadata.name
        description_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{tp_namespace}}}description"
        )
        description_element.text = cls.taxonomy_document.metadata.description
        version_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{tp_namespace}}}version"
        )
        version_element.text = cls.taxonomy_document.metadata.publication_date
        publisher_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{tp_namespace}}}publisher"
        )
        publisher_element.text = cls.taxonomy_document.metadata.publisher
        publisherUrl_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{tp_namespace}}}publisherURL"
        )
        publisherUrl_element.text = cls.taxonomy_document.metadata.publisher_url
        publisherCountry_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{tp_namespace}}}publisherCountry"
        )
        publisherCountry_element.text = cls.taxonomy_document.metadata.publisher_country
        publicationdate_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{tp_namespace}}}publicationDate"
        )
        publicationdate_element.text = cls.taxonomy_document.metadata.publication_date
        entrypoints_element: etree.Element = etree.SubElement(
            taxonomy_package_element,
            f"{{{tp_namespace}}}entryPoints"
        )
        for entrypoint in cls.taxonomy_document.metadata.entrypoints:
            entrypoint_element: etree.Element = etree.SubElement(
                entrypoints_element,
                f"{{{tp_namespace}}}entryPoint"
            )
            ep_name_element: etree.Element = etree.SubElement(
                entrypoint_element,
                f"{{{tp_namespace}}}name"
            )
            ep_name_element.text = entrypoint.name
            ep_description_element: etree.Element = etree.SubElement(
                entrypoint_element,
                f"{{{tp_namespace}}}description"
            )
            ep_description_element.text = entrypoint.description
            for entrypoint_document in [cls.taxonomy_document.schema_url] + entrypoint.documents:
                ep_document_element: etree.Element = etree.SubElement(
                    entrypoint_element,
                    f"{{{tp_namespace}}}entryPointDocument",
                    {
                        "href": entrypoint_document
                    }
                )
            ep_langs_element: etree.Element = etree.SubElement(
                entrypoint_element,
                f"{{{tp_namespace}}}languages"
            )
            ep_lang_element: etree.Element = etree.SubElement(
                ep_langs_element,
                f"{{{tp_namespace}}}language"
            )
            ep_lang_element.text = entrypoint.language

        return [
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

    def _create_taxonomy_files(cls, taxonomy_folder: File) -> None:
        cls._create_schema(taxonomy_folder)
        cls._create_presentation(taxonomy_folder)
        cls._create_calculation(taxonomy_folder)
        cls._create_definition(taxonomy_folder)
        for labels_lang in cls.taxonomy_document.labels:
            cls._create_label_linkbase(taxonomy_folder, labels_lang)

    def _create_schema(cls, taxonomy_folder: File) -> None:
        # create base structure
        xlink_namespace: str = "http://www.w3.org/1999/xlink"
        linkbase_namespace: str = "http://www.xbrl.org/2003/linkbase"
        xbrli_namespace: str = "http://www.xbrl.org/2003/instance"
        xs_namespace: str = "http://www.w3.org/2001/XMLSchema"
        namespace_map = {
            cls.taxonomy_document.prefix: cls.taxonomy_document.namespace,
            "xlink": xlink_namespace,
            "link": linkbase_namespace,
            "xbrli": xbrli_namespace,
            "xs": xs_namespace
        }
        for namespace, prefix in cls.taxonomy_document.namespaces.items():
            namespace_map[prefix] = namespace
        schema_root: etree.Element = etree.Element(
            f"{{{xs_namespace}}}schema",
            {
                "targetNamespace": cls.taxonomy_document.namespace
            },
            nsmap=namespace_map
        )
        # import schemas
        for import_schema_ns, import_schema_location in cls.taxonomy_document.namespace_imports.items():
            namespace_import_element: etree.Element = etree.SubElement(
                schema_root,
                f"{{{xs_namespace}}}import",
                {
                    "schemaLocation": import_schema_location,
                    "namespace": import_schema_ns
                }
            )
        # creat annotation elements
        annotation_element: etree.Element = etree.SubElement(
            schema_root,
            f"{{{xs_namespace}}}annotation"
        )
        appinfo_element: etree.Element = etree.SubElement(
            annotation_element,
            f"{{{xs_namespace}}}appinfo"
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
            linkbase_ref_attributes = {
                f"{{{xlink_namespace}}}arcrole": "http://www.w3.org/1999/xlink/properties/linkbase",
                f"{{{xlink_namespace}}}href": linkbase_href,
                f"{{{xlink_namespace}}}type": "simple"
            }
            if linkbase_role:
                linkbase_ref_attributes[f"{{{xlink_namespace}}}role"] = linkbase_role
            linkbase_element: etree.Element = etree.SubElement(
                appinfo_element,
                f"{{{linkbase_namespace}}}linkbaseRef",
                linkbase_ref_attributes
            )
        # add roles
        for role in cls.taxonomy_document.roles:
            if not role.schema_location:
                role_element: etree.Element = etree.SubElement(
                    appinfo_element,
                    f"{{{linkbase_namespace}}}roleType",
                    {
                        "id": role.role_id,
                        "roleURI": role.uri(cls.taxonomy_document.namespace)
                    }
                )
                role_name_element: etree.Element = etree.SubElement(
                    role_element,
                    f"{{{linkbase_namespace}}}definition"
                )
                role_name_element.text = role.role_name
                if role.presentation_linkbase:
                    role_link_element: etree.Element = etree.SubElement(
                        role_element,
                        f"{{{linkbase_namespace}}}usedOn"
                    )
                    role_link_element.text = "link:presentationLink"
                if role.calculation_linkbase:
                    role_link_element: etree.Element = etree.SubElement(
                        role_element,
                        f"{{{linkbase_namespace}}}usedOn"
                    )
                    role_link_element.text = "link:calculationLink"
                if role.definition_linkbase:
                    role_link_element: etree.Element = etree.SubElement(
                        role_element,
                        f"{{{linkbase_namespace}}}usedOn"
                    )
                    role_link_element.text = "link:definitionLink"
                role_link_element: etree.Element = etree.SubElement(
                    role_element,
                    f"{{{linkbase_namespace}}}usedOn"
                )
                role_link_element.text = "link:labelLink"
        # add taxonomy elements
        for element_data in cls.taxonomy_document.elements:
            attributes: Dict[str, str] = {
                    "id": element_data.name,
                    f"{{{xbrli_namespace}}}periodType": element_data.period_type,
                    "name": element_data.name,
                    "nillable": "true" if element_data.nillable else "false",
                    "substitutionGroup": element_data.substitution_group.to_prefixed_name(cls.taxonomy_document.namespaces),
                    "type": element_data.type.to_prefixed_name(cls.taxonomy_document.namespaces)
            }
            if element_data.abstract:
                attributes["abstract"] = "true"
            if element_data.balance:
                attributes[f"{{{xbrli_namespace}}}balance"] = element_data.balance
            element_element: etree.Element = etree.SubElement(
                schema_root,
                f"{{{xs_namespace}}}element",
                attributes
            ) 
        taxonomy_folder.contained_files.append(File(f"{cls.taxonomy_document.files_base_name}.xsd", content=xml_to_string(schema_root)))

    def _create_presentation(cls, taxonomy_folder: File) -> None:
        # create presentation Linkbase
        xsi_namespace: str = "http://www.w3.org/2001/XMLSchema-instance"
        linkbase_namespace: str = "http://www.xbrl.org/2003/linkbase"
        xlink_namespace: str = "http://www.w3.org/1999/xlink"
        namespace_map = {
            None: linkbase_namespace,
            "xsi": xsi_namespace,
            "xlink": xlink_namespace
        }
        presentation_root: etree.Element = etree.Element(
            f"{{{linkbase_namespace}}}linkbase",
            {
                f"{{{xsi_namespace}}}schemaLocation": "http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd"
            },
            nsmap=namespace_map
        )
        for role_data in cls.taxonomy_document.roles:
            if role_data.presentation_linkbase:
                role_ref_element: etree.Element = etree.SubElement(
                    presentation_root,
                    f"{{{linkbase_namespace}}}roleRef",
                    {
                        "roleURI": role_data.uri(cls.taxonomy_document.namespace),
                        f"{{{xlink_namespace}}}href": role_data.href(cls.taxonomy_document.files_base_name),
                        f"{{{xlink_namespace}}}type": "simple"
                    }
                ) 
                presentation_link_element: etree.Element = etree.SubElement(
                    presentation_root,
                    f"{{{linkbase_namespace}}}presentationLink",
                    {
                        f"{{{xlink_namespace}}}role": role_data.uri(cls.taxonomy_document.namespace),
                        f"{{{xlink_namespace}}}type": "extended"
                    }
                )
                # add elements to the presentation linkbase
                locators: Dict[str, str] = {}
                for child in role_data.presentation_linkbase:
                    locators = cls._add_presentation_item(
                        child, 
                        presentation_link_element, 
                        locators,
                        linkbase_namespace,
                        xlink_namespace
                    )
        taxonomy_folder.contained_files.append(File(f"{cls.taxonomy_document.files_base_name}_pre.xml", content=xml_to_string(presentation_root)))
        
    def _add_presentation_item(cls, presentation_element: PresentationElement, parent_element: etree.Element, locators: Dict[str, str], linkbase_namespace: str, xlink_namespace: str, parent_element_locator: str = None) -> Dict[str, str]:
        element_label, locators = cls._add_element_locator(
            parent_element,
            presentation_element.schema_location,
            presentation_element.element_id,
            locators,
            linkbase_namespace,
            xlink_namespace
        )
        if parent_element_locator:
            arc_attributes = {
                f"{{{xlink_namespace}}}type": "arc",
                f"{{{xlink_namespace}}}from": parent_element_locator,
                f"{{{xlink_namespace}}}to": element_label,
                f"{{{xlink_namespace}}}arcrole": "http://www.xbrl.org/2003/arcrole/parent-child",
                "order": str(presentation_element.order)
            }
            if presentation_element.preferred_label:
                arc_attributes["preferredLabel"] = presentation_element.preferred_label
            presentation_arc_element: etree.Element = etree.SubElement(
                parent_element,
                f"{{{linkbase_namespace}}}presentationArc",
                arc_attributes
            )
        for child in presentation_element.children:
            locators = cls._add_presentation_item(
                child, 
                parent_element, 
                locators,
                linkbase_namespace,
                xlink_namespace,
                element_label
            )
        return locators
    
    def _create_calculation(cls, taxonomy_folder: File) -> None:
        # create calculation Linkbase
        xsi_namespace: str = "http://www.w3.org/2001/XMLSchema-instance"
        linkbase_namespace: str = "http://www.xbrl.org/2003/linkbase"
        xlink_namespace: str = "http://www.w3.org/1999/xlink"
        namespace_map = {
            None: linkbase_namespace,
            "xsi": xsi_namespace,
            "xlink": xlink_namespace
        }
        calculation_root: etree.Element = etree.Element(
            f"{{{linkbase_namespace}}}linkbase",
            {
                f"{{{xsi_namespace}}}schemaLocation": "http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd"
            },
            nsmap=namespace_map
        )
        for role_data in cls.taxonomy_document.roles:
            if role_data.calculation_linkbase:
                role_ref_element: etree.Element = etree.SubElement(
                    calculation_root,
                    f"{{{linkbase_namespace}}}roleRef",
                    {
                        "roleURI": role_data.uri(cls.taxonomy_document.namespace),
                        f"{{{xlink_namespace}}}href": role_data.href(cls.taxonomy_document.files_base_name),
                        f"{{{xlink_namespace}}}type": "simple"
                    }
                ) 
                calculation_link_element: etree.Element = etree.SubElement(
                    calculation_root,
                    f"{{{linkbase_namespace}}}calculationLink",
                    {
                        f"{{{xlink_namespace}}}role": role_data.uri(cls.taxonomy_document.namespace),
                        f"{{{xlink_namespace}}}type": "extended"
                    }
                )
                # add elements to the calculation linkbase
                locators: Dict[str, str] = {}
                for child in role_data.calculation_linkbase:
                    locators = cls._add_calculation_item(
                        child, 
                        calculation_link_element, 
                        locators,
                        linkbase_namespace,
                        xlink_namespace
                    )
        taxonomy_folder.contained_files.append(File(f"{cls.taxonomy_document.files_base_name}_cal.xml", content=xml_to_string(calculation_root)))
        
    def _add_calculation_item(cls, calculation_element: CalculationElement, parent_element: etree.Element, locators: Dict[str, str], linkbase_namespace: str, xlink_namespace: str, parent_element_locator: str = None) -> Dict[str, str]:
        element_label, locators = cls._add_element_locator(
            parent_element,
            calculation_element.schema_location,
            calculation_element.element_id,
            locators,
            linkbase_namespace,
            xlink_namespace
        )
        if parent_element_locator:
            arc_attributes = {
                f"{{{xlink_namespace}}}type": "arc",
                f"{{{xlink_namespace}}}from": parent_element_locator,
                f"{{{xlink_namespace}}}to": element_label,
                f"{{{xlink_namespace}}}arcrole": "http://www.xbrl.org/2003/arcrole/summation-item",
                "weight": str(calculation_element.weight)
            }
            calculation_arc_element: etree.Element = etree.SubElement(
                parent_element,
                f"{{{linkbase_namespace}}}calculationArc",
                arc_attributes
            )

        for child in calculation_element.children:
            locators = cls._add_calculation_item(
                child, 
                parent_element, 
                locators,
                linkbase_namespace,
                xlink_namespace,
                element_label
            )
        return locators

    def _create_definition(cls, taxonomy_folder: File) -> None:
        # create definition Linkbase
        xsi_namespace: str = "http://www.w3.org/2001/XMLSchema-instance"
        linkbase_namespace: str = "http://www.xbrl.org/2003/linkbase"
        xlink_namespace: str = "http://www.w3.org/1999/xlink"
        namespace_map = {
            None: linkbase_namespace,
            "xsi": xsi_namespace,
            "xlink": xlink_namespace
        }
        definition_root: etree.Element = etree.Element(
            f"{{{linkbase_namespace}}}linkbase",
            {
                f"{{{xsi_namespace}}}schemaLocation": "http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd"
            },
            nsmap=namespace_map
        )
        for arcrole_uri, arcrole_href in cls.taxonomy_document.definition_arcroles.items():
            arcrole_ref_element: etree.Element = etree.SubElement(
                definition_root,
                f"{{{linkbase_namespace}}}arcroleRef",
                {
                    "arcroleURI": arcrole_uri,
                    f"{{{xlink_namespace}}}href": arcrole_href,
                    f"{{{xlink_namespace}}}type": "simple"
                }
            )
        for role_data in cls.taxonomy_document.roles:
            if role_data.definition_linkbase:
                role_ref_element: etree.Element = etree.SubElement(
                    definition_root,
                    f"{{{linkbase_namespace}}}roleRef",
                    {
                        "roleURI": role_data.uri(cls.taxonomy_document.namespace),
                        f"{{{xlink_namespace}}}href": role_data.href(cls.taxonomy_document.files_base_name),
                        f"{{{xlink_namespace}}}type": "simple"
                    }
                ) 
                definition_link_element: etree.Element = etree.SubElement(
                    definition_root,
                    f"{{{linkbase_namespace}}}definitionLink",
                    {
                        f"{{{xlink_namespace}}}role": role_data.uri(cls.taxonomy_document.namespace),
                        f"{{{xlink_namespace}}}type": "extended"
                    }
                )
                # add elements to the calculation linkbase
                locators: Dict[str, str] = {}
                for child in role_data.definition_linkbase:
                    locators = cls._add_definition_item(
                        child, 
                        definition_link_element, 
                        locators,
                        linkbase_namespace,
                        xlink_namespace
                    )
        taxonomy_folder.contained_files.append(File(f"{cls.taxonomy_document.files_base_name}_def.xml", content=xml_to_string(definition_root)))
        
    def _add_definition_item(cls, definition_element: DefinitionElement, parent_element: etree.Element, locators: Dict[str, str], linkbase_namespace: str, xlink_namespace: str, parent_element_locator: str = None) -> Dict[str, str]:
        element_label, locators = cls._add_element_locator(
            parent_element,
            definition_element.schema_location,
            definition_element.element_id,
            locators,
            linkbase_namespace,
            xlink_namespace
        )
        if parent_element_locator:
            xbrldt_namespace = "http://xbrl.org/2005/xbrldt"
            nsmp = {
                "xbrldt": xbrldt_namespace
            }
            arc_attributes = {
                f"{{{xlink_namespace}}}type": "arc",
                f"{{{xlink_namespace}}}from": parent_element_locator,
                f"{{{xlink_namespace}}}to": element_label,
                f"{{{xlink_namespace}}}arcrole": definition_element.arcrole
            }
            if definition_element.closed != None:
                arc_attributes[f"{{{xbrldt_namespace}}}closed"] = "true" if definition_element.closed else "false"
            if definition_element.context_element != None:
                arc_attributes[f"{{{xbrldt_namespace}}}contextElement"] = definition_element.context_element
            definition_arc_element: etree.Element = etree.SubElement(
                parent_element,
                f"{{{linkbase_namespace}}}definitionArc",
                arc_attributes,
                nsmap=nsmp
            )
        for child in definition_element.children:
            locators = cls._add_definition_item(
                child, 
                parent_element, 
                locators,
                linkbase_namespace,
                xlink_namespace,
                element_label
            )
        return locators

    def _create_label_linkbase(cls, taxonomy_folder: File, labels_lang: str) -> None:
        label_elements = cls.taxonomy_document.labels[labels_lang]
        # set up document
        xsi_namespace: str = "http://www.w3.org/2001/XMLSchema-instance"
        linkbase_namespace: str = "http://www.xbrl.org/2003/linkbase"
        xlink_namespace: str = "http://www.w3.org/1999/xlink"
        xml_namespace: str = "http://www.w3.org/XML/1998/namespace"
        namespace_map = {
            None: linkbase_namespace,
            "xsi": xsi_namespace,
            "xlink": xlink_namespace,
            "xml": xml_namespace
        }
        linkbase_root: etree.Element = etree.Element(
            f"{{{linkbase_namespace}}}linkbase",
            {
                f"{{{xsi_namespace}}}schemaLocation": "http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd"
            },
            nsmap=namespace_map
        )
        label_link_element: etree.Element = etree.SubElement(
            linkbase_root,
            f"{{{linkbase_namespace}}}labelLink",
            {
                f"{{{xlink_namespace}}}role": "http://www.xbrl.org/2003/role/link",
                f"{{{xlink_namespace}}}type": "extended"
            }
        )
        locators: Dict[str, str] = {}
        label_id: int = 0
        for label_element_data in label_elements:
            locator_label, locators = cls._add_element_locator(
                label_link_element,
                label_element_data.schema_location,
                label_element_data.element_id,
                locators,
                linkbase_namespace,
                xlink_namespace
            )
            for label_data in label_element_data.lables:
                label_label: str = f"label_{label_id}"
                label_id += 1
                label_element: etree.Element = etree.SubElement(
                    label_link_element,
                    f"{{{linkbase_namespace}}}label",
                    {
                        f"{{{xlink_namespace}}}label": label_label,
                        f"{{{xlink_namespace}}}role": label_data.label_role,
                        f"{{{xlink_namespace}}}type": "resource",
                        f"{{{xml_namespace}}}lang": labels_lang
                    }
                )
                label_element.text = label_data.label
                label_arc_element: etree.Element = etree.SubElement(
                    label_link_element,
                    f"{{{linkbase_namespace}}}labelArc",
                    {
                        f"{{{xlink_namespace}}}type": "arc",
                        f"{{{xlink_namespace}}}from": locator_label,
                        f"{{{xlink_namespace}}}to": label_label,
                        f"{{{xlink_namespace}}}arcrole": "http://www.xbrl.org/2003/arcrole/concept-label",
                        "priority": "100"
                    }
                )
        taxonomy_folder.contained_files.append(File(f"{cls.taxonomy_document.files_base_name}_lab-{labels_lang}.xml", content=xml_to_string(linkbase_root)))

    def _add_element_locator(cls, parent_element: etree.Element, schema_location: str, element_id: str, located_elements_elements: Dict[str, str], linkbase_namespace: str, xlink_namespace: str) -> None:
        if schema_location:
            locator_href = f"{schema_location}#{element_id}"
        else:
            locator_href = f"{cls.taxonomy_document.files_base_name}.xsd#{element_id}"
        if locator_href in located_elements_elements:
            return located_elements_elements[locator_href], located_elements_elements
        locator_label: str = f"locator_{len(located_elements_elements.keys())}"
        element_locator: etree.Element = etree.SubElement(
            parent_element,
            f"{{{linkbase_namespace}}}loc",
            {
                f"{{{xlink_namespace}}}type": "locator",
                f"{{{xlink_namespace}}}href": locator_href,
                f"{{{xlink_namespace}}}label": locator_label
            }
        )
        located_elements_elements[locator_href] = locator_label
        return locator_label, located_elements_elements