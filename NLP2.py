"""
Ứng dụng Sửa lỗi chính tả và Dịch văn bản. Cho phép người dùng:
1. Nhập văn bản
2. Kiểm tra và sửa lỗi chính tả tự động/thủ công
3. Dịch văn bản sang nhiều ngôn ngữ khác nhau
4. Không hoạt động tốt nếu kiểm tra chính tả tiếng Việt
"""

#  B0: Thư viện code, framework và ngôn ngữ 
import streamlit as st
from langdetect import DetectorFactory, detect
from spellchecker import SpellChecker
from deep_translator import GoogleTranslator
from nltk.tokenize import TreebankWordDetokenizer, wordpunct_tokenize
import langcodes


# 1) CONFIG
class AppConfig:
    # Cấu hình trang
    PAGE_TITLE = "🦧 Đười ươi yêu tiếng người"
    PAGE_ICON = "🦧"
    LAYOUT = "centered"

    # Tiêu đề giao diện
    APP_TITLE = "🦍 Sửa lỗi chính tả & Dịch văn bản"
    APP_SUBTITLE = "🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵🐵"

    # Nội dung sidebar
    SIDEBAR_TITLE = "Hướng dẫn sử dụng"
    SIDEBAR_GUIDE = """
**Quy trình:**
1. **Nhập văn bản**
2. **Nhấn "Check"** để tìm lỗi chính tả
3. **Chọn "Có"** nếu muốn dịch
4. **Chọn ngôn ngữ đích** từ dropdown
5. **Nhấn "Dịch ngay"** để xem kết quả

**Lưu ý:**
- Cần kết nối Internet để dịch
- Nhấn **"Refresh"** để nhập văn bản mới
- ⚠️ **Tôi không chịu trách nhiệm cho sản phẩm của mình**
"""
    SIDEBAR_VERSION = "Phiên bản 11.0 - Mệt như chó"

    # Text UI
    INPUT_LABEL = "Nhập tiếng người - không nhập ngôn ngữ Toán 🙈:"
    INPUT_PLACEHOLDER = "Nhập tiếng Anh thì đỡ sai hơn..."
    CHECK_BUTTON = "🔍 Check!"
    TRANSLATE_BUTTON = "🌐 Dịch ngay"
    REFRESH_BUTTON = "🔄 Refresh"

    # Các key dùng cho session_state
    KEY_INPUT = "input_area"
    KEY_CORRECTED = "corrected_text"
    KEY_TRANSLATED = "translated_text"
    KEY_SHOW_TRANSLATE = "show_translate_section"
    KEY_TARGET_LANG = "target_lang"
    KEY_DETECTED_LANG = "detected_lang"
    KEY_CHECK_PERFORMED = "check_performed"
    KEY_MANUAL_EDIT = "manual_edit"
    KEY_CHANGES = "spell_changes"

    # Giá trị mặc định
    DEFAULT_TARGET_LANG = "vi"
    MIN_INPUT_LENGTH = 3

    # Danh sách ngôn ngữ hỗ trợ dịch
    LANGUAGES = {
        "vi": "Tiếng Việt",
        "en": "Tiếng Anh",
        "zh-CN": "Tiếng Trung",
        "ja": "Tiếng Nhật",
        "ko": "Tiếng Hàn",
        "fr": "Tiếng Pháp",
        "de": "Tiếng Đức",
        "es": "Tiếng Tây Ban Nha",
        "ru": "Tiếng Nga",
        "th": "Tiếng Thái",
    }

    # Danh sách ngôn ngữ hỗ trợ pyspellchecker
    SPELL_LANGS = {"en", "es", "fr", "pt", "de", "ru", "ar", "eu", "lv", "nl"}

    # Session state mặc định
    SESSION_DEFAULTS = {
        KEY_INPUT: "",
        KEY_CORRECTED: "",
        KEY_TRANSLATED: "",
        KEY_SHOW_TRANSLATE: False,
        KEY_TARGET_LANG: DEFAULT_TARGET_LANG,
        KEY_DETECTED_LANG: None,
        KEY_CHECK_PERFORMED: False,
        KEY_MANUAL_EDIT: "",
        KEY_CHANGES: [],
    }


# Cố định seed để kết quả detect ngôn ngữ ổn định hơn giữa các lần chạy
DetectorFactory.seed = 0

# 2) CÁC HÀM-s TIỆN ÍCH:

def init_page():
    
    st.set_page_config(
        page_title=AppConfig.PAGE_TITLE,
        page_icon=AppConfig.PAGE_ICON,
        layout=AppConfig.LAYOUT,
    )


def init_session_state():
    """Khởi tạo session_state với các giá trị mặc định."""
    for key, default_value in AppConfig.SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def reset_session_state():
    """Reset toàn bộ session_state về giá trị mặc định."""
    for key, default_value in AppConfig.SESSION_DEFAULTS.items():
        st.session_state[key] = default_value


def get_language_name(lang_code: str) -> str:
    """
    Trả về tên ngôn ngữ hiển thị bằng tiếng Việt.
    """
    try:
        return langcodes.get(lang_code).display_name("vi")
    except Exception:
        return lang_code


def preserve_case(original_token: str, corrected_token: str) -> str:
    """
    Giữ kiểu viết hoa của token gốc cho token đã sửa.
    Ví dụ:
    - HELLO -> WORLD
    - Hello -> World
    - hello -> world
    """
    if original_token.isupper():
        return corrected_token.upper()
    if original_token.istitle():
        return corrected_token.title()
    return corrected_token


# 3) CÁC HÀM cache_data

# Phát hiện ngôn ngữ của văn bản, mặc định là English
@st.cache_data(show_spinner=False)
def detect_source_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"

# Sửa lỗi chính tả 
@st.cache_data(show_spinner=False)
def fix_typos(text: str, lang_code: str):
    """
    - corrected_text: văn bản sau khi sửa
    - has_changes: có thay đổi hay không
    - changes: list các tuple (từ_gốc, từ_sửa)
    """
    spell_checker = SpellChecker(language=lang_code)
    tokens = wordpunct_tokenize(text)

    fixed_tokens = []
    changes = []

    for token in tokens:
        # Chỉ thử sửa token là chữ và có độ dài > 1
        if token.isalpha() and len(token) > 1:
            suggestion = spell_checker.correction(token.lower())

            # Nếu không có gợi ý thì giữ nguyên token cũ
            if suggestion is None:
                corrected = token
            else:
                corrected = preserve_case(token, suggestion)

            fixed_tokens.append(corrected)

            if corrected != token:
                changes.append((token, corrected))
        else:
            # Số, dấu câu, ký hiệu... thì giữ nguyên
            fixed_tokens.append(token)

    corrected_text = TreebankWordDetokenizer().detokenize(fixed_tokens)
    has_changes = len(changes) > 0
    return corrected_text, has_changes, changes

#  không cần gọi lại translator nếu cùng một đoạn text được dịch sang cùng một ngôn ngữ 
@st.cache_data(show_spinner=False, ttl=3600)
def translate_text(text: str, target_lang: str) -> str:
    """
    ttl=3600 = 1 giờ.
    """
    translator = GoogleTranslator(source="auto", target=target_lang)
    return translator.translate(text)

 
# 4) CÁC HÀM RENDER GIAO DIỆN: title, sidebar, input

def render_header():
    st.title(AppConfig.APP_TITLE)
    st.markdown(AppConfig.APP_SUBTITLE)


def render_sidebar():
    with st.sidebar:
        st.header(AppConfig.SIDEBAR_TITLE)
        st.markdown(AppConfig.SIDEBAR_GUIDE)
        st.markdown("---")
        st.caption(AppConfig.SIDEBAR_VERSION)


def render_input_area():
    """
    Giá trị được lưu trực tiếp vào st.session_state[KEY_INPUT].
    """
    st.text_area(
        AppConfig.INPUT_LABEL,
        placeholder=AppConfig.INPUT_PLACEHOLDER,
        height=150,
        key=AppConfig.KEY_INPUT,
    )


# 5) CHECK VĂN BẢN
def process_check():
    """
    1. Lấy input
    2. Validate độ dài
    3. Detect ngôn ngữ
    4. Spellcheck nếu ngôn ngữ được hỗ trợ
    5. Lưu kết quả vào session_state
    """
    input_text = st.session_state[AppConfig.KEY_INPUT]
    st.session_state[AppConfig.KEY_CHECK_PERFORMED] = True

    # Mỗi lần check mới thì xóa kết quả dịch cũ
    st.session_state[AppConfig.KEY_TRANSLATED] = ""

    # Nếu input rỗng / quá ngắn thì dừng
    if not input_text or len(input_text.strip()) < AppConfig.MIN_INPUT_LENGTH:
        st.warning(f"⚠️ Tối thiểu {AppConfig.MIN_INPUT_LENGTH} ký tự!")
        st.session_state[AppConfig.KEY_SHOW_TRANSLATE] = False
        st.session_state[AppConfig.KEY_CORRECTED] = ""
        st.session_state[AppConfig.KEY_MANUAL_EDIT] = ""
        st.session_state[AppConfig.KEY_CHANGES] = []
        return

    # Xác định ngôn ngữ
    src_lang = detect_source_language(input_text)
    st.session_state[AppConfig.KEY_DETECTED_LANG] = src_lang
    st.info(f"🔍 Ngôn ngữ phát hiện: **{get_language_name(src_lang)}**")

    corrected_text = input_text
    changes = []

    # Spellcheck nếu ngôn ngữ được hỗ trợ
    if src_lang in AppConfig.SPELL_LANGS:
        try:
            corrected_text, has_changes, changes = fix_typos(input_text, src_lang)

            if not has_changes:
                st.success("✅ Không tìm thấy lỗi chính tả nào!")
            else:
                st.warning("⚠️ Phát hiện lỗi chính tả! Đã tự động sửa:")

        except Exception as e:
            # Nếu spellchecker có lỗi, giữ nguyên text gốc
            st.warning("⚠️ Không thể chạy spellcheck cho ngôn ngữ này.")
            st.caption(f"Chi tiết lỗi: {e}")
            corrected_text = input_text
            changes = []
    else:
        st.warning(
            f"⚠️ Chưa hỗ trợ ngôn ngữ **{get_language_name(src_lang)}**"
        )
        st.info("💡 Vẫn có thể dịch văn bản sang ngôn ngữ khác!")
        corrected_text = input_text
        changes = []

    # Lưu kết quả vào session_state
    st.session_state[AppConfig.KEY_CORRECTED] = corrected_text
    st.session_state[AppConfig.KEY_MANUAL_EDIT] = corrected_text
    st.session_state[AppConfig.KEY_CHANGES] = changes
    st.session_state[AppConfig.KEY_SHOW_TRANSLATE] = True


def render_check_button():
    """Hiển thị nút Check và gọi process_check khi được nhấn."""
    if st.button(AppConfig.CHECK_BUTTON, type="primary", use_container_width=True):
        process_check()



# 6) HIỂN THỊ KẾT QUẢ SPELLCHECK

def render_spellcheck_result():
    """
    Hiển thị:
    - danh sách từ bị sửa
    - văn bản sau khi sửa
    - ô để người dùng chỉnh sửa thủ công nếu muốn
    """
    if not st.session_state[AppConfig.KEY_CHECK_PERFORMED]:
        return

    corrected_text = st.session_state[AppConfig.KEY_CORRECTED]
    changes = st.session_state[AppConfig.KEY_CHANGES]

    # Nếu không có corrected_text thì thường là do input không hợp lệ
    if not corrected_text:
        return

    if changes:
        st.markdown("**📝 So sánh thay đổi:**")
        for original, fixed in changes:
            st.write(f"• `{original}` → **{fixed}**")

        st.text_area(
            "Văn bản đã sửa tự động:",
            value=corrected_text,
            height=100,
            disabled=True,
        )

        st.text_area(
            "Hoặc bạn tự sửa theo ý mình:",
            height=100,
            key=AppConfig.KEY_MANUAL_EDIT,
        )

        # Luôn đồng bộ corrected_text với bản sửa tay mới nhất
        st.session_state[AppConfig.KEY_CORRECTED] = st.session_state[AppConfig.KEY_MANUAL_EDIT]

    else:   # không thì lấy bản tự động
        st.text_area(
            "📄 Văn bản hiện tại:",
            value=corrected_text,
            height=100,
            disabled=True,
        )


# 7) DỊCH VĂN BẢN
def render_translate_section():
    """
    - hỏi có muốn dịch không
    - chọn ngôn ngữ đích
    - bấm nút Dịch
    """
    if not st.session_state[AppConfig.KEY_SHOW_TRANSLATE]:
        return

    if not st.session_state[AppConfig.KEY_CORRECTED]:
        return

    should_translate = st.radio(
        "🌐 Bạn có muốn dịch đoạn văn bản này không?",
        options=["❌ Không", "✅ Có"],
        index=0,
        horizontal=True,
    )

    if should_translate != "✅ Có":
        return

    language_codes = list(AppConfig.LANGUAGES.keys())

    # Tính index mặc định cho selectbox
    current_target = st.session_state[AppConfig.KEY_TARGET_LANG]
    if current_target in language_codes:
        default_index = language_codes.index(current_target)
    else:
        default_index = 0

    target_lang = st.selectbox(
        "Chọn ngôn ngữ đích:",
        options=language_codes,
        format_func=lambda code: AppConfig.LANGUAGES[code],
        index=default_index,
    )

    st.session_state[AppConfig.KEY_TARGET_LANG] = target_lang

    # Cảnh báo nếu ngôn ngữ đích trùng ngôn ngữ nguồn
    src_lang = st.session_state[AppConfig.KEY_DETECTED_LANG]
    if src_lang == target_lang:
        st.warning("⚠️ Ngôn ngữ đích đang trùng với ngôn ngữ gốc.")

    if st.button(AppConfig.TRANSLATE_BUTTON, type="primary", use_container_width=True):
        try:
            text_to_translate = st.session_state[AppConfig.KEY_CORRECTED]

            with st.spinner(f"🔄 Đang dịch sang {AppConfig.LANGUAGES[target_lang]}..."):
                translated = translate_text(text_to_translate, target_lang)
                st.session_state[AppConfig.KEY_TRANSLATED] = translated

        except Exception as e:
            st.error(f"❌ Lỗi khi dịch: {str(e)}")
            st.info("🔌 Kiểm tra kết nối internet hoặc thử lại sau.")


def render_translation_result():
    """
    Hiển thị kết quả dịch nếu đã có trong session_state.
    Tách riêng để sau mỗi lần rerun, bản dịch vẫn còn hiện.
    """
    translated_text = st.session_state[AppConfig.KEY_TRANSLATED]
    if not translated_text:
        return

    target_lang = st.session_state[AppConfig.KEY_TARGET_LANG]
    st.markdown("---")
    st.markdown(f"### 📝 Bản dịch sang {AppConfig.LANGUAGES[target_lang]}:")
    st.success(translated_text)


# 8) REFRESH
def render_refresh_button():
    """
    - xóa input
    - xóa kết quả sửa
    - xóa kết quả dịch
    - reset state
    """
    st.markdown("---")
    if st.button(AppConfig.REFRESH_BUTTON, type="secondary", use_container_width=True):
        reset_session_state()
        st.rerun()
# Luồng UI
def main():
    init_page()
    init_session_state()

    render_header()
    render_sidebar()
    render_input_area()
    render_check_button()
    render_spellcheck_result()
    render_translate_section()
    render_translation_result()
    render_refresh_button()


if __name__ == "__main__":
    main()

