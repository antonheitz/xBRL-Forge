from dataclasses import dataclass
from typing import Dict, List

from .ContentDataclasses import ContentDocument
from .TaxonomyDataclasses import TaxonomyDocument

@dataclass
class InputData:
    taxonomy: TaxonomyDocument
    reports: List[ContentDocument]

    @classmethod
    def from_dict(cls, data: dict) -> 'InputData':
        return cls(
            taxonomy=TaxonomyDocument.from_dict(data.get("taxonomy")) if "taxonomy" in data and data.get("taxonomy") else None,
            reports=[ContentDocument.from_dict(report) for report in data.get("reports", [])]
        )
    
    @classmethod
    def combine(cls, input_data_list: List["InputData"]) -> 'InputData':
        # combine taxonomies and update reports if necessary
        available_taxonomy_input_data: List[InputData] = [data for data in input_data_list if data.taxonomy]
        available_taxonomy_input_data.sort(key=lambda data: data.taxonomy.priority, reverse=True)
        target_taxonomy: TaxonomyDocument = None
        if available_taxonomy_input_data:
            target_taxonomy = available_taxonomy_input_data[0].taxonomy
            available_taxonomy_input_data = available_taxonomy_input_data[1:]
        for additional_data in available_taxonomy_input_data:
            update_element_map = target_taxonomy.add_taxonomy(additional_data.taxonomy)
            # update elements that were renamed in content documents
            for content_document in additional_data.reports:
                for content_item in content_document.content:
                    content_item.update_tags_elements(update_element_map)
        # sort and combine reports
        sorted_reports: Dict[str, List[ContentDocument]] = {}
        for input_data in input_data_list:
            for report in input_data.reports:
                if not report.name in sorted_reports:
                    sorted_reports[report.name] = []
                sorted_reports[report.name].append(report)
        combined_documents: List[ContentDocument] = []
        for report_name in sorted_reports:
            combined_documents.append(ContentDocument.combine(sorted_reports[report_name]))
        return cls(
            taxonomy=target_taxonomy,
            reports=combined_documents
        )
        

    def to_dict(cls) -> dict:
        return {
            "taxonomy": cls.taxonomy.to_dict() if cls.taxonomy else None,
            "reports": [report.to_dict() for report in cls.reports]
        }