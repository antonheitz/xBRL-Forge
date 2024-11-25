# JSON Input file documentation

## Summary

The generation of iXBRL instances, xBRL instances, xBRL Taxonomies and XHTML files are based on a simple and easy to use JSON structure.

This documentation decribes the structure and functionalities of the input JSON.

## Documentation

```json
{
    // the taxonomy json key contains all data necessary to generate a taxonomy or extension taxonomy
    // if only reports should be generated with no extension taxonomy, this key is omitted
    "taxonomy": {

        // priority for combining taxonomies, the higher one wins!
        "priority": 400,

        // this is the preferred prefix used for the taxonomy
        "prefix": "test",
        
        // the metadata for the taxonomy
        "metadata": {

            // name of the taxonomy or report package
            "name": "Example Taxonomy",

            // a small description on the reason for this taxonomy
            "description": "<description>",

            // name of the publisher or publishing organisation
            "publisher": "Test Company Inc",

            // the url from the publisher, this will be used for the taxonomy namespace, do not include the protokoll "http://"
            "publisher_url": "test-company.com",

            // the date of the taxonomy, this needs to be in the format YYYY-MM-DD
            "publication_date": "2024-12-31",
            
            // country of publication
            "publisher_country": "DE",

            // entrypoints to the taxonomy
            "entrypoints": [

                {
                    // name for the taxonomy in the language
                    "name": "<name>",

                    // description in the language
                    "description": "<description>",

                    // entrypoints for the taxonomy - the schema from this taxonomy gets added by default
                    // additional entrypoints can be added. this may be necessary for used base taxonomies
                    "documents": [
                        "https://external_entrypoint",
                        "https://external_entrypoint_2"
                    ],

                    // the language of these entrypoints
                    "language": "de"
                }
            ]
        },

        // every namespace used in the following (taxonomy) parts of the json must be profided with a prefix here
        "namespaces": {
            "http://namespace-uri": "prefix-of-this-namespace"
        },

        // in some cases additional roles and schemas need to be imported to be usable by the taxonomy
        "schema_imports": {
            "http://<namespace-uri>": "http://external_schema.xsd"
        },

        // elements defined by this taxonomy
        "elements": [

            {

                // each element carries a period type "duration" or "instant"
                "period_type": "duration",

                // technical name of the element - must be unique for the elements defined by this taxonomy
                "name": "FirstSectionAbstract",

                // abstract elements are strucural elements not directly used for tagging
                "abstract": true,

                // element is nillable or not
                "nillable": true,

                // the substitutuon group defines the basic element type
                "substitution_group": {

                    // namespace and name of the substitution group
                    // the namespace must be a key in the "namespaces" attribute of the taxonomy json
                    "namespace": "<defining namespace>",
                    "name": "<substitution group>"
                },

                // the type defines the specific item type like String or Monetary etc
                "type": {

                    // namespace and name of the type
                    // the namespace must be a key in the "namespaces" attribute of the taxonomy json
                    "namespace": "<defining namespace>",
                    "name": "<type>"
                }
            }
        ],

        // in some cases external linkbases need to be imported
        // the key is the url for the linkbase
        // the value, if provided and not "null" is the role of the linkbase (e.g. label linkbase: http://www.xbrl.org/2003/role/labelLinkbaseRef)
        // in case of a value null, no dedicated role will be used
        "linkbase_imports": {
            "<url to linkbase>": "<role to be used or null>"
        },

        // the definition linkbase may require additional arcrole that need to be imported from external schemas
        "arc_roles_import": {
        
            // key: the arcrole 
            // value: the import of the definition
            "http://arcrole": "http://arcrole_schema.xsd#arcrole-id"
        },

        // roles are the broaded structural items and can be used in diffenet linkbases
        // they can be either imported or defined newly
        "roles": [
            
            // a role object which can be used in definition, calculation and presentation linkbases
            {

                // the human readable description for the role
                "role_name": "<role name>",
                
                // in case of an external role, the id must represent the id used in the external schema
                // in case of a taxonomy specific role, this is the key that is used for mergeing roles from different sources
                // only characters a-z and numbers and - and _ should be used
                "role_id": "<role id>",
                
                // the uri only needs to be provided if an external role is used
                // if an role specific to this taxonomy should be created, omit the role_uri
                "role_uri": "https://<external_role_uri>",

                // the schema location only needs to be provided if an external role is used
                // if an role specific to this taxonomy should be created, omit the role schema_location
                "schema_location": "https://www.esma.europa.eu/taxonomy/2022-03-24/esef_cor.xsd",

                // presentation relationships for this role, if empty the role will not be used in the presentation linkbase
                "presentation_linkbase": [
                    
                    // nested (recursive) presentation object
                    {
                        
                        // the id of the element to be used
                        // in case of an external element (not defined by this taxonomy) this must be the id of the element as it is defined in the external schema
                        // in case of an element defined by this taxonomy, this must reflect the "technical_name" value of the defined element
                        "element_id": "<element_id>",
                        
                        // in case of an external element (not defined by this taxonomy) this must be the schema it was defined in
                        "schema_location": "https://schema_url.xsd",

                        // presentation content will be odered in an ascending order to the "order" value
                        "order": 0,

                        // presentation arcrole to be used
                        "arc_role": "https://arcrole",

                        // children of the presentation object forming hierarchical relationships
                        "children": []
                    }
                ],
                
                // definition relationships for this role, if empty the role will not be used in the definition linkbase
                "definition_linkbase": [

                    // nested (recursive) definition object
                    {
                        // the id of the element to be used
                        // in case of an external element (not defined by this taxonomy) this must be the id of the element as it is defined in the external schema
                        // in case of an element defined by this taxonomy, this must reflect the "technical_name" value of the defined element
                        "element_id": "<element_id>",
                        
                        // in case of an external element (not defined by this taxonomy) this must be the schema it was defined in
                        "schema_location": "https://schema_url.xsd",

                        // the arcrole to be used in this relationship
                        // the object defining this is the target of the relationship, it only may be null for the top level element
                        // it may be necessary to import the arcrole via the definition_arcroles key
                        "arc_role": "<arcrole>",
                        
                        // in case of an hypercube definition, a context element and closed attribute may be necessary
                        "context_element": "scenario",
                        "closed": true,

                        // recursive definition object forming the relationship
                        "children": []
                    }
                ],
                
                // calculation relationships for this role, if empty the role will not be used in the calculation linkbase
                "calculation_linkbase": [
                    
                    // nested (recursive) calculation object
                    {

                        // the id of the element to be used
                        // in case of an external element (not defined by this taxonomy) this must be the id of the element as it is defined in the external schema
                        // in case of an element defined by this taxonomy, this must reflect the "technical_name" value of the defined element
                        "element_id": "<element_id>",
                        
                        // in case of an external element (not defined by this taxonomy) this must be the schema it was defined in
                        "schema_location": "https://schema_url.xsd",

                        // weight of the calculation relationship. The relationship weight is defined by the child (target) of the relationship 
                        "weight": 1,

                        // calculation arcrole to be used
                        "arc_role": "https://arcrole",
                        
                        // recursive calculation object forming the relationship
                        "children": []
                    }
                ]
            }
        ],

        // labels for elements used in the taxonomy
        "labels": {

            // each key resembles a language (used by the subsequent labels) in the ISO code
            "en": [

                // a element label object
                {
                     // the id of the element to be used
                    // in case of an external element (not defined by this taxonomy) this must be the id of the element as it is defined in the external schema
                    // in case of an element defined by this taxonomy, this must reflect the "technical_name" value of the defined element
                    "element_id": "<element_id>",
                    
                    // in case of an external element (not defined by this taxonomy) this must be the schema it was defined in
                    "schema_location": "https://schema_url.xsd",

                    // one or more labels for the element
                    "lables": [
                        {
                            // each label must have a role
                            // the role must be unique for the combination of element and language
                            "label_role": "<label_role_uri>",

                            // the human readable label
                            "label": "<some label value>"
                        }
                    ]
                }
            ]
        }
    },
    
    // reports, XHTML and iXBRL, multiple reports are allowed
    // every report object in the reports array will result in a seperate instance
    // if the reports key is omitted, only a taxonomy will be produced
    "reports": [
        {
            // the report file name and the document title
            // this is also the key to combine reports from different resources,
            // example: two parts of the reports are produced by two different systems
            "name": "Example Report File",
            
            // if this key is given, it should reference an external available taxonomy schema
            // if this key is omitted, the package taxonomy will be used
            // in case of pure xhtml files (see detection in the "resource" object kex "contexts"), this key will be ignored
            "taxonomy_schema": "http://external/schema.xsd",
            
            // every instance can only carry one language
            "lang": "de",

            // boolean: if true the document will be a inline XBRL document, if not a simple xBRL instance
            // ATTENTION: if false: only transformations "num-comma-decimal", "fixed-zero" and "num-dot-decimal" can be used
            // ATTENTION: Only tag-wide (start and end index null) tags can be used and they cannot be nested! Currently no escaped text is available
            "inline": true,
                    
            // each report can be constructed from multiple resource objects, each carrying all the information like an isolated report
            // in case of multiple resources for the file the content will be ordered depending on this key, ascending when combined
            "priority": 1,

            // in case of pure xhtml, this key will be ignored
            // every namespace used by the ixbrl content such as the taxonomy namespaces of the elements used and namespaces for transformations/values must be included here
            // every namespace used in the resource must be defined here
            // the namespace for the taxonomy provided in this json file is added automatically
            "namespaces": {
                "http://namespace-uri": "namespace-prefix",
                "https://namespace-uri-2": "namespace-prefix-2"
            },

            // every tagged fact needs a context
            // if no contexts are declared, the resource will be treated as XHMTL only
            "contexts": {
                
                // every context id referenced in the tags on the content must be contained as a key in this object
                // the context id may only contist of a-z characters, numbers and underscores
                "<context-id>": {

                    // an entity is defined by the identifier and the scheme used for the identifier
                    "entity": "<identifier string>",
                    "entity_scheme": "<entiy scheme>",

                    // the dates must be provided in the format YYYY-MM-DD
                    // for instant values only provide end_date
                    // for duration values provide both dates
                    // NOTE: end_date always refers to the end of the day, while start_date refers to the start of the day
                    "end_date": "2024-12-31",
                    "start_date": "2024-01-01",
                    
                    // zero to n dimensions can be provided for a context
                    "dimensions": [

                        // each dimension object consists of an axis and a member
                        // each axis must only be used once per context
                        {
                            "axis": {

                                // the taxonomy namespace and element name of the axis element
                                // the namespace value must be included in the namespaces object of the report object
                                // if the element was defined in the taxonomy provided in this json file, omit the namespace
                                "namespace": "https://namespace-uri",
                                "name": "<Axis Name>"
                            },
                            "member": {
                                
                                // the taxonomy namespace and element name of the member element
                                // the namespace value must be included in the namespaces object of the report object
                                // if the element was defined in the taxonomy provided in this json file, omit the namespace
                                "namespace": "https://namespace-uri-2",
                                "name": "<Member Name>"
                            }
                        }
                    ]
                }
            },
            
            // numeric facts need a unit
            "units": {
                
                // every unit_id referenced in the tags on the content must be contained as a key in this object
                // the unit_id may only contist of a-z characters, numbers and underscores
                "<unit_id>": {

                    // the numerator will be the numerator of the unit
                    // in case of a unit which does not contain of a numerator and denominator unit but a single unit, only provide the numerator
                    "numerator": {
                        
                        // the namespace and name of the unit
                        // the namespace value must be included in the namespaces object of the report object
                        "namespace": "http//namespace-uri",
                        "name": "Unit Name"
                    },

                    // this key can be omitted for units not needing a denominator
                    "denominator": {
                        
                        // the namespace and name of the unit
                        // the namespace value must be included in the namespaces object of the report object
                        "namespace": "http//namespace-uri",
                        "name": "Unit Name"
                    }
                }
            },

            // the human readable content enriched with tags
            // please  find all available content types as examples below
            // each content type has their own strucure
            "content": [

                // the TITLE content can include headings with different levels
                {

                    // identifier for the type TITLE
                    "type": "TITLE",

                    // Text content of the Title
                    "content": "Example Report for Test Company",

                    // level can be 1 - 6, broad to specific
                    "level": 1,

                    // tags on this content are described as objects
                    "tags": [
                        
                        {
                            // the namespace and the name of the concept (line item) used for the tag
                            // in case of multiple usages of NON-NUMERIC (see type below) concepts with the same concept, continuations will be handled automatically
                            // in case of an element from the taxonomy created by this json, omit the namespace attribute
                            "namespace": "http://test-company.com/xbrl/2023",
                            "name": "CompleteSection",

                            // the context id must be included in the contexts section of this resource
                            "context_id": "context_1",

                            // start_index and end_index define the applicable content for this tag.
                            // if both are omitted, the tag will be applied to the whole structue including the structural elements
                            // if provided, the indexes will count in characters of the content, starting with 0
                            // the end index is the index of the character after the last character which is to be tagged
                            "start_index": null,
                            "end_index": null,

                            // currently two types are supported, "NUMERIC" and "NONNUMERIC"
                            "type": "NONNUMERIC",

                            // each tag is enhanced by attributes, depending pn their type
                            "attributes": {

                                // NONNUMERIC ATTRIBUTES

                                // escaping includes xhtml strucural elements into the fact value for nonnumeric tags
                                // only the escaping flag from the first ocurrance of a concept for each context will read this attribute and then apply to all continuations for that fact
                                "escape": true,

                                // NUMERIC ATTIBUTES

                                // decimals declare the accuracy of the tagged value
                                "decimals": -2,

                                // scale declare the scale of the tagged value, tag*10^scale
                                "scale": 3,

                                // this references to a unit defined in the "units" object of this resource
                                "unit": "<unit_id>",

                                // the format of the number decribing how it should be transformed to a number for the mashine
                                // for this normally transformation registries are used
                                "format": {

                                    // the namespace of the transformation registry
                                    // this must be defined with a prefix in the namespaces object of the resource
                                    "namespace": "http://namesace-uri",
                                    "name": "transformation-name"
                                },

                                // the sign attribute reverses the mashine readable value
                                // this is necessary if the human readable logic differs from the xbrl logic
                                "sign": false
                            }
                        }
                    ]
                },
                
                // the PARAGRAPH content is the standard text content structure
                {
                    
                    // identifier for the type PARAGRAPH
                    "type": "PARAGRAPH",

                    // text content for the paragraph
                    "content": "This Paragraph should be tagged with one whole tag. This sentence is a similar topic but gets a second tag as well. This Sentence and a part of the sentence before are a third tag.",
                    
                    // please refer to the tags section of the "TITLE" type
                    "tags": []
                },
                
                // the TABLE content creates beautiful table structures
                {
                    
                    // identifier for the type TABLE
                    "type": "TABLE",

                    // each table contains of one or more rows
                    "rows": [

                        // each row is represented by a row object
                        {
                            
                            // rows consist of one or more cells
                            "cells": [

                                // each cell object represents one cell
                                {
                                    
                                    // the content of a cell is a nested (recursive) structure
                                    // this contains any strucural content type such as TABLE PARAGRAPH TITLE etc.
                                    "content": [],
                                    
                                    // header cells can be identified with this key
                                    // in case of data cell, set this to false
                                    "header": true
                                }
                            ]
                        }
                    ],

                    // please refer to the tags section of the "TITLE" type
                    // only tags on the whole structure are allowed in this place (omitting the start_index and end_index keys)
                    "tags": []
                },
                
                
                // the IMAGE content displays images which are provided in base-64 data uris
                {
                    
                    // identifier for the type IMAGE
                    "type": "IMAGE",
                    
                    // the image encoded in base64 (as data uri)
                    "image_data": "<data uri>",

                    // applied tags to the image
                    // only tags on the whole structure (start and end index omitted) work here
                    // please refer to the tags section of the "TITLE" type
                    "tags": []
                },

                // the LSIT content builds list structures in the report
                {

                    // identifier for the type LIST
                    "type": "LIST",

                    // normal lists use bullets. With this key true the list will be numbered in ascending order
                    "ordered": false,

                    // each list needs at least one element in the list
                    "elements": [
                        {

                            // elements are a nested strucure
                            // the content are the normal content structures,
                            // this allows for nesting of lists in lists or pragraphs in list
                            "content": []
                        }
                    ],

                    // please refer to the tags section of the "TITLE" type
                    // only tags on the whole structure are allowed in this place (omitting the start_index and end_index keys)
                    "tags": []
                },

                // the BASE_XBRL content is there for two cases, bot ONLY for xbrl instances (no inline)
                // 1) to tag numbers
                // 2) to tag strings without HTML elements (unescaped)
                {
                    // the identifier
                    "type": "BASE_XBRL",

                    // the text content
                    "content": "<content placed herer>",

                    // please refer to the tags section of the "TITLE" type
                    // only tags on the whole structure are allowed in this place (omitting the start_index and end_index keys)
                    "tags": []
                }
            ]
        }
    ]
}
```