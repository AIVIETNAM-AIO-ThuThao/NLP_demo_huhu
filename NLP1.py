import streamlit as st                                                         

def preprocess_text(text):   # Định nghĩa hàm tiền xử lý văn bản, nhận đầu vào là chuỗi text
    text = text.lower()   # Chuyển tất cả thành chữ thường 
    text = text.strip()   # Xóa khoảng trắng ở đầu và cuối chuỗi
    return text           # Trả về văn bản đã được xử lý

def predict_sentiment(text): # Hàm dự đoán cảm xúc, nhận đầu vào là chuỗi text đã xử lý
    # logic đơn giản, sau này có thể thay bằng AI model
    if "good" in text or "great" in text:     # nếu văn bản có chứa từ "good" HOẶC "great"
        return "Positive"  # có → Trả về "Positive" (Tích cực)
    return "Neutral"       # không → Trả về "Neutral" (Trung tính)

st.title("Sentiment Analysis Demo")   # Hiển thị tiêu đề chính trên giao diện web

text = st.text_area("Nhập văn bản cần phân tích") # Tạo ô nhập văn bản nhiều dòng, lưu nội dung vào biến text

if st.button("Dự đoán"):     # kiểm tra nếu người dùng có click vào nút
    if text.strip() == "":   # Kiểm tra nếu văn bản rỗng hoặc chỉ có khoảng trắng
        st.warning("Vui lòng nhập văn bản.")  # Nếu rỗng → cảnh báo màu vàng
    else:                                     # Nếu có nội dung
        processed_text = preprocess_text(text)  # Gọi hàm tiền xử lý, lưu kết quả vào biến processed_text
        prediction = predict_sentiment(processed_text)   # Gọi hàm dự đoán cảm xúc, lưu kết quả vào biến prediction
        
        st.write("Văn bản sau xử lý:", processed_text)  # Hiển thị văn bản đã được tiền xử lý ra giao diện
        st.success(f"Kết quả dự đoán: {prediction}")    # Hiển thị kết quả dự đoán với màu xanh thành công