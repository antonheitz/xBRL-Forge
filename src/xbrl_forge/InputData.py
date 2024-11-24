from dataclasses import dataclass
from typing import List

from .ContentDataclasses import ContentDocument
from .TaxonomyDataclasses import TaxonomyDocument

@dataclass
class InputData:
    taxonomy: TaxonomyDocument
    reports: List[ContentDocument]

    @classmethod
    def from_dict(cls, data: dict) -> 'InputData':
        return cls(
            taxonomy=TaxonomyDocument.from_dict(data.get("taxonomy")) if "taxonomy" in data else None,
            reports=[ContentDocument.from_dict(report) for report in data.get("reports", [])]
        )

    def to_dict(cls) -> dict:
        return {
            "taxonomy": cls.taxonomy.to_dict(),
            "reports": [report.to_dict() for report in cls.reports]
        }