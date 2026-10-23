"""Datalyst — Financial Intelligence. Chạy bằng: streamlit run app.py"""
from __future__ import annotations
import pandas as pd
import plotly.express as px
import streamlit as st

from services.data_loader import load_default, read_table
from services.financial_metrics import available_metrics, METRICS
from services.forecasting import baseline_forecast
from services.risk_alerts import build_alerts
from services.chatbot import answer_question

st.set_page_config(page_title="Datalyst | Financial Intelligence", page_icon="◈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
.stApp {background:#f4f7fb;color:#15233b;font-family:'DM Sans',sans-serif}
[data-testid="stSidebar"]{background:#101c32}
[data-testid="stSidebar"] *{color:#e5edf8}
[data-testid="stMetric"]{background:white;border:1px solid #e5eaf2;padding:18px 20px;border-radius:15px;box-shadow:0 4px 14px #18345c08}
[data-testid="stMetricLabel"]{color:#6d7b90}
h1,h2,h3{font-family:'Manrope',sans-serif;color:#15233b}
.eyebrow{color:#0d8b82;text-transform:uppercase;letter-spacing:.14em;font-size:.72rem;font-weight:700}
.notice{background:#eaf5f4;border-left:4px solid #13a394;padding:14px 17px;border-radius:8px;color:#294958;margin:10px 0 20px}
.warning{background:#fff5e8;border-left:4px solid #f2a43a;padding:14px 17px;border-radius:8px;color:#704d1c;margin:10px 0 20px}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_default(): return load_default()

if "financial_df" not in st.session_state:
    st.session_state.financial_df = get_default()
df = st.session_state.financial_df

with st.sidebar:
    st.markdown("<div style='font:800 1.55rem Manrope;color:white;padding:12px 0'>◈ DATALYST</div><div style='color:#9db0c9;font-size:.78rem;margin-top:-12px;margin-bottom:22px'>FINANCIAL INTELLIGENCE</div>", unsafe_allow_html=True)
    page = st.radio("Điều hướng", ["Tổng quan", "Phân tích tài chính", "Dự báo", "Cảnh báo rủi ro", "AI Chatbot", "Dữ liệu", "Giới thiệu"], label_visibility="collapsed")
    st.divider()
    st.caption(f"{len(df):,} dòng dữ liệu" if not df.empty else "Chưa có dữ liệu")
    if "model_name" in df and df.model_name.notna().any(): st.caption("Nguồn có nhãn mô hình: " + str(df.model_name.dropna().iloc[0]))

def title(kicker, heading, desc):
    st.markdown(f"<div class='eyebrow'>{kicker}</div>", unsafe_allow_html=True)
    st.title(heading); st.caption(desc)

def filters(data, key):
    left, right = st.columns(2)
    companies = sorted(data.company_id.dropna().astype(str).unique())
    chosen = left.multiselect("Doanh nghiệp", companies, default=companies, key=f"co_{key}")
    years = sorted(data.fiscal_year.dropna().astype(int).unique()) if "fiscal_year" in data else []
    year_sel = right.multiselect("Năm tài chính", years, default=years, key=f"yr_{key}")
    out = data[data.company_id.astype(str).isin(chosen)]
    if year_sel: out = out[out.fiscal_year.isin(year_sel)]
    return out

def empty_state():
    st.info("Chưa có dữ liệu tương thích. Tải CSV/XLSX trong trang **Dữ liệu**; cần có company_id và fiscal_year.")

if df.empty:
    title("DATALYST", "Financial Intelligence", "Phân tích tài chính dựa trên dữ liệu của bạn")
    empty_state()
elif page == "Tổng quan":
    title("DASHBOARD", "Tổng quan tài chính", "Theo dõi các chỉ số có trong bộ dữ liệu đã nạp.")
    st.markdown("<div class='warning'><b>Phạm vi nguồn dữ liệu:</b> submission_output.csv là bảng kết quả phân tích và cảnh báo, không phải báo cáo tài chính gốc. Không có doanh thu/lợi nhuận tuyệt đối, tổng tài sản hay tổng nợ để cộng gộp.</div>", unsafe_allow_html=True)
    data = filters(df, "dash")
    n1,n2,n3,n4 = st.columns(4)
    n1.metric("Doanh nghiệp", f"{data.company_id.nunique():,}")
    n2.metric("Năm dữ liệu", f"{data.fiscal_year.nunique():,}")
    n3.metric("Bản ghi", f"{len(data):,}")
    alerts = build_alerts(data); n4.metric("Nhãn cảnh báo", f"{len(alerts):,}")
    st.markdown("### Xu hướng chỉ số")
    metrics = available_metrics(data)
    preferred = [m for m in ["revenue_growth_pct", "net_margin_pct", "free_cash_flow_vnd_mn", "debt_to_assets_pct"] if m in metrics]
    metric = st.selectbox("Chọn chỉ số", preferred or list(metrics), format_func=lambda x: metrics[x][0])
    chart_data = data.dropna(subset=[metric]).sort_values("fiscal_year")
    if not chart_data.empty:
        fig = px.line(chart_data, x="fiscal_year", y=metric, color="company_id", markers=True,
                      labels={"fiscal_year":"Năm tài chính",metric:metrics[metric][0],"company_id":"Doanh nghiệp"})
        fig.update_layout(template="plotly_white",height=390,legend_title_text="Doanh nghiệp",margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig,use_container_width=True)
    st.markdown("### Financial insights")
    if "revenue_growth_pct" in data and data.revenue_growth_pct.notna().any():
        valid = data.dropna(subset=["revenue_growth_pct"]); avg = valid.revenue_growth_pct.mean()
        lo,hi=int(valid.fiscal_year.min()),int(valid.fiscal_year.max())
        st.markdown(f"<div class='notice'>Trong {lo}–{hi}, mức tăng trưởng doanh thu đã ghi nhận trung bình là <b>{avg:.2f}%</b> trên {len(valid)} quan sát. Chỉ số mô tả tốc độ tăng trưởng, không phải doanh thu tuyệt đối.</div>",unsafe_allow_html=True)
    if "free_cash_flow_vnd_mn" in data:
        neg=data[data.free_cash_flow_vnd_mn<0]
        if not neg.empty: st.warning(f"Có {len(neg)} quan sát dòng tiền tự do âm trong khoảng năm đã chọn.")
    st.markdown("### Dữ liệu đang xem")
    show=[c for c in ["company_id","fiscal_year",*metrics.keys(),"predicted_severity","alert_tags"] if c in data]
    st.dataframe(data[show],use_container_width=True,hide_index=True)

elif page == "Phân tích tài chính":
    title("ANALYTICS", "Phân tích tài chính", "So sánh chỉ số đã có trong dữ liệu. Giá trị thiếu không được tự suy diễn.")
    data=filters(df,"analysis"); metrics=available_metrics(data)
    if not metrics: empty_state()
    else:
        metric=st.selectbox("Chỉ số",list(metrics),format_func=lambda x:metrics[x][0])
        chosen=data.dropna(subset=[metric]).sort_values(["company_id","fiscal_year"])
        if chosen.empty: st.info("Không có quan sát cho lựa chọn này.")
        else:
            fig=px.line(chosen,x="fiscal_year",y=metric,color="company_id",markers=True,
                        labels={"fiscal_year":"Năm tài chính",metric:metrics[metric][0],"company_id":"Doanh nghiệp"})
            fig.update_layout(template="plotly_white",height=410)
            st.plotly_chart(fig,use_container_width=True)
            table=chosen[["company_id","fiscal_year",metric]].rename(columns={metric:metrics[metric][0]})
            st.dataframe(table,use_container_width=True,hide_index=True)
            st.caption("Các trường tỷ lệ giữ nguyên đơn vị của nguồn (% hoặc lần). Báo cáo gốc không có trong workspace nên không tính được doanh thu, lợi nhuận hay tỷ số chưa có sẵn.")

elif page == "Dự báo":
    title("FORECAST", "Dự báo tham khảo", "Baseline minh bạch cho chuỗi thời gian ngắn; không phải khuyến nghị đầu tư.")
    metrics=available_metrics(df)
    forecastable=[m for m in ["revenue_growth_pct","net_margin_pct","free_cash_flow_vnd_mn"] if m in metrics]
    if not forecastable: st.warning("Thiếu chỉ số phù hợp để lập baseline.")
    else:
        c1,c2,c3=st.columns(3)
        co=c1.selectbox("Doanh nghiệp",sorted(df.company_id.dropna().unique()))
        metric=c2.selectbox("Chỉ số",forecastable,format_func=lambda x:metrics[x][0])
        periods=c3.selectbox("Số năm hiển thị",[1,2,3],index=1)
        hist=df[df.company_id.astype(str)==str(co)]
        forecast,message=baseline_forecast(hist,metric,periods)
        st.markdown(f"<div class='warning'>{message}</div>",unsafe_allow_html=True)
        if forecast is not None:
            fig=px.line(forecast,x="fiscal_year",y=metric,color="series",markers=True,
                        labels={"fiscal_year":"Năm tài chính",metric:metrics[metric][0],"series":"Loại dữ liệu"})
            fig.update_layout(template="plotly_white",height=400)
            st.plotly_chart(fig,use_container_width=True)
            st.caption("Không hiển thị MAE/RMSE hoặc khoảng tin cậy: 5 điểm dữ liệu mỗi doanh nghiệp không đủ để đưa ra đánh giá tin cậy.")

elif page == "Cảnh báo rủi ro":
    title("RISK MONITOR", "Cảnh báo rủi ro", "Các nhãn được nhập từ kết quả quy tắc trong CSV; không phải khẳng định về tương lai.")
    alerts=build_alerts(df)
    if alerts.empty: st.success("Không có nhãn cảnh báo trong dữ liệu hiện tại.")
    else:
        co=st.multiselect("Doanh nghiệp",sorted(alerts.company_id.astype(str).unique()),default=sorted(alerts.company_id.astype(str).unique()))
        alerts=alerts[alerts.company_id.astype(str).isin(co)]
        st.metric("Nhãn cảnh báo trong lựa chọn",len(alerts))
        st.dataframe(alerts[["company_id","fiscal_year","risk","severity","risk_score","evidence","basis"]],use_container_width=True,hide_index=True)
        with st.expander("Cách đọc"):
            st.write("Mức độ và điểm số được hiển thị nguyên trạng từ submission_output.csv. Cột căn cứ phản ánh trường/quy tắc nguồn; ngưỡng trong nguồn chưa được kiểm định như chuẩn ngành.")

elif page == "AI Chatbot":
    title("DATA ASSISTANT", "Hỏi đáp dữ liệu", "Truy vấn xác định trên dữ liệu hiện nạp; chưa kết nối mô hình ngôn ngữ/API.")
    st.markdown("<div class='notice'>Chế độ cơ bản đang hoạt động. Câu trả lời lấy số trực tiếp từ bảng; không gửi dữ liệu ra dịch vụ bên ngoài.</div>",unsafe_allow_html=True)
    if "chat" not in st.session_state: st.session_state.chat=[]
    for role,content in st.session_state.chat:
        with st.chat_message(role): st.markdown(content)
    prompt=st.chat_input("Ví dụ: C001 có biên lợi nhuận nào theo năm? / Công ty nào có ROA cao nhất?")
    if prompt:
        st.session_state.chat.append(("user",prompt))
        reply=answer_question(prompt,df)
        st.session_state.chat.append(("assistant",reply))
        st.rerun()

elif page == "Dữ liệu":
    title("DATA MANAGEMENT", "Nhập và quản lý dữ liệu", "Tải CSV hoặc Excel vào bộ nhớ phiên; dữ liệu gốc không bị chỉnh sửa.")
    uploaded=st.file_uploader("Chọn CSV, XLSX hoặc XLS",type=["csv","xlsx","xls"])
    if uploaded:
        try:
            if uploaded.name.lower().endswith((".xlsx",".xls")):
                sheets=pd.ExcelFile(uploaded).sheet_names
                sheet=st.selectbox("Sheet",sheets)
                uploaded.seek(0); incoming=read_table(uploaded,sheet)
            else: incoming=read_table(uploaded)
            st.success(f"Đã đọc {uploaded.name}: {len(incoming):,} dòng × {len(incoming.columns)} cột.")
            dup=incoming.duplicated(["company_id","fiscal_year"],keep=False)
            a,b,c=st.columns(3); a.metric("Dòng trùng khóa",int(dup.sum())); b.metric("Giá trị thiếu",int(incoming.isna().sum().sum())); c.metric("Công ty",int(incoming.company_id.nunique()))
            st.dataframe(incoming.head(30),use_container_width=True,hide_index=True)
            st.caption("Khóa công ty/năm phải duy nhất để diễn giải chuỗi thời gian. Cột không nhận dạng số được giữ nguyên; hãy kiểm tra bản xem trước.")
            if st.button("Dùng dữ liệu này cho ứng dụng",type="primary"):
                if dup.any(): st.error("Khóa company_id + fiscal_year bị trùng. Hãy sửa dữ liệu rồi tải lại.")
                else:
                    st.session_state.financial_df=incoming; st.session_state.chat=[]
                    st.success("Đã thay bộ dữ liệu trong phiên hiện tại."); st.rerun()
        except Exception as exc: st.error(f"Không đọc được tệp: {exc}")
    else:
        st.info("Đang dùng submission_output.csv có sẵn trong dự án. Tải tệp mới và nhấn nút để thay dữ liệu trong phiên.")
    st.markdown("### Kiểm tra dữ liệu hiện tại")
    st.write(f"**Kích thước:** {len(df):,} dòng × {len(df.columns)} cột")
    st.write("**Thiếu theo cột:**")
    missing=df.isna().sum(); st.dataframe(missing[missing>0].rename("Số giá trị thiếu").to_frame(),use_container_width=True)
    st.write("**Kiểu cột:**")
    st.dataframe(pd.DataFrame({"Cột":df.columns,"Kiểu dữ liệu":df.dtypes.astype(str).values}),use_container_width=True,hide_index=True)

else:
    title("ABOUT", "Về Datalyst", "Financial Intelligence — công cụ khám phá dữ liệu tài chính cho trình diễn và phân tích.")
    st.markdown("### Phạm vi dữ liệu hiện có")
    st.write("Workspace có submission_output.csv gồm 60 bản ghi, 12 mã công ty (C001–C012), năm 2021–2025. Đây là đầu ra mô hình/quy tắc với các tỷ lệ và nhãn; không có dữ liệu báo cáo gốc hoặc thông tin tên/ngành doanh nghiệp.")
    st.markdown("### Giới hạn cần biết")
    st.write("Datalyst chỉ thể hiện trường có sẵn. Không thể tính tổng doanh thu/lợi nhuận/tài sản/nợ hay so sánh theo ngành. Dự báo giữ nguyên giá trị kỳ gần nhất làm baseline, không phải mô hình có độ chính xác đã chứng minh. Chatbot hoạt động theo mẫu câu cơ bản và chưa cần API key.")
    st.markdown("### Chạy trên Windows")
    st.code("cd D:\\Datalyst\npy -m venv .venv\n.venv\\Scripts\\Activate.ps1\npython -m pip install -r requirements.txt\nstreamlit run app.py",language="powershell")

st.markdown("<div style='text-align:center;color:#8794a7;font-size:.75rem;padding:30px 0 8px'>DATALYST · Phân tích hỗ trợ quyết định, không thay thế tư vấn tài chính hoặc kiểm toán.</div>",unsafe_allow_html=True)
