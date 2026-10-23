"""Các phép tính chỉ dùng trường có sẵn; tỷ lệ phần trăm được giữ nguyên đơn vị."""
import numpy as np
import pandas as pd

METRICS = {
    "revenue_growth_pct": ("Tăng trưởng doanh thu (%)", "%"),
    "gross_margin_pct": ("Biên lợi nhuận gộp (%)", "%"),
    "operating_margin_pct": ("Biên lợi nhuận hoạt động (%)", "%"),
    "net_margin_pct": ("Biên lợi nhuận ròng (%)", "%"),
    "current_ratio_x": ("Thanh toán hiện hành (lần)", "x"),
    "quick_ratio_x": ("Thanh toán nhanh (lần)", "x"),
    "debt_to_assets_pct": ("Nợ / tài sản (%)", "%"),
    "debt_to_equity_x": ("Nợ / vốn chủ sở hữu (lần)", "x"),
    "roa_pct": ("ROA (%)", "%"), "roe_pct": ("ROE (%)", "%"),
    "cfo_margin_pct": ("Biên dòng tiền HĐKD (%)", "%"),
    "free_cash_flow_vnd_mn": ("Dòng tiền tự do (triệu VND)", " triệu VND"),
    "working_capital_vnd_mn": ("Vốn lưu động (triệu VND)", " triệu VND"),
    "interest_coverage_x": ("Khả năng trả lãi (lần)", "x"),
}

def available_metrics(df):
    return {k: v for k, v in METRICS.items() if k in df and df[k].notna().any()}

def safe_divide(numerator, denominator):
    """Chia an toàn; mẫu số thiếu hoặc bằng 0 cho kết quả NaN."""
    den = pd.to_numeric(denominator, errors="coerce").replace(0, np.nan)
    return pd.to_numeric(numerator, errors="coerce") / den

def metric_summary(df, metric):
    valid = df[metric].dropna()
    return {"count": int(valid.size), "mean": valid.mean() if len(valid) else np.nan,
            "latest": valid.iloc[-1] if len(valid) else np.nan}
