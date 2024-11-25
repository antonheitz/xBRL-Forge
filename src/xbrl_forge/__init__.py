from typing import List

from .ContentDataclasses import ContentDocument

from .XbrlProducer import XbrlProducer
from .PackageDataclasses import File
from .InputData import InputData
from .HtmlProducer import HtmlProducer
from .TaxonomyProducer import TaxonomyProducer

def load_data(data: dict) -> InputData:
    return InputData.from_dict(data)

def create_xbrl(input_data_list: List[InputData], styles: str = None) -> File:
    # load data
    loaded_data: InputData = InputData.combine(input_data_list)
    local_namespace = None
    local_namespace_prefix = None
    local_taxonomy_schema = None
    if loaded_data.taxonomy:
        local_namespace=loaded_data.taxonomy.namespace
        local_namespace_prefix=loaded_data.taxonomy.prefix 
        local_taxonomy_schema=loaded_data.taxonomy.schema_url
    report_files: List[File] = []
    for report in loaded_data.reports:
        if report.inline:
            html_producer: HtmlProducer = HtmlProducer(
                report, 
                styles=styles, 
                local_namespace=local_namespace, 
                local_namespace_prefix=local_namespace_prefix, 
                local_taxonomy_schema=local_taxonomy_schema
            )
            report_files.append(html_producer.create_html())
        else:
            xbrl_producer: XbrlProducer = XbrlProducer(
                report, 
                local_namespace=local_namespace, 
                local_namespace_prefix=local_namespace_prefix, 
                local_taxonomy_schema=local_taxonomy_schema
            )
            report_files.append(xbrl_producer.create_xbrl())
    if not loaded_data.taxonomy:
        return File("reports", contained_files=report_files)
    taxonomy_producer: TaxonomyProducer = TaxonomyProducer(loaded_data.taxonomy)
    return taxonomy_producer.create_files(report_files)