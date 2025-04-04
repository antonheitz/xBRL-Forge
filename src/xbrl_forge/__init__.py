from typing import List
import os
import logging

from .logger_setup import logger_conf
logger_conf()

from .xbrl_generation.ContentDataclasses import ContentDocument

from .xbrl_generation.XbrlProducer import XbrlProducer
from .xbrl_generation.PackageDataclasses import File
from .xbrl_generation.InputData import InputData
from .xbrl_generation.HtmlProducer import HtmlProducer
from .xbrl_generation.TaxonomyProducer import TaxonomyProducer

from .utils.schema_validation import validate_schema

from .file_conversion import doc_to_data

logger = logging.getLogger(__name__)

SCHEMA_FOLDER: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "schemas")

def convert_document(document_path: str) -> InputData:
    logger.info(f"Converting file {document_path}")
    input_data_object = doc_to_data(document_path)
    validate_input_data(input_data_object.to_dict())
    return input_data_object

def validate_input_data(data: dict) -> None:
    logger.info(f"Validating input data")
    # get schemas
    input_schema_folder = os.path.join(SCHEMA_FOLDER, "input")
    validate_schema(data, "https://xbrl-forge.org/schema/input/wrapper", input_schema_folder)

def load_input_data(data: dict) -> InputData:
    logger.info(f"Loading Input Data")
    return InputData.from_dict(data)

def create_xbrl(input_data_list: List[InputData], xthml_template: str = None) -> File:
    logger.info(f"Creating XBRL")
    # load data
    loaded_data: InputData = InputData.combine(input_data_list)
    local_namespace = None
    local_namespace_prefix = None
    local_taxonomy_schema = None
    if loaded_data.taxonomy:
        local_namespace=loaded_data.taxonomy.namespace
        local_namespace_prefix=loaded_data.taxonomy.prefix 
        local_taxonomy_schema=loaded_data.taxonomy.schema_url
    reports_folder: File = None
    untagged_reports_folder: File = None
    inline_instances: int = 0
    non_inline_instances: int = 0
    for report in loaded_data.reports:
        if not reports_folder:        
            reports_folder = File("reports", contained_files=[])
        if report.xhtml:
            html_producer: HtmlProducer = HtmlProducer(
                report, 
                xthml_template=xthml_template, 
                local_namespace=local_namespace, 
                local_namespace_prefix=local_namespace_prefix, 
                local_taxonomy_schema=local_taxonomy_schema
            )
            if html_producer.ixbrl:
                reports_folder.contained_files.append(html_producer.create_html())
                inline_instances += 1
            else:
                if not untagged_reports_folder:
                    untagged_reports_folder: File = File("untagged_reports", contained_files=[])
                    reports_folder.contained_files.append(untagged_reports_folder)
                untagged_reports_folder.contained_files.append(html_producer.create_html())
        else:
            xbrl_producer: XbrlProducer = XbrlProducer(
                report, 
                local_namespace=local_namespace, 
                local_namespace_prefix=local_namespace_prefix, 
                local_taxonomy_schema=local_taxonomy_schema
            )
            reports_folder.contained_files.append(xbrl_producer.create_xbrl())
            non_inline_instances += 1
    if not loaded_data.taxonomy:
        return reports_folder
    taxonomy_producer: TaxonomyProducer = TaxonomyProducer(loaded_data.taxonomy)
    package_extension: str = "zip"
    if inline_instances == 1 and non_inline_instances == 0: package_extension = "xbri"
    if inline_instances == 0 and non_inline_instances == 1: package_extension = "xbr"
    return taxonomy_producer.create_files(reports_folder, package_extension)