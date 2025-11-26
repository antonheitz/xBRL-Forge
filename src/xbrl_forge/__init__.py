from typing import List
import os
import logging

from .logger_setup import logger_conf
logger_conf()

from .xbrl_generation.PackageDataclasses import File
from .xbrl_generation.InputData import InputData
from .xbrl_generation.PackageProducer import PackageProducer
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
    producer: PackageProducer = PackageProducer(loaded_data, xthml_template=xthml_template)
    return producer.get_package()