"""Hỏi đáp xác định trên dữ liệu, không bịa số và không gọi API ngoài."""
import pandas as pd
from .risk_alerts import build_alerts
from .financial_metrics import METRICS

def answer_question(question, df):
    q = question.casefold()
    companies = df.company_id.dropna().astype(str).unique().tolist()
    company = next((c for c in companies if c.casefold() in q), None)
    if any(k in q for k in ("cảnh báo", "rủi ro", "alert")):
        alerts = build_alerts(df)
        if company: alerts = alerts[alerts.company_id.astype(str) == company]
        if alerts.empty: return "Không tìm thấy cảnh báo phù hợp trong dữ liệu đang nạp."
        latest = alerts.sort_values("fiscal_year").tail(8)
        return "Các cảnh báo tìm thấy (theo nhãn nguồn):\n" + "\n".join(
            f"• {r.company_id}, {int(r.fiscal_year)}: {r.risk} — mức {r.severity}; {r.evidence}"
            for r in latest.itertuples())
    metric = next((m for m in METRICS if m.replace("_", " ") in q), None)
    if not metric:
        aliases = {"doanh thu": "revenue_growth_pct", "tăng trưởng": "revenue_growth_pct",
                   "biên lợi nhuận": "net_margin_pct", "dòng tiền": "free_cash_flow_vnd_mn",
                   "thanh khoản": "current_ratio_x", "nợ": "debt_to_assets_pct"}
        metric = next((v for k, v in aliases.items() if k in q), None)
    if not metric or metric not in df:
        return "Mình chưa nhận diện được chỉ số. Hãy hỏi về tăng trưởng doanh thu, biên lợi nhuận, dòng tiền, thanh khoản, nợ hoặc cảnh báo."
    data = df.dropna(subset=[metric]).copy()
    if company: data = data[data.company_id.astype(str) == company]
    if data.empty: return "Không có dữ liệu cho chỉ số/doanh nghiệp được hỏi."
    data = data.sort_values("fiscal_year")
    if any(k in q for k in ("cao nhất", "lớn nhất", "top")):
        year = int(data.fiscal_year.max()); latest = data[data.fiscal_year == year]
        row = latest.loc[latest[metric].idxmax()]
        return f"{row.company_id} có {METRICS[metric][0].lower()} cao nhất năm {year}: {row[metric]:,.2f}{METRICS[metric][1]}."
    rows = data.tail(5)
    return f"{company + ': ' if company else ''}{METRICS[metric][0]} theo năm:\n" + "\n".join(
        f"• {int(r.fiscal_year)}: {r[metric]:,.2f}{METRICS[metric][1]}" for _, r in rows.iterrows())
