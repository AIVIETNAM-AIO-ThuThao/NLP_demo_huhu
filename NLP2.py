# app.py - Ứng dụng sửa lỗi chính tả và dịch văn bản

# === B0: Thư viện code, framework và ngôn ngữ ===
import streamlit as st  
from langdetect import DetectorFactory, detect  # Phát hiện ngôn ngữ
from spellchecker import SpellChecker  
from deep_translator import GoogleTranslator  # Google Translate
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

# === B1: Cấu hình trang và tiêu đề ứng dụng ===
st.set_page_config(
    page_title="Sửa lỗi chính tả & Dịch văn bản",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Sửa lỗi chính tả & Dịch văn bản")
st.markdown("---")

# === B2: Hiển thị giao diện chính ===
# Người dùng nhập văn bản
input_text = st.text_area(
    "Nhập văn bản cần kiểm tra:",
    placeholder="Nhập văn bản của bạn vào đây...",
    height=150
)

# === B3: Người dùng nhấn nút kiểm tra ===
if st.button("🔍 Kiểm tra văn bản", type="primary"):
    
    # === B4: Kiểm tra văn bản rỗng ===
    if not input_text or len(input_text.strip()) < 3:
        st.warning("⚠️ Vui lòng nhập văn bản có ít nhất 3 ký tự!")
    else:
        # === B5: Xử lý văn bản - Phát hiện ngôn ngữ gốc ===
        try:
            src_lang = detect(input_text)
            st.info(f"🔍 Ngôn ngữ phát hiện: {langcodes.get(src_lang).display_name('vi')}")
        except:
            src_lang = 'en'
            st.warning("⚠️ Không thể phát hiện ngôn ngữ, sử dụng mặc định là Tiếng Anh")
        
        # Tách từ để kiểm tra chính tả
        words = input_text.split()
        
        # === B6: Tìm lỗi chính tả ===
        misspelled = spell.unknown(words)
        
        # Khởi tạo biến lưu văn bản đã sửa
        corrected_text = input_text
        
        if not misspelled:
            # === 6.1: Không có lỗi ===
            st.success("✅ Không tìm thấy lỗi chính tả nào!")
            st.text_area("📄 Văn bản đã kiểm tra:", corrected_text, height=100, key="no_error_text")
        else:
            # === 6.2: Có lỗi - Hiển thị danh sách ===
            st.warning(f"⚠️ Phát hiện {len(misspelled)} từ sai chính tả:")
            
            # Tạo dictionary lưu từ sai và gợi ý sửa
            corrections = {}
            for word in misspelled:
                suggestions = spell.candidates(word)
                if suggestions:
                    corrected_word = list(suggestions)[0]
                    corrections[word] = corrected_word
                    st.write(f"  • '{word}' → **{corrected_word}**")
            
            # === B7: Sửa lỗi ===
            # 7.1: Tự động sửa lỗi
            corrected_text = input_text
            for wrong, correct in corrections.items():
                corrected_text = corrected_text.replace(wrong, correct)
            
            st.text_area("✏️ Văn bản đã sửa tự động:", corrected_text, height=100, key="auto_corrected")
            
            # 7.2: Người dùng sửa thủ công
            manual_edit = st.text_area(
                "📝 Chỉnh sửa thủ công (nếu cần):",
                value=corrected_text,
                height=100,
                key="manual_edit"
            )
            
            # Cập nhật văn bản nếu người dùng chỉnh sửa thủ công
            if manual_edit != corrected_text:
                corrected_text = manual_edit
        
        # === B8: Hỏi người dùng có muốn dịch không? ===
        st.markdown("---")
        st.subheader("🌐 Dịch văn bản")
        
        should_translate = st.radio(
            "Bạn có muốn dịch đoạn văn bản này không?",
            options=["❌ Không dịch", "✅ Có, tôi muốn dịch"],
            index=0,
            horizontal=True,
            key="translate_radio"
        )
        
        # === B9: Nếu có, chọn ngôn ngữ đích và dịch ===
        if should_translate == "✅ Có, tôi muốn dịch":
            # Hiển thị dropdown chọn ngôn ngữ
            target_lang = st.selectbox(
                "Chọn ngôn ngữ đích:",
                options=list(LANGUAGES.keys()),
                format_func=lambda x: LANGUAGES[x],
                index=0,  # Mặc định Tiếng Việt
                key="target_lang_select"
            )
            
            # Nút dịch
            if st.button("🌐 Dịch ngay", type="primary"):
                try:
                    # Lấy văn bản đã sửa để dịch
                    text_to_translate = corrected_text if corrected_text else input_text
                    
                    # Hiển thị văn bản đang dịch
                    st.info(f"📝 Đang dịch văn bản sang {LANGUAGES[target_lang]}...")
                    
                    # Gọi API dịch
                    translator = GoogleTranslator(source='auto', target=target_lang)
                    translated = translator.translate(text_to_translate)
                    
                    # === B10: Hiển thị kết quả dịch ===
                    st.success(f"✅ Kết quả dịch sang {LANGUAGES[target_lang]}:")
                    st.text_area("📄 Bản dịch:", translated, height=150, key="translated_output")
                    
                except Exception as e:
                    st.error(f"❌ Lỗi khi dịch: {str(e)}")
                    st.info("💡 Gợi ý: Kiểm tra kết nối internet hoặc thử lại sau.")
        else:
            # Người dùng chọn không dịch
            st.info("ℹ️ Bạn đã chọn không dịch văn bản.")

# === Hướng dẫn sử dụng (Sidebar) ===
with st.sidebar:
    st.header("📖 Hướng dẫn sử dụng")
    st.markdown("""
    **Quy trình:**
    1. 📝 **Nhập văn bản** vào ô trên
    2. 🔍 **Nhấn "Kiểm tra"** để tìm lỗi chính tả
    3. ✏️ **Sửa lỗi** (tự động hoặc thủ công)
    4. 🌐 **Chọn "Có"** nếu muốn dịch
    5. 🗣️ **Chọn ngôn ngữ đích**
    6. 🌐 **Nhấn "Dịch ngay"** để xem kết quả
    
    **Lưu ý:**
    - Tự động phát hiện ngôn ngữ gốc
    - Hỗ trợ kiểm tra chính tả tiếng Anh
    - Cần kết nối Internet để dịch
    """)
    
    