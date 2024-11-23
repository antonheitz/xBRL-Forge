from typing import List
from .PackageDataclasses import File
from .InputData import InputData
from .HtmlDataclasses import ContentDocument
from .HtmlProducer import HtmlProducer
from .TaxonomyDataclasses import TaxonomyDocument
from .TaxonomyProducer import TaxonomyProducer
    
def generate(data: dict, styles: str = None) -> File:
    # load data
    loaded_data: InputData = InputData.from_dict(data)
    report_files: List[File] = []
    for report in loaded_data.reports:
        producer: HtmlProducer = HtmlProducer(
            report, 
            styles=styles, 
            local_namespace=loaded_data.taxonomy.namespace, 
            local_namespace_prefix=loaded_data.taxonomy.prefix, 
            local_taxonomy_schema=loaded_data.taxonomy.schema_url
        )
        report_files.append(producer.create_html())
    if not loaded_data.taxonomy:
        return File("reports", contained_files=report_files)
    taxonomy_producer: TaxonomyProducer = TaxonomyProducer(loaded_data.taxonomy)
    return taxonomy_producer.create_files(report_files)