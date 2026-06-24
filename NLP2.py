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

# === B2: Khởi tạo session state ===
if 'corrected_text' not in st.session_state:
    st.session_state.corrected_text = ""
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = ""
if 'show_translate_section' not in st.session_state:
    st.session_state.show_translate_section = False
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""
if 'target_lang' not in st.session_state:
    st.session_state.target_lang = 'vi'
if 'check_performed' not in st.session_state:
    st.session_state.check_performed = False

# === B3: Người dùng nhập văn bản ===
input_text = st.text_area(
    "📝 Nhập văn bản cần kiểm tra:",
    placeholder="Nhập văn bản của bạn vào đây...",
    height=150,
    key="input_area"
)

# Cập nhật session state
if input_text:
    st.session_state.input_text = input_text

# === B4: Nút kiểm tra ===
if st.button("🔍 Kiểm tra văn bản", type="primary", use_container_width=True):
    st.session_state.check_performed = True
    st.session_state.translated_text = ""
    
    # Kiểm tra văn bản rỗng
    if not input_text or len(input_text.strip()) < 3:
        st.warning("⚠️ Vui lòng nhập văn bản có ít nhất 3 ký tự!")
        st.session_state.show_translate_section = False
    else:
        # === Xử lý văn bản - Phát hiện ngôn ngữ gốc ===
        try:
            src_lang = detect(input_text)
            st.info(f"🔍 Ngôn ngữ phát hiện: {langcodes.get(src_lang).display_name('vi')}")
        except:
            src_lang = 'en'
            st.warning("⚠️ Không thể phát hiện ngôn ngữ, sử dụng mặc định là Tiếng Anh")
        
        # Tách từ để kiểm tra chính tả
        words = input_text.split()
        
        # === Tìm lỗi chính tả ===
        misspelled = spell.unknown(words)
        
        # Khởi tạo biến lưu văn bản đã sửa
        corrected_text = input_text
        
        if not misspelled:
            # === Không có lỗi ===
            st.success("✅ Không tìm thấy lỗi chính tả nào!")
            st.text_area("📄 Văn bản đã kiểm tra:", corrected_text, height=100, key="no_error")
        else:
            # === Có lỗi - Hiển thị danh sách ===
            st.warning(f"⚠️ Phát hiện {len(misspelled)} từ sai chính tả:")
            
            # Tạo dictionary lưu từ sai và gợi ý sửa
            corrections = {}
            for word in misspelled:
                suggestions = spell.candidates(word)
                if suggestions:
                    corrected_word = list(suggestions)[0]
                    corrections[word] = corrected_word
                    st.write(f"  • '{word}' → **{corrected_word}**")
            
            # === Tự động sửa lỗi ===
            corrected_text = input_text
            for wrong, correct in corrections.items():
                corrected_text = corrected_text.replace(wrong, correct)
            
            st.text_area("✏️ Văn bản đã sửa tự động:", corrected_text, height=100, key="auto_correct")
            
            # === Người dùng sửa thủ công ===
            manual_edit = st.text_area(
                "📝 Chỉnh sửa thủ công (nếu cần):",
                value=corrected_text,
                height=100,
                key="manual_edit"
            )
            
            # Cập nhật văn bản nếu người dùng chỉnh sửa thủ công
            if manual_edit != corrected_text:
                corrected_text = manual_edit
        
        # Lưu vào session state
        st.session_state.corrected_text = corrected_text
        st.session_state.show_translate_section = True

# === B5: Hỏi người dùng có muốn dịch không? ===
if st.session_state.show_translate_section and st.session_state.corrected_text:
    st.markdown("---")
    st.subheader("🌐 Dịch văn bản")
    
    # Hiển thị văn bản sẽ được dịch
    st.info(f"📝 Văn bản sau khi sửa: '{st.session_state.corrected_text[:100]}...'")
    
    # === Radio button hỏi người dùng có muốn dịch không ===
    should_translate = st.radio(
        "Bạn có muốn dịch đoạn văn bản này không?",
        options=["❌ Không", "✅ Có, tôi muốn dịch"],
        index=0,
        horizontal=True,
        key="translate_radio"
    )
    
    # === B6: Nếu người dùng chọn "Có" ===
    if should_translate == "✅ Có, tôi muốn dịch":
        # Hiển thị dropdown chọn ngôn ngữ đích
        target_lang = st.selectbox(
            "🌐 Chọn ngôn ngữ đích:",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            index=0,
            key="target_lang_select"
        )
        
        # Lưu ngôn ngữ đã chọn
        st.session_state.target_lang = target_lang
        
        # === B7: Nút dịch ===
        if st.button("🌐 Dịch ngay", type="primary", use_container_width=True):
            try:
                # Lấy văn bản đã sửa để dịch
                text_to_translate = st.session_state.corrected_text
                
                with st.spinner(f"🔄 Đang dịch sang {LANGUAGES[target_lang]}..."):
                    # Gọi API dịch
                    translator = GoogleTranslator(source='auto', target=target_lang)
                    translated = translator.translate(text_to_translate)
                    
                    # Lưu vào session state
                    st.session_state.translated_text = translated
                    
                    # === B8: Hiển thị kết quả dịch ===
                    st.markdown("---")
                    st.success(f"✅ Kết quả dịch sang {LANGUAGES[target_lang]}:")
                    st.text_area("📄 Bản dịch:", translated, height=150, key="translated_result")
                    
            except Exception as e:
                st.error(f"❌ Lỗi khi dịch: {str(e)}")
                st.info("💡 Gợi ý: Kiểm tra kết nối internet hoặc thử lại sau.")
    
    else:
        # Người dùng chọn không dịch
        st.info("ℹ️ Bạn đã chọn không dịch văn bản.")

# === B9: Nút làm mới ===
st.markdown("---")
if st.button("🔄 Làm mới", type="secondary", use_container_width=True):
    # Reset tất cả session state
    for key in ['corrected_text', 'translated_text', 'show_translate_section', 'input_text', 'check_performed']:
        if key in st.session_state:
            st.session_state[key] = "" if key != 'check_performed' else False
    st.session_state.target_lang = 'vi'
    st.rerun()

# === Hướng dẫn sử dụng (Sidebar) ===
with st.sidebar:
    st.header("📖 Hướng dẫn sử dụng")
    st.markdown("""
    **Quy trình:**
    1. 📝 **Nhập văn bản** vào ô trên
    2. 🔍 **Nhấn "Kiểm tra"** để tìm lỗi chính tả
    3. ✏️ **Sửa lỗi** (tự động hoặc thủ công)
    4. ❓ **Chọn "Có"** nếu muốn dịch
    5. 🌐 **Chọn ngôn ngữ đích** từ dropdown
    6. 🌐 **Nhấn "Dịch ngay"** để xem kết quả
    
    **Lưu ý:**
    - Tự động phát hiện ngôn ngữ gốc
    - Hỗ trợ kiểm tra chính tả tiếng Anh
    - Cần kết nối Internet để dịch
    - Nhấn **"Làm mới"** để bắt đầu lại
    """)
    
    st.markdown("---")
    st.caption("✨ Phiên bản 4.0 - Hoàn chỉnh theo yêu cầu")

# Debug - Hiển thị trạng thái (có thể xóa sau khi test)
with st.expander("🔧 Debug Info"):
    st.write("Session State:", {
        'show_translate_section': st.session_state.show_translate_section,
        'corrected_text': st.session_state.corrected_text[:50] + '...' if st.session_state.corrected_text else '',
        'translated_text': st.session_state.translated_text[:50] + '...' if st.session_state.translated_text else '',
        'target_lang': st.session_state.target_lang,
        'check_performed': st.session_state.check_performed
    })