# How to "Tag" the JSON file

NOTE: Links to Schemas/Folders only work withing github. See this file in the `docs/engine_guides/` folder on GitHub to use the links!

## Table of Contents

1. [Where to put the tags](#where-to-put-the-tags)
2. [Composition of the "AppliedTag" Object](#composition-of-the-appliedtag-object)
2. [Examples for differnet Data Types](#examples)
3. [Conclusion](#conclusion)

## Where to put the tags

The JSON Schema located [here](../../src/xbrl_forge/schemas/input/) are a great starting point to understand the general structure of the `Input` Object (also called `wrapper`in the schema). Every key for every object has a description on the function and content of the key.

Each `Input` Object can carry multiple `report` Objects, which each represent a part of a XHTML/XBRL Instance document. Each Report Object carries (next to other information) 3 relevant keys for the tagging:
 - `xhtml`: Determines if it will be inline xBRL/xHTML or if it will be a xBRL instance

 - `namespaces`: 
 Every concept used for tagging (and some other things like transformations, more on that later) is identified by the tuple of `namespace` and `name`, Each of the `namespace` values consists of a URI (caution: no URL but same format, must not be a real "website") identifing the defintion context of the concept. An example: `http://example-company-or-org.com/xbrl/2024` (created by an example organization in 2024). The `namespaces` object will assign a `prefix` for every `namespace`-URI in a object:
    - Example: { "http://example-company-or-org.com/xbrl/2024": "example" }
    - **Caution**: the `prefix` should only consist of characters and must be unique in the `namespaces` object.
    - Every namespace used for tagging **must** be part of this object **except** for the `namespace` of extension concepts created in the report. This will be generated and added automatically.

 - `content`: A list of content objects of differnt types. Some of them (like `LIST` or `Table`) can include further lists of `content` objects. Please see the schemas for the different content types [here](../../src/xbrl_forge/schemas/input/reports/content/). Each content has one or more `tag` properties (please see echema defintions for exact placement) which carry a list of `AppliedTag` objects. Updating this list is the essence of the tagging procedure.

## Composition of the "AppliedTag" Object

The `AppliedTag` object is defined in [this Schema](../../src/xbrl_forge/schemas/input/reports/applied-tag.schema.json). Please use it as a reference.

## Examples

Here are some examples of the `AppliedTag` object for differnt data types. The list of `AppliedTag` elements can be any amount, from 0 to n tags for the content. The nesting and beaking, contiuations and other complex things are handeled automatically. Just include the information what should be tagged!

### Numeric Data (all quantitative Data types)

Example text in a `ContentItem` of type `PARAGRAPH`:

```
My Intangible Assets are -23.4 K EUR for non-controlling interests.
```

The number should be tagged with the concept `ifrs-full:IntangibleAssetsOtherThanGoodwill` from the 2022 IFRS Taxonomy:

```json
{
    // start and end index (first index AFTER the value) of the provided content string
    // if the whole structure should be tagged, set both to null or omi them
    // for numeric values please make sure only digits, spaces, dots and commas are part of the string
    // on some structures only tags without these attributes will be considered. Please check with the JSON Schema of the respective content element
    "start_index": 26,
    // the end index can also be -1, which leads to the end of the content of the structure 
    "end_index": 30,

    // the namespace of the 2022 IFRS taxonomy in which the concept is defined
    // make sure that this is included in the `namespaces` property of the report json
    "namespace": "https://xbrl.ifrs.org/taxonomy/2022-03-24/ifrs-full",
    // the name of the defined concept - Attention! Not the "id" attrubte of the definition.
    "name": "IntangibleAssetsOtherThanGoodwill",

    // the identitifier of the company the value refers to, must not be a LEI
    "entity": "254900OPPU84GM83MG36",
    // the standard (scheme) under which the identifier is issued, in this case the LEI
    "entity_scheme": "http://standards.iso.org/iso/17442",

    // start and end dates, both in the format "YYYY-MM-DD"
    // the end date must always be given and refers to the end of the given day
    // the start date must only be given for duration values, refers to the start of the day. For instant values, omit this key or set to null
    "end_date": "2024-12-31",
    "start_date": null,

    // 0 to n dimension can be added to the fact
    // every added dimension conains one axis concept and one member concept
    // for explicit axis elements, omit the "typed_member_value" or set to null
    // for typed axis elements, provide the typed axis value (string) additionally to axis and member.
    "dimensions": [
        {
            "axis": {
                // make sure that this is included in the `namespaces` property of the report json
                "namespace": "https://xbrl.ifrs.org/taxonomy/2022-03-24/ifrs-full",
                "name": "ComponentsOfEquityAxis"
            },
            "member": {
                // make sure that this is included in the `namespaces` property of the report json
                "namespace": "https://xbrl.ifrs.org/taxonomy/2022-03-24/ifrs-full",
                "name": "NoncontrollingInterestsMember"
            },
            "typed_member_value": null
        }
    ],

    // attributes define the meta information tied to every fact
    "attributes": {

        // this value is in thousands and must be multiplied with 10 ^ 3
        "scale": 3,

        // the value multiplied by the scale is accurate to 2 digits BEFORE the decimal point:
        "decimals": -2,

        // Units are made up form a numerator unit and an optional denominator unit
        // the numerator unit must be set
        // the denominator is optional, for exaple for EUR per Share
        // in this case it is only EUR
        "unit": {
            "numerator": {
                // make sure that this is included in the `namespaces` property of the report json
                "namespace": "http://www.xbrl.org/2003/iso4217",
                "name": "EUR"
            },
            "denominator": null
        },

        // the format of the number. In this case the decimal seperator is a comma
        "format": {
            // make sure that this is included in the `namespaces` property of the report json
            "namespace": "http://www.xbrl.org/inlineXBRL/transformation/2020-02-12",
            "name": "num-comma-decimal"
        },

        // all tagged values in iXBRL must tagged withoug any prefixed sign
        // this attribute is used to mark the value to be negative IN REGARDS TO THE USED CONCEPT DEFINITION.
        "sign": false
    }
}
```

### Unformatted Text-Based Data (TextBlock, String)

Example text in a `ContentItem` of type `PARAGRAPH`:

```
My Intangible Assets are -23.4 K EUR for non-controlling interests. This has not changes in the prior year.
```

The whole paragraph should be tagged with the `textBlock` concept `ifrs-full:DisclosureOfDetailedInformationAboutIntangibleAssetsExplanatory` from the 2022 IFRS Taxonomy:

```json
{
    // no indexes will be provided to tag the whole content of the ContentItem
    "start_index": null,
    "end_index": null,
    
    // the namespace of the 2022 IFRS taxonomy in which the concept is defined
    // make sure that this is included in the `namespaces` property of the report json
    "namespace": "https://xbrl.ifrs.org/taxonomy/2022-03-24/ifrs-full",
    // the name of the defined concept - Attention! Not the "id" attrubte of the definition.
    "name": "DisclosureOfDetailedInformationAboutIntangibleAssetsExplanatory",

    // the identitifier of the company the value refers to, must not be a LEI
    "entity": "254900OPPU84GM83MG36",
    // the standard (scheme) under which the identifier is issued, in this case the LEI
    "entity_scheme": "http://standards.iso.org/iso/17442",

    // start and end dates, both in the format "YYYY-MM-DD"
    // the end date must always be given and refers to the end of the given day
    // the start date must only be given for duration values, refers to the start of the day. For instant values, omit this key or set to null
    "end_date": "2024-12-31",
    "start_date": "2024-01-01",

    // 0 to n dimension can be added to the fact
    // every added dimension conains one axis concept and one member concept
    // for explicit axis elements, omit the "typed_member_value" or set to null
    // for typed axis elements, provide the typed axis value (string) additionally to axis and member.
    "dimensions": [],

    // attributes define the meta information tied to every fact
    "attributes": {
        // for tagging unformatted text information only the escape attribute is relevant. Please do not provide more attributes
        // if this is true, the html structures will be contained in the tag, if not it will be a simple string according to the iXBRL Specification
        "escape": true
    }
},
```

### Formatted Text-Based Data (Boolean, Enumerations, Date, etc.)

Lets take the `ContentItem` from the above example:

```
My Intangible Assets are -23.4 K EUR for non-controlling interests. This has not changes in the prior year.
```

The second sentence should be tagged with the `boolean` concept `extension-prefix:IntangibleAssetsHaveChanged` defined in the extension taxonomy json provided next to the report:

```json
{
    // The start and end index of the second sentence
    "start_index": 68,
    "end_index": 107,
    
    // no namespace will be provided, since it will use the provided extension taxonomy namespace
    "namespace": null,
    // the value of the "name" attribute of the element definition in the "elements" attribute of the provided extension taxonomy json
    "name": "IntangibleAssetsHaveChanged",

    // the identitifier of the company the value refers to, must not be a LEI
    "entity": "254900OPPU84GM83MG36",
    // the standard (scheme) under which the identifier is issued, in this case the LEI
    "entity_scheme": "http://standards.iso.org/iso/17442",

    // start and end dates, both in the format "YYYY-MM-DD"
    // the end date must always be given and refers to the end of the given day
    // the start date must only be given for duration values, refers to the start of the day. For instant values, omit this key or set to null
    "end_date": "2024-12-31",
    "start_date": "2024-01-01",

    // 0 to n dimension can be added to the fact
    // every added dimension conains one axis concept and one member concept
    // for explicit axis elements, omit the "typed_member_value" or set to null
    // for typed axis elements, provide the typed axis value (string) additionally to axis and member.
    "dimensions": [],

    // attributes define the meta information tied to every fact
    "attributes": {
        // only the transforamtion rule will be set
        // in this cas the transformation to a false boolean value
        "format": {
            // make sure that this is included in the `namespaces` property of the report json
            "namespace": "http://www.xbrl.org/inlineXBRL/transformation/2020-02-12",
            "name": "fixed-false"
        },
    }
},
```

Lets take the above example `ContentItem` again for a example of enumeration.

The whole paragraph should be tagged with the `EnumerationSet` concept `esrs:TargetCoverage` with the single selected value `esrs:GeographiesMember` defined in the 2024 ESRS taxonomy:

```json
{
    // no indexes will be provided to tag the whole content of the ContentItem
    "start_index": null,
    "end_index": null,
    
    // the namespace of the 2024 ESRS taxonomy in which the concept is defined
    // make sure that this is included in the `namespaces` property of the report json
    "namespace": "https://xbrl.efrag.org/taxonomy/draft-esrs/2023-07-31",
    // the name of the defined concept - Attention! Not the "id" attrubte of the definition.
    "name": "TargetCoverage",

    // the identitifier of the company the value refers to, must not be a LEI
    "entity": "254900OPPU84GM83MG36",
    // the standard (scheme) under which the identifier is issued, in this case the LEI
    "entity_scheme": "http://standards.iso.org/iso/17442",

    // start and end dates, both in the format "YYYY-MM-DD"
    // the end date must always be given and refers to the end of the given day
    // the start date must only be given for duration values, refers to the start of the day. For instant values, omit this key or set to null
    "end_date": "2024-12-31",
    "start_date": "2024-01-01",

    // 0 to n dimension can be added to the fact
    // every added dimension conains one axis concept and one member concept
    // for explicit axis elements, omit the "typed_member_value" or set to null
    // for typed axis elements, provide the typed axis value (string) additionally to axis and member.
    "dimensions": [],

    // attributes define the meta information tied to every fact
    "attributes": {
        // 1 to n enumeration values have to be applied for EnumerationSets
        // limited to 1 value for simple Enumerations
        "enumeration_values": [
            {
                // the namespace of the enumeration value concept
                // make sure that this is included in the `namespaces` property of the report json
                "namespace": "https://xbrl.efrag.org/taxonomy/draft-esrs/2023-07-31",
                // the value of the "name" attribute of the enumeration value concept
                "name": "GeographiesMember"
            }
        ]
    }
},
```