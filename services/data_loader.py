"""Đọc và chuẩn hóa bản sao dữ liệu tài chính."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "submission_output.csv"

NUMERIC_COLUMNS = [
    "fiscal_year", "revenue_growth_pct", "gross_margin_pct", "operating_margin_pct",
    "net_margin_pct", "current_ratio_x", "quick_ratio_x", "debt_to_assets_pct",
    "debt_to_equity_x", "roa_pct", "roe_pct", "cfo_margin_pct",
    "cfo_to_net_income_x", "free_cash_flow_vnd_mn", "dso_days", "inventory_days",
    "dpo_days", "interest_coverage_x", "working_capital_vnd_mn", "risk_score",
    "priority_rank", "confidence", "processing_time_ms",
]

def read_table(upload, sheet_name=0) -> pd.DataFrame:
    """Đọc CSV/Excel mà không sửa file nguồn; chuẩn hóa kiểu số và khóa."""
    name = getattr(upload, "name", str(upload))
    suffix = Path(name).suffix.lower()
    if suffix == ".csv":
        try:
            frame = pd.read_csv(upload, encoding="utf-8-sig")
        except UnicodeDecodeError:
            upload.seek(0)
            frame = pd.read_csv(upload, encoding="cp1252")
    elif suffix in (".xlsx", ".xls"):
        frame = pd.read_excel(upload, sheet_name=sheet_name)
    else:
        raise ValueError("Định dạng chưa hỗ trợ. Hãy chọn CSV, XLSX hoặc XLS.")
    return normalize(frame)

def normalize(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out.columns = [str(c).strip().lower().replace(" ", "_") for c in out.columns]
    if "company_id" not in out or "fiscal_year" not in out:
        raise ValueError("Cần có hai cột khóa company_id và fiscal_year để phân tích.")
    out["company_id"] = out["company_id"].astype("string").str.strip()
    for col in NUMERIC_COLUMNS:
        if col in out:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out.sort_values(["company_id", "fiscal_year"], kind="stable").reset_index(drop=True)

def load_default() -> pd.DataFrame:
    if not DEFAULT_DATA.exists():
        return pd.DataFrame()
    return read_table(DEFAULT_DATA)
