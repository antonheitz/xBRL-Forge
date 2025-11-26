import json

from typing import List, Dict

from .PackageDataclasses import File, PACKAGE_EXTENSIONS
from .InputData import InputData
from .HtmlProducer import HtmlProducer
from .XbrlProducer import XbrlProducer
from .TaxonomyProducer import TaxonomyProducer

PACKAGE_EXTENSION_URIS: Dict[str, str] = {
    PACKAGE_EXTENSIONS.ZIP: "https://xbrl.org/report-package/2023",
    PACKAGE_EXTENSIONS.XBRI: "https://xbrl.org/report-package/2023/xbri",
    PACKAGE_EXTENSIONS.XBR: "https://xbrl.org/report-package/2023/xbr"
}

class PackageProducer:
    local_namespace: str
    local_namespace_prefix: str
    local_taxonomy_schema: str
    root_folder: File

    def __init__(cls, input_data: InputData, xthml_template: str = None):
        # get namespace data
        cls.local_namespace = None
        cls.local_namespace_prefix = None
        cls.local_taxonomy_schema = None
        if input_data.taxonomy:
            cls.local_namespace=input_data.taxonomy.namespace
            cls.local_namespace_prefix=input_data.taxonomy.prefix 
            cls.local_taxonomy_schema=input_data.taxonomy.schema_url
        # create reports
        inline_xbrl_reports: List[File] = []
        xbrl_reports: List[File] = []
        xhtml_reports: List[File] = []
        for report in input_data.reports:
            if report.xhtml:
                html_producer: HtmlProducer = HtmlProducer(
                    report, 
                    xthml_template=xthml_template, 
                    local_namespace=cls.local_namespace, 
                    local_namespace_prefix=cls.local_namespace_prefix, 
                    local_taxonomy_schema=cls.local_taxonomy_schema
                )
                if html_producer.ixbrl:
                    inline_xbrl_reports.append(html_producer.create_html())
                else:
                    xhtml_reports.append(html_producer.create_html())
            else:
                xbrl_producer: XbrlProducer = XbrlProducer(
                    report, 
                    local_namespace=cls.local_namespace, 
                    local_namespace_prefix=cls.local_namespace_prefix, 
                    local_taxonomy_schema=cls.local_taxonomy_schema
                )
                xbrl_reports.append(xbrl_producer.create_xbrl())
        # create taxonomy
        taxonomy_meta_inf_files: List[File] = []
        taxonomy_folder: File = None
        if input_data.taxonomy:
            taxonomy_producer: TaxonomyProducer = TaxonomyProducer(input_data.taxonomy)
            taxonomy_meta_inf_files = taxonomy_producer.get_meta_inf_files()
            taxonomy_folder = taxonomy_producer.get_taxonomy()

        package_extension: str = PACKAGE_EXTENSIONS.ZIP
        if len(inline_xbrl_reports) == 1 and not xbrl_reports:
            package_extension = PACKAGE_EXTENSIONS.XBRI
        elif len(xbrl_reports) == 1 and not inline_xbrl_reports:
            package_extension = PACKAGE_EXTENSIONS.XBR
        
        # create base folder
        root_folder_name: str = "EMPTY"
        if input_data.taxonomy:
            root_folder_name = f'{"_".join(input_data.taxonomy.metadata.name.split())}'
        elif inline_xbrl_reports:
            root_folder_name = inline_xbrl_reports[0].name.split(".")[0]
        elif xbrl_reports:
            root_folder_name = xbrl_reports[0].name.split(".")[0]
        elif xhtml_reports:
            root_folder_name = xhtml_reports[0].name.split(".")[0]
        cls.root_folder: File = File(name=root_folder_name, zip_extension=package_extension)
        
        # add content
        meta_inf_folder: File = File(name="META-INF", contained_files=taxonomy_meta_inf_files)
        cls.root_folder.contained_files.append(meta_inf_folder)
        if taxonomy_folder:
            cls.root_folder.contained_files.append(taxonomy_folder)
        if xbrl_reports or inline_xbrl_reports or xhtml_reports:
            reports_folder: File = File("reports", contained_files=xbrl_reports + inline_xbrl_reports)
            cls.root_folder.contained_files.append(reports_folder)
            if xhtml_reports:
                untagged_reports_folder: File = File("untagged_reports", contained_files=xhtml_reports)
                reports_folder.contained_files.append(untagged_reports_folder)
            # add reportPackage.json
            meta_inf_folder.contained_files.append(File(
                name="reportPackage.json",
                content=json.dumps({
                    "documentInfo": {
                        "documentType": PACKAGE_EXTENSION_URIS.get(package_extension)
                    }
                })
            ))

    def get_package(cls) -> File:
        return cls.root_folder