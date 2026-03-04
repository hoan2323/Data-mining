import streamlit as st
import markdown as md
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER_C = os.path.abspath(os.path.join(BASE_DIR, "../rag"))
sys.path.insert(0, FOLDER_C)
from rag.search import load_retriever, search, lookup, is_direct_name, is_lookup  # pyright: ignore[reportMissingImports]
from rag.llm import ask_llm, format_search_context, format_lookup_context, extract_indices # pyright: ignore[reportMissingImports]


st.set_page_config(
    page_title="Tư vấn Laptop AI",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #0d0d1a !important;
    color: #ffffff !important;
}
.stApp { background-color: #0d0d1a !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 1rem 1.5rem !important;
    max-width: 100% !important;
}

/* ── Xóa border mặc định Streamlit input ── */
.stTextInput > div,
.stTextInput > div > div {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    padding: 0 !important;
}
.stTextInput > div > div > input {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    color: #fff !important;
    padding: 10px 16px !important;
    font-size: 15px !important;
    box-shadow: none !important;
    outline: none !important;
    height: 44px !important;
}
.stTextInput > div > div > input::placeholder {
    color: #555 !important;
}

/* ── Xóa border form container ── */
[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}

/* ── Bo tròn toàn bộ row input + button ── */
[data-testid="stForm"] [data-testid="stHorizontalBlock"] {
    background: #1a1a2e !important;
    border: 1px solid #2e2e4e !important;
    border-radius: 999px !important;
    padding: 3px 6px 3px 6px !important;
    align-items: center !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
}
[data-testid="stForm"]:focus-within [data-testid="stHorizontalBlock"] {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.18) !important;
}

/* ── Nút gửi tròn ── */
.stFormSubmitButton > button {
    background: #7c3aed !important;
    border: none !important;
    color: #fff !important;
    border-radius: 50% !important;
    width: 38px !important;
    height: 38px !important;
    min-width: 38px !important;
    font-size: 16px !important;
    padding: 0 !important;
    line-height: 1 !important;
    transition: background 0.2s, transform 0.1s !important;
    cursor: pointer !important;
}
.stFormSubmitButton > button:hover {
    background: #6d28d9 !important;
    transform: scale(1.08) !important;
}
.stFormSubmitButton > button:active {
    transform: scale(0.95) !important;
}


/* ── Chat bubbles ── */
.user-bubble {
    background: #1e1e3f;
    border-radius: 18px 18px 4px 18px;
    padding: 10px 16px;
    margin: 6px 0 6px auto;
    max-width: 80%;
    width: fit-content;
    color: #fff;
    font-size: 14px;
    line-height: 1.6;
    margin-left: auto;
}
.bot-wrap {
    background: #16213e;
    border: 1px solid #2e2e4e;
    border-radius: 0px 18px 18px 18px;
    padding: 12px 16px;
    margin: 4px 0 12px 0;
    max-width: 92%;
}
.bot-wrap p {
    margin: 4px 0 !important;
    line-height: 1.7 !important;
    font-size: 14px !important;
    color: #e0e0e0 !important;
}
.bot-wrap ul, .bot-wrap ol {
    margin: 4px 0 6px 18px !important;
    padding: 0 !important;
}
.bot-wrap li {
    margin: 3px 0 !important;
    line-height: 1.6 !important;
    font-size: 14px !important;
    color: #e0e0e0 !important;
}
.bot-wrap strong { color: #fff !important; }
.bot-wrap table {
    width: 100%; border-collapse: collapse;
    margin: 8px 0 !important; font-size: 13px;
}
.bot-wrap th {
    background: #252545 !important; color: #fff !important;
    padding: 8px !important; border: 1px solid #3a3a6e !important;
    text-align: left !important;
}
.bot-wrap td {
    padding: 7px 8px !important;
    border: 1px solid #2a2a4a !important;
    color: #ccc !important;
}

.chat-label {
    font-size: 11px;
    color: #555;
    margin: 8px 0 2px;
    padding: 0 4px;
}

/* ── Product cards ── */
.laptop-card {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
    display: flex;
    flex-direction: column;
    min-height: 260px;
}
.laptop-card:hover { border-color: #7c3aed; }
.card-name {
    font-weight: 700; font-size: 13px;
    color: #fff; margin-bottom: 8px; line-height: 1.5;
    min-height: 40px;
}
.card-price {
    color: #00e676; font-size: 19px;
    font-weight: 700; margin-bottom: 10px;
}
.card-badges {
    min-height: 80px;
    display: flex;
    flex-wrap: wrap;
    align-content: flex-start;
    gap: 4px;
    margin-bottom: 6px;
}
.badge {
    background: #252545; color: #aaa;
    border-radius: 20px; padding: 3px 9px;
    font-size: 11px;
    white-space: nowrap;
}
.card-footer {
    display: flex; justify-content: space-between;
    color: #666; font-size: 12px;
    margin-top: auto;
    padding-top: 8px;
}
.divider { border: none; border-top: 1px solid #2a2a4a; margin: 8px 0; }
.section-header {
    font-size: 12px; font-weight: 600; color: #666;
    letter-spacing: 1px; text-transform: uppercase;
    padding-bottom: 8px; border-bottom: 1px solid #2a2a4a;
    margin-bottom: 14px;
}
            /* Thêm vào phần <style> */

/* Căn nút sát phải bên trong pill */
[data-testid="stForm"] [data-testid="stHorizontalBlock"] > div:last-child {
    display: flex !important;
    justify-content: flex-end !important;
    align-items: center !important;
    padding-right: 4px !important;
    flex: 0 0 auto !important;
    min-width: fit-content !important;
}

/* Bỏ padding thừa bên phải cột input */
[data-testid="stForm"] [data-testid="stHorizontalBlock"] > div:first-child {
    padding-right: 0 !important;
}
/* Nút reset dạng text link */
.reset-btn > button {
    background: transparent !important;
    border: none !important;
    color: #444 !important;
    font-size: 12px !important;
    padding: 4px 0 !important;
    width: 100% !important;
    cursor: pointer !important;
    text-decoration: underline !important;
    text-underline-offset: 3px !important;
    transition: color 0.2s !important;
    box-shadow: none !important;
}
.reset-btn > button:hover {
    color: #7c3aed !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Reset button kiểu text link */
/* Reset button thành text mờ */
div[data-testid="stButton"] > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;

    color: #444 !important;
    font-size: 12px !important;
    padding: 4px 0 !important;
}

/* Hover mới sáng lên nhẹ */
div[data-testid="stButton"] > button:hover {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;

    color: #7c3aed !important;
    text-decoration: underline !important;
}

/* XÓA luôn focus ring xanh của Streamlit */
div[data-testid="stButton"] > button:focus {
    outline: none !important;
    box-shadow: none !important;
}

</style>
""", unsafe_allow_html=True)


# ── Load retriever ──────────────────────────────────────────────
@st.cache_resource
def init_retriever():
    return load_retriever()


model, collection = init_retriever()


# ── Session state ───────────────────────────────────────────────
for key, default in {
    "started": False,
    "history": [],
    "session_products": {},
    "current_products": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Refinement detection ────────────────────────────────────────
REFINEMENT_KEYWORDS = [
    "trong đó", "trong các máy", "trong 10", "trong danh sách",
    "trên đây", "vừa tìm", "pin trâu nhất", "rẻ nhất",
    "mạnh nhất", "nhẹ nhất", "tốt nhất", "phù hợp nhất",
    "cái nào", "máy nào trong",
]

def is_refinement(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in REFINEMENT_KEYWORDS) and bool(st.session_state.session_products)


# ── Core logic ──────────────────────────────────────────────────
def process_query(query: str):
    indices = extract_indices(query)

    if indices and st.session_state.session_products:
        valid_pairs = [
            (i, st.session_state.session_products[i])
            for i in indices if i in st.session_state.session_products
        ]
        if not valid_pairs:
            context = "Không tìm thấy máy theo số thứ tự đó."
            st.session_state.current_products = []
        elif len(valid_pairs) == 1:
            idx, r = valid_pairs[0]
            context = f"Máy {idx}:\n" + format_lookup_context(r)
            st.session_state.current_products = [r]
        else:
            context = format_search_context(
                [r for _, r in valid_pairs], indexed_results=valid_pairs
            )
            st.session_state.current_products = [r for _, r in valid_pairs]

    elif is_refinement(query):
        sp = st.session_state.session_products
        products = list(sp.items())
        context = format_search_context(
            [r for _, r in products], indexed_results=products
        )
        st.session_state.current_products = [r for _, r in products]

    elif is_direct_name(query) or is_lookup(query):
        result = lookup(query, model, collection)
        context = format_lookup_context(result)
        st.session_state.current_products = [result] if result else []

    else:
        results, _ = search(query, model, collection, top_k=10)
        st.session_state.session_products = {i + 1: r for i, r in enumerate(results)}
        context = format_search_context(
            results, indexed_results=[(i + 1, r) for i, r in enumerate(results)]
        )
        st.session_state.current_products = results

    llm_history = [
        {"user": u, "assistant": a, "context": c}
        for u, a, c in st.session_state.history
    ]
    answer = ask_llm(query, context, llm_history)
    st.session_state.history.append((query, answer, context))
    st.session_state.started = True


# ── Render card ─────────────────────────────────────────────────
def render_card(r: dict, index: int = None) -> str:
    price_fmt = f"{r['price']:,.0f}".replace(",", ".") + " ₫"
    sim = r.get("similarity", r.get("final_score", 0))
    rating = r.get("rating", 0)
    stars = "★" * int(round(rating)) + "☆" * (5 - int(round(rating)))
    idx_badge = (
        f"<span style='background:#7c3aed;color:#fff;border-radius:6px;"
        f"padding:2px 8px;font-size:11px;margin-bottom:8px;display:inline-block'>#{index}</span><br>"
        if index else ""
    )

    # Review text — cắt ngắn 120 ký tự
    review = r.get("review_text", "")
    review_html = (
        f"<div style='color:#888;font-size:11px;font-style:italic;"
        f"margin-top:6px;line-height:1.5;border-top:1px solid #2a2a4a;padding-top:6px'>"
        f"💬 {review[:120]}{'...' if len(review) > 120 else ''}</div>"
        if review and review != "Chưa có phản hồi" else ""
    )

    return f"""
    <div class="laptop-card">
        {idx_badge}
        <div class="card-name">{r['name']}</div>
        <div class="card-price">{price_fmt}</div>
        <div class="card-badges">
            <span class="badge">🖥 {r['cpu']}</span>
            <span class="badge">🎮 {r['gpu']}</span>
            <span class="badge">💾 {int(r['ram'])}GB RAM</span>
            <span class="badge">💿 {int(r['storage'])}GB SSD</span>
            <span class="badge">📐 {r['screen_size']}" {r.get('screen_resolution','')}</span>
        </div>
        <hr class="divider">
        <div style="color:#f1c40f;font-size:13px;margin-bottom:4px">
            {stars} <span style="color:#555;font-size:11px">score: {sim:.3f}</span>
        </div>
        <div class="card-footer">
            <span>🔋 {r.get('battery_wh','N/A')} Wh</span>
            <span>🎨 {r.get('color','N/A')}</span>
        </div>
        {review_html}
    </div>
    """



# ── Render bot message ──────────────────────────────────────────
def render_bot(text: str) -> str:
    html_body = md.markdown(text, extensions=["tables", "nl2br"])
    return f"<div class='bot-wrap'>{html_body}</div>"


# ── Input form helper ───────────────────────────────────────────
def render_input_form(form_key: str, placeholder: str = "Ask about laptops..."):
    with st.form(form_key, clear_on_submit=True):
        col_inp, col_btn = st.columns([17, 1])
        with col_inp:
            value = st.text_input(
                "", placeholder=placeholder,
                label_visibility="collapsed"
            )
        with col_btn:
            submitted = st.form_submit_button("➤")
    return value, submitted


# ══════════════════════════════════════════════════════════════════
# WELCOME SCREEN
# ══════════════════════════════════════════════════════════════════
if not st.session_state.started:
    st.markdown("<div style='height:28vh'></div>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown(
            "<h1 style='text-align:center;color:#fff;font-size:2.5em;"
            "font-weight:700;margin-bottom:32px;font-family:Inter,sans-serif'>"
            "How can I help?</h1>",
            unsafe_allow_html=True,
        )
        welcome_input, submitted = render_input_form("welcome_form")

        if submitted and welcome_input.strip():
            with st.spinner("Đang tìm kiếm..."):
                process_query(welcome_input.strip())
            st.rerun()


# ══════════════════════════════════════════════════════════════════
# MAIN LAYOUT
# ══════════════════════════════════════════════════════════════════
else:
    col_products, col_chat = st.columns([5, 4], gap="medium")

    # ── Cột trái: Product cards ─────────────────────────────────
    with col_products:
        st.markdown('<div class="section-header">💻 Sản phẩm tìm được</div>', unsafe_allow_html=True)
        product_container = st.container(height=750)
        with product_container:
            products = st.session_state.current_products
            sp = st.session_state.session_products
            if products:
                for i in range(0, len(products), 2):
                    c1, c2 = st.columns(2)
                    with c1:
                        idx = next((k for k, v in sp.items() if v == products[i]), None)
                        st.markdown(render_card(products[i], idx), unsafe_allow_html=True)
                    if i + 1 < len(products):
                        with c2:
                            idx2 = next((k for k, v in sp.items() if v == products[i + 1]), None)
                            st.markdown(render_card(products[i + 1], idx2), unsafe_allow_html=True)
            else:
                st.markdown(
                    "<div style='color:#444;text-align:center;margin-top:60px;font-size:14px'>"
                    "🔍 Kết quả sản phẩm sẽ hiển thị ở đây</div>",
                    unsafe_allow_html=True,
                )

    # ── Cột phải: Chat ──────────────────────────────────────────
    with col_chat:
        st.markdown('<div class="section-header">🤖 Trợ lý AI</div>', unsafe_allow_html=True)

        chat_container = st.container(height=620)
        with chat_container:
            for user_msg, bot_msg, _ in st.session_state.history:
                st.markdown(
                    f"<div class='chat-label' style='text-align:right'>Bạn</div>"
                    f"<div class='user-bubble'>{user_msg}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("<div class='chat-label'>🤖 Trợ lý</div>", unsafe_allow_html=True)
                st.markdown(render_bot(bot_msg), unsafe_allow_html=True)

        chat_input, send = render_input_form("chat_form")

        if send and chat_input.strip():
            with st.spinner("Đang tìm kiếm..."):
                process_query(chat_input.strip())
            st.rerun()

        # Thay đoạn st.button cũ bằng:
        reset_container = st.container()

        with reset_container:
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("Bắt đầu cuộc hội thoại mới", key="reset_chat"):
                    for key in ["started", "history", "session_products", "current_products"]:
                        st.session_state[key] = False if key == "started" else (
                            [] if key in ["history", "current_products"] else {}
                        )
                    st.rerun()

