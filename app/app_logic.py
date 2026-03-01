import gradio as gr
import re

# =========================
# IMPORT TỪ CÁC FILE LOGIC CỦA BẠN
# =========================
import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # → DATA-MINING/app
FOLDER_C = os.path.abspath(os.path.join(BASE_DIR, "../rag"))   # → DATA-MINING/rag

sys.path.insert(0, FOLDER_C)
from search import load_retriever, search, lookup, is_direct_name, is_lookup # pyright: ignore[reportMissingImports]
from llm import ask_llm, format_search_context, format_lookup_context # type: ignore

print("Đang khởi động giao diện, kết nối Database và LLM...")
embed_model, vector_db = load_retriever()

# =========================
# BƯỚC 1: RENDER KẾT QUẢ RA HTML
# =========================
def render_html_results(results):
    if not results:
        return "" 

    html_output = '<div class="result-grid">'
    
    for r in results:
        price_fmt = "{:,.0f}".format(r.get('price', 0)).replace(",", ".")
        name = r.get('name', 'Unknown')
        cpu = r.get('cpu', 'Đang cập nhật')
        gpu = r.get('gpu', 'Đang cập nhật')
        ram = f"{r.get('ram', '')}GB"
        storage = f"{r.get('storage', '')}GB"
        sim_score = r.get('similarity', 0)
        desc = str(r.get('mo_ta', 'Chưa có mô tả')).replace('\n', '<br>')

        screen_size = r.get('screen_size', 'Đang cập nhật')
        screen_resolution = r.get('screen_resolution', 'Đang cập nhật')
        screen_panel = r.get('screen_panel', 'Đang cập nhật')
        battery_wh = r.get('battery_wh', 'Đang cập nhật')
        color = r.get('color', 'Đang cập nhật')
        rating = r.get('rating', 'Chưa có')

        # XỬ LÝ ĐÁNH GIÁ
        review_text_raw = str(r.get('review_text', ''))
        reviews_html = ""
        if review_text_raw.lower() in ['nan', 'none', 'null', ''] or not review_text_raw:
            reviews_html = "<div class='review-item' style='border-left-color: #565869; font-style: italic; color: #888;'>Chưa có đánh giá chi tiết từ người dùng.</div>"
        else:
            reviews = [rev.strip() for rev in review_text_raw.split('||') if rev.strip()]
            for rev in reviews:
                reviews_html += f"<div class='review-item'><i class='fas fa-user-circle'></i> {rev}</div>"

        card_html = f"""
        <div class="card-wrapper">
            <div class="laptop-card">
                <div class="card-header">
                    <div class="laptop-name">{name}</div>
                    <div class="laptop-price">{price_fmt} ₫</div>
                </div>
                <div class="badges">
                    <span class="badge badge-cpu"><i class="fas fa-microchip"></i> {cpu}</span>
                    <span class="badge badge-gpu"><i class="fas fa-gamepad"></i> {gpu}</span>
                    <span class="badge badge-similarity">⭐ {sim_score}</span>
                </div>
                <div class="specs-row">
                    <div class="spec-item"><i class="fas fa-memory"></i> <span>{ram}</span></div>
                    <div class="spec-item"><i class="fas fa-hdd"></i> <span>{storage}</span></div>
                </div>
                
                <div class="card-detail" style="display: none;">
                    <div class="detail-section">
                        <div class="detail-title">⚙️ Cấu hình chi tiết</div>
                        <ul class="specs-list">
                            <li><b>CPU:</b> <span>{cpu}</span></li>
                            <li><b>RAM:</b> <span>{ram}</span></li>
                            <li><b>GPU:</b> <span>{gpu}</span></li>
                            <li><b>Ổ cứng:</b> <span>{storage}</span></li>
                            <li><b>Màn hình:</b> <span>{screen_size} inch, {screen_resolution}, {screen_panel}</span></li>
                            <li><b>Pin:</b> <span>{battery_wh}</span></li>
                            <li><b>Màu sắc:</b> <span>{color}</span></li>
                        </ul>
                    </div>
                    <div class="detail-section">
                        <div class="detail-title">⭐ Đánh giá ({rating} Sao)</div>
                        <div class="reviews-container">
                            {reviews_html}
                        </div>
                    </div>
                    </div>
                <button class="view-detail-btn" onclick="toggleDetail(this)">Xem chi tiết</button>
            </div>
        </div>
        """
        html_output += card_html
        
    html_output += '</div>'
    return html_output

# =========================
# BƯỚC 2: BỘ XỬ LÝ TRÍ NHỚ TỪ KHÓA
# =========================
def smart_combine(memory, new_query):
    if not memory: return new_query
    mem = memory
    new_lower = new_query.lower()
    
    if re.search(r'\d+\s*(tr|triệu|m)', new_lower):
        mem = re.sub(r"(?:dưới|tầm|khoảng|trên|từ|max|min|tối đa|ít nhất)?\s*\d+(?:[.,]\d+)?\s*(?:tr|triệu|m)(?:\s*(?:-|đến|tới)\s*\d+(?:[.,]\d+)?\s*(?:tr|triệu|m))?", "", mem, flags=re.IGNORECASE)
    if re.search(r'(ram\s*\d+|\d+\s*gb)', new_lower):
        mem = re.sub(r"(?:ram\s*\d+|\d+\s*gb\s*ram|\d+\s*gb)", "", mem, flags=re.IGNORECASE)
    if re.search(r'(ssd|tb)', new_lower):
        mem = re.sub(r"(?:\d+\s*tb\s*ssd|ssd\s*\d+\s*tb|ssd|\d+\s*tb)", "", mem, flags=re.IGNORECASE)
    if re.search(r'(i\d|ryzen\s*\d)', new_lower):
        mem = re.sub(r"(core\s+)?(i3|i5|i7|i9)|(ryzen\s*\d)", "", mem, flags=re.IGNORECASE)
        
    categories = r"(gaming|game|chơi game|văn phòng|office|đồ họa|thiết kế|render|mỏng nhẹ|sinh viên|code|lập trình)"
    if re.search(categories, new_lower):
        mem = re.sub(categories, "", mem, flags=re.IGNORECASE)
        
    brands = r"(apple|macbook|mac|dell|hp|asus|lenovo|acer|msi|samsung|gigabyte|thinkpad|legion|rog|tuf|vivobook|ideapad)"
    if re.search(brands, new_lower):
        mem = re.sub(brands, "", mem, flags=re.IGNORECASE)
        
    if "laptop" in new_lower:
        mem = re.sub(r"laptop", "", mem, flags=re.IGNORECASE)

    mem = re.sub(r'\s+', ' ', mem).strip()
    return re.sub(r'\s+', ' ', f"{mem} {new_query}".strip())

# =========================
# BƯỚC 3: HÀM CHAT TỔNG (ĐÃ TÍCH HỢP SO SÁNH)
# =========================
def chat_logic(new_query, memory, chat_history, ui_history):
    if not new_query.strip():
        return gr.skip()
    
    def do_search(query):
        query_lower = query.lower()
        
        # --- TÍNH NĂNG MỚI: XỬ LÝ LỆNH SO SÁNH ---
        if "so sánh" in query_lower:
            # Dùng Regex để tách lấy tên 2 máy (VD: so sánh máy A và máy B / với máy B / - máy B)
            match = re.search(r"so sánh\s+(.*?)\s+(?:và|với|-)\s+(.*)", query_lower)
            if match:
                laptop1_name = match.group(1).strip()
                laptop2_name = match.group(2).strip()
                
                # Gọi search riêng rẽ cho từng máy (lấy top 1 máy chuẩn nhất cho mỗi tên)
                res1, _ = search(laptop1_name, embed_model, vector_db, top_k=1)
                res2, _ = search(laptop2_name, embed_model, vector_db, top_k=1)
                
                combined_results = []
                if res1: combined_results.extend(res1)
                if res2: combined_results.extend(res2)
                
                # Nếu tìm thấy ít nhất 1 trong 2 máy, bung UI hiển thị
                if combined_results:
                    return True, render_html_results(combined_results), format_search_context(combined_results)
            
            # Fallback: Nếu gõ chữ "so sánh" nhưng không đúng form "A và B"
            res_list, _ = search(query, embed_model, vector_db, top_k=2)
            if res_list:
                return True, render_html_results(res_list), format_search_context(res_list)

        # --- TÌM ĐÍCH DANH 1 MÁY ---
        elif is_direct_name(query) or is_lookup(query):
            res = lookup(query, embed_model, vector_db)
            if res:
                return True, render_html_results([res]), format_lookup_context(res)
                
        # --- TÌM KIẾM NHU CẦU BÌNH THƯỜNG ---
        else:
            res_list, _ = search(query, embed_model, vector_db, top_k=6)
            if res_list:
                return True, render_html_results(res_list), format_search_context(res_list)
                
        return False, "", "Không tìm thấy laptop phù hợp."

    combined_query = smart_combine(memory, new_query)
    has_results, html_res, llm_context = do_search(combined_query)
    new_memory = combined_query
    
    # Nếu kết hợp memory không ra, thử lại với query mới nguyên
    if not has_results and memory:
        has_results, html_res, llm_context = do_search(new_query)
        if has_results:
            new_memory = new_query
        else:
            new_memory = memory
    
    bot_response = ask_llm(new_query, llm_context, chat_history)

    chat_history.append({"user": new_query, "assistant": bot_response})
    
    # ======= ĐÃ FIX LỖI GRADIO 6.0: TRẢ VỀ DẠNG ROLE / CONTENT =======
    ui_history.append({"role": "user", "content": new_query})
    ui_history.append({"role": "assistant", "content": bot_response})

    # ĐIỀU KHIỂN GIAO DIỆN BẰNG PYTHON
    if has_results:
        res_col_update = gr.update(visible=True)
        chat_col_update = gr.update(elem_classes=["chat-col", "side"])
    else:
        res_col_update = gr.update(visible=False)
        chat_col_update = gr.update(elem_classes=["chat-col", "center"])

    hero_update = gr.update(visible=False)
    chatbot_update = gr.update(visible=True)
    clear_btn_update = gr.update(visible=True)

    return html_res, new_memory, chat_history, ui_history, "", res_col_update, chat_col_update, hero_update, chatbot_update, clear_btn_update

# =========================
# HÀM RESET
# =========================
def reset_all():
    return "", "", [], [], "", gr.update(visible=False), gr.update(elem_classes=["chat-col", "center"]), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)