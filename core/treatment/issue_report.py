from datetime import datetime
from pathlib import Path

import pandas as pd

from core.ingest.issues import issues_to_dicts


def export_treatment_issues_report(issues, output_base, timestamp=None):
    if not issues:
        return ""

    output_dir = Path(output_base)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    xlsx_path = output_dir / f"treatment_issues_{timestamp}.xlsx"
    dataframe = pd.DataFrame(issues_to_dicts(issues))

    try:
        dataframe.to_excel(xlsx_path, index=False, sheet_name="issues")
        return str(xlsx_path)
    except Exception:
        csv_path = xlsx_path.with_suffix(".csv")
        dataframe.to_csv(csv_path, index=False)
        return str(csv_path)


__all__ = ["export_treatment_issues_report"]
