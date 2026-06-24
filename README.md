Link: https://huhu-huhuhuhu.streamlit.app/

Flowchart:
1. Cài đặt thư viện và khởi tạo ứng dụng
   ↓
2. Xây dựng giao diện chính
   ↓
3. Người dùng Nhập văn bản (Text Area)
   ↓
4. Click "Kiểm tra"
   ↓
Kiểm tra Văn bản rỗng/ dưới 3 ký tự?
├ Có → Cảnh báo → Quay lại nhập (B3)
└─ Không → Tiền xử lý văn bản (B5)//

      ↓
6. Tìm lỗi 
      ↓
├ Không có lỗi → Thông báo (6.1)
└─ Có lỗi → Hiển thị danh sách và gợi ý (6.2)
          ↓
7. Sửa lỗi và hiển thị kết quả
          ↓
8. Dropbox "Bạn có muốn dịch đoạn văn bản này không?"
          ↓
├ Không → Kết thúc (8.1)
└─ Có → Gọi API dịch (8.2)
       ↓
Chọn ngôn ngữ (Dropdown)
       ↓
9. Hiển thị kết quả
      ↓
Kết thúc
