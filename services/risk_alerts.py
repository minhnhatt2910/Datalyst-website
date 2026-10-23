"""Cảnh báo giải thích được dựa trên nhãn và chỉ số trong CSV nguồn."""
import pandas as pd

def build_alerts(df):
    rows = []
    for _, r in df.iterrows():
        raw_tags = r.get("alert_tags", "")
        tags = "" if pd.isna(raw_tags) else str(raw_tags)
        if tags in ("", "nan", "<NA>"):
            continue
        for tag in tags.split(";"):
            tag = tag.strip()
            if not tag:
                continue
            rows.append({
                "company_id": r.get("company_id"), "fiscal_year": r.get("fiscal_year"),
                "risk": tag.replace("_", " ").title(),
                "severity": str(r.get("predicted_severity", "Chưa xác định")),
                "risk_score": r.get("risk_score"), "evidence": r.get("alert_reason", ""),
                "basis": r.get("evidence_fields", ""),
                "health": r.get("predicted_overall_health", ""),
            })
    return pd.DataFrame(rows)
