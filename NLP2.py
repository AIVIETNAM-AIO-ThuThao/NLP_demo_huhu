#B0. Thư viện code, framework và ngôn ngữ

import streamlit as st  
from langdetect import DetectorFactory, detect  # Phát hiện ngôn ngữ
from spellchecker import SpellChecker  
from deep_translator import GoogleTranslator  # DGoogle Translate
import langcodes  # Xử lý mã ngôn ngữ

# Cố định seed để kết quả phát hiện ngôn ngữ nhất quán
DetectorFactory.seed = 0

# Khởi tạo spell checker
spell = SpellChecker()

# Danh sách ngôn ngữ hỗ trợ dịch
LANGUAGES = {
    'vi': 'Tiếng Việt',
    'en': 'Tiếng Anh',
    'zh-CN': 'Tiếng Trung (Giản thể)',
    'ja': 'Tiếng Nhật',
    'ko': 'Tiếng Hàn',
    'fr': 'Tiếng Pháp',
    'de': 'Tiếng Đức',
    'es': 'Tiếng Tây Ban Nha',
    'ru': 'Tiếng Nga',
    'th': 'Tiếng Thái'
}

# B1. Cấu hình trang và tiêu đề ứng dụng
st.set_page_config(
    page_title="Sửa lỗi chính tả & Dịch văn bản",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Sửa lỗi chính tả & Dịch văn bản")
st.markdown("***")

# Bước 3: Người dùng nhập văn bản và chọn ngôn ngữ
input_text = st.text_area(
    "Nhập văn bản cần kiểm tra:",
    placeholder="Nhập văn bản của bạn vào đây...",
    height=150
)

target_lang = st.selectbox(
    "Chọn ngôn ngữ đích:",
    options=list(LANGUAGES.keys()),
    format_func=lambda x: LANGUAGES[x],
    index=0  # Mặc định chọn Tiếng Việt
)

# B4. Kiểm tra văn bản
if st.button("🔍 Kiểm tra văn bản", type="primary"):
    #Kiểm tra văn bản rỗng?
    if not input_text or len(input_text.strip()) < 3:
        st.warning("⚠️ Vui lòng nhập văn bản có ít nhất 3 ký tự!")
    else:
        # B5: Xử lý văn bản 
        # Phát hiện ngôn ngữ gốc
        try:
            src_lang = detect(input_text)
            st.info(f"🔍 Ngôn ngữ phát hiện: {langcodes.get(src_lang).display_name('vi')}")
        except:
            src_lang = 'en'  # Mặc định nếu không phát hiện được
            st.warning("⚠️ Không thể phát hiện ngôn ngữ, sử dụng mặc định là Tiếng Anh")
        
        # Tách từ để kiểm tra chính tả
        words = input_text.split()
        
        # B.6: Tìm lỗi chính tả
        # Tìm từ sai chính tả
        misspelled = spell.unknown(words)
        
        if not misspelled:
            # 6.1: Không có lỗi
            st.success("✅ Không tìm thấy lỗi chính tả nào!")
            corrected_text = input_text
            st.text_area("Văn bản đã kiểm tra:", corrected_text, height=100)
        else:
            # 6.2: Có lỗi - Hiển thị danh sách từ sai
            st.warning(f"⚠️ Phát hiện {len(misspelled)} từ sai chính tả:")
            
            # Tạo dictionary lưu từ sai và gợi ý sửa
            corrections = {}
            for word in misspelled:
                suggestions = spell.candidates(word)
                if suggestions:
                    # Lấy gợi ý đầu tiên (gần đúng nhất)
                    corrected_word = list(suggestions)[0]
                    corrections[word] = corrected_word
                    st.write(f"  • '{word}' → **{corrected_word}**")
            
            # Bước 7: Sửa lỗi
            # 7.1. Tự động sửa lỗi
            corrected_text = input_text
            for wrong, correct in corrections.items():
                corrected_text = corrected_text.replace(wrong, correct)
            
            st.text_area("✏️ Văn bản đã sửa:", corrected_text, height=100)
            
            # 7.2. Người dùng sửa thủ công
            manual_edit = st.text_area(
                "Chỉnh sửa thủ công (nếu cần):",
                value=corrected_text,
                height=100
            )
            
            # Cập nhật văn bản đã sửa nếu người dùng chỉnh sửa thủ công
            if manual_edit != corrected_text:
                corrected_text = manual_edit
        
        # Bước 8: Dịch văn bản (nếu người dùng muốn)
        st.markdown("***")
        should_translate = st.radio(
            "Bạn có muốn dịch đoạn văn bản này không?",
            options=["Không", "Có"],
            index=0,
            horizontal=True
        )
        
        # 8.2. Gọi API dịch
        if should_translate == "Có":
            try:
                # Lấy văn bản đã sửa (hoặc gốc nếu không có lỗi)
                text_to_translate = corrected_text if 'corrected_text' in locals() else input_text
                
                # Dịch sang ngôn ngữ đã chọn
                translator = GoogleTranslator(source='auto', target=target_lang)
                translated = translator.translate(text_to_translate)
                
                # Bước 9. Hiển thị kết quả dịch
                st.success(f"✅ Kết quả dịch sang {LANGUAGES[target_lang]}:")
                st.text_area("Bản dịch:", translated, height=150, key="translated_output")
                
            except Exception as e:
                st.error(f"❌ Lỗi khi dịch: {str(e)}")
        

# Hướng dẫn sử dụng
with st.sidebar:
    st.header("📖 Hướng dẫn")
    st.markdown("""
    1. **Nhập văn bản** vào ô trên
    2. **Chọn ngôn ngữ** bạn muốn dịch
    3. Nhấn **"Kiểm tra"** để tìm lỗi
    4. **Sửa lỗi** nếu có
    5. Chọn **"Có"** nếu muốn dịch
    6. Xem kết quả!
    
    📌 **Lưu ý:**
    - Ứng dụng tự động phát hiện ngôn ngữ gốc
    - Hỗ trợ kiểm tra chính tả tiếng Anh
    - Có thể sửa thủ công nếu cần
    """)