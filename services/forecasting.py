"""Baseline tham khảo, không gọi là dự báo tin cậy khi chỉ có chuỗi ngắn."""
import numpy as np
import pandas as pd

def baseline_forecast(frame, metric, periods=2):
    series = frame[["fiscal_year", metric]].dropna().sort_values("fiscal_year")
    if len(series) < 2:
        return None, "Cần ít nhất 2 quan sát hợp lệ để tạo baseline."
    years = series.fiscal_year.astype(int).to_numpy()
    vals = series[metric].astype(float).to_numpy()
    gaps = np.diff(years)
    if len(gaps) and not np.all(gaps == 1):
        return None, "Chuỗi năm bị gián đoạn; không tạo đường dự báo."
    last_year, last_value = int(years[-1]), float(vals[-1])
    # Naive baseline: giữ giá trị kỳ gần nhất. Tránh ước lượng xu hướng từ 5 điểm.
    result = pd.DataFrame({"fiscal_year": range(last_year + 1, last_year + periods + 1),
                           metric: [last_value] * periods, "series": "Baseline tham khảo"})
    history = series.copy(); history["series"] = "Lịch sử"
    return pd.concat([history, result], ignore_index=True), (
        f"Baseline giữ nguyên mức {last_value:,.2f} của năm {last_year}; "
        f"chỉ có {len(series)} quan sát, không phải dự báo đã được xác nhận."
    )
