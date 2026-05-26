from dataclasses import dataclass

import pandas as pd

from settings import INGEST_SHEET_NAME, INGEST_WORKBOOK_PATH


@dataclass(frozen=True)
class IngestCatalogRow:
    sheet_row: int
    data: object

    def get(self, key, default=None):
        return self.data.get(key, default)


class IngestRepository:
    def iter_rows(self):
        raise NotImplementedError

    def count_rows(self):
        return sum(1 for _row in self.iter_rows())


class ExcelIngestRepository(IngestRepository):
    def __init__(self, workbook_path=INGEST_WORKBOOK_PATH, sheet_name=INGEST_SHEET_NAME):
        self.workbook_path = workbook_path
        self.sheet_name = sheet_name

    def read_dataframe(self):
        return pd.read_excel(self.workbook_path, sheet_name=self.sheet_name)

    def iter_rows(self):
        dataframe = self.read_dataframe()
        for idx, row in dataframe.iterrows():
            yield IngestCatalogRow(sheet_row=idx + 2, data=row)

    def count_rows(self):
        return len(self.read_dataframe())


def build_ingest_repository(
    workbook_path=INGEST_WORKBOOK_PATH,
    sheet_name=INGEST_SHEET_NAME,
    repository=None,
):
    if repository is not None:
        return repository
    return ExcelIngestRepository(
        workbook_path=workbook_path,
        sheet_name=sheet_name,
    )


__all__ = [
    "ExcelIngestRepository",
    "IngestCatalogRow",
    "IngestRepository",
    "build_ingest_repository",
]
