# Datalyst — Financial Intelligence

Phiên bản giao diện cuộc thi chạy bằng HTML5, CSS3 và JavaScript thuần qua VS Code Live Server. Trang chính là `datalyst/index.html`; trang dùng Chart.js để vẽ biểu đồ, PapaParse để đọc CSV/TXT, SheetJS để đọc Excel và Lucide cho icon. Các thư viện tải từ CDN khi mở trang, vì vậy cần kết nối internet. Không cần Python, Node.js hoặc backend để chạy website.

## Chạy bằng Live Server trên Windows

1. Mở thư mục `D:\Datalyst` trong VS Code.
2. Cài extension **Live Server** nếu chưa có.
3. Mở `datalyst/index.html` rồi nhấn **Go Live** ở thanh trạng thái.
4. Workspace có `submission_output.csv`; trang sẽ thử đọc tệp cục bộ này. Nếu Live Server không tìm thấy, nhấn **Nhập dữ liệu** và chọn tệp trên máy.

## Dữ liệu đã kiểm tra

`submission_output.csv` có 60 dòng, 31 cột, 12 `company_id`, các năm tài chính 2021–2025 và không trùng khóa công ty/năm. Đây là kết quả phân tích/cảnh báo, không phải báo cáo tài chính gốc. Tệp có tăng trưởng doanh thu (%), một số biên lợi nhuận, tỷ lệ thanh khoản/đòn bẩy, chỉ số sinh lời, dòng tiền tự do (triệu VND) và nhãn rủi ro. Sáu cột `revenue_growth_pct`, `roa_pct`, `roe_pct`, `dso_days`, `inventory_days`, `dpo_days` thiếu 12 giá trị mỗi cột. Không có doanh thu/lợi nhuận tuyệt đối, tổng tài sản, tổng nợ, tên pháp nhân hoặc ngành.

## Nhập dữ liệu

Nhấn **Nhập dữ liệu**, chọn CSV/TXT/XLSX, kiểm tra bản xem trước và trường được nhận diện rồi xác nhận. Cần có cột mã doanh nghiệp và năm tài chính (ví dụ `company_id`, `fiscal_year`). Dữ liệu được xử lý trong trình duyệt và chỉ giữ trong phiên hiện tại; không gửi lên dịch vụ ngoài.

## Chức năng và giới hạn

- Dashboard và phân tích lọc công ty/năm, có bảng tìm kiếm, biểu đồ và insight mô tả.
- Chỉ tiêu không có cột tương ứng hiển thị “Chưa có”. Tỷ lệ không bị cộng như số tiền.
- Dự báo giữ giá trị kỳ cuối làm baseline; cần chuỗi tối thiểu hai năm liên tiếp. Không đưa ra độ chính xác hoặc khoảng tin cậy giả.
- Cảnh báo hiển thị nhãn nguồn hoặc quy tắc tham khảo có thể điều chỉnh.
- Trợ lý hỏi đáp dùng quy tắc JavaScript trên dữ liệu đang nạp; chưa kết nối mô hình AI/API.

Các file Python còn lại từ phiên bản trước không tham gia chạy trang `datalyst/index.html`.
