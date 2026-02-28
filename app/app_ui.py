import gradio as gr
from app import chat_logic, reset_chat

# =========================
# CSS & JS TỐI ƯU CỰC XỊN
# =========================
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
:root { --bg-dark: #0f172a; --card-bg: rgba(30, 41, 59, 0.5); --primary: #3b82f6; --primary-glow: rgba(59, 130, 246, 0.5); --accent: #10b981; --text-main: #f1f5f9; --text-sub: #94a3b8; --radius: 16px; }
body { background-color: #0b1121 !important; background-image: radial-gradient(circle at 10% 20%, rgba(56, 189, 248, 0.3) 0%, transparent 40%), radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.3) 0%, transparent 40%) !important; background-attachment: fixed !important; background-size: cover !important; font-family: 'Inter', sans-serif !important; color: var(--text-main) !important; margin: 0 !important; min-height: 100vh !important; }
gradio-app, .gradio-container, .main, .wrap { background: transparent !important; background-color: transparent !important; }
footer { display: none !important; }

/* BỐ CỤC CHÍNH ĐỂ TRƯỢT MƯỢT MÀ */
#main-container {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    width: 98% !important; /* DÀN TRẢI GẦN KÍN MÀN HÌNH */
    max-width: 1800px !important; /* TĂNG GIỚI HẠN SIÊU RỘNG */
    margin: 0 auto !important;
    gap: 30px;
    justify-content: center !important; 
    align-items: flex-start !important;
    transition: all 0.7s cubic-bezier(0.25, 1, 0.5, 1) !important;
}

/* --- TRẠNG THÁI: KHÔNG CÓ KẾT QUẢ (CHAT BÀNH TRƯỚNG Ở GIỮA) --- */
.results-col-hidden {
    width: 0% !important;
    min-width: 0 !important;
    max-width: 0 !important;
    flex: 0 0 0% !important;
    opacity: 0 !important;
    overflow: hidden !important;
    padding: 0 !important; margin: 0 !important; border: none !important;
    transition: all 0.7s cubic-bezier(0.25, 1, 0.5, 1) !important;
}
.chat-col-center {
    width: 100% !important;
    max-width: 1200px !important; /* FULL MÀN Ở GIỮA LÚC BAN ĐẦU */
    flex: 1 1 100% !important;
    transition: all 0.7s cubic-bezier(0.25, 1, 0.5, 1) !important;
}

/* --- TRẠNG THÁI: CÓ KẾT QUẢ LAPTOP (DẠT SANG 2 BÊN) --- */
.results-col-show {
    width: 55% !important; /* BÊN TRÁI: LAPTOP */
    min-width: 300px !important;
    max-width: 1100px !important;
    flex: 1.5 1 55% !important;
    opacity: 1 !important;
    overflow: visible !important;
    transition: all 0.7s cubic-bezier(0.25, 1, 0.5, 1) !important;
}
.chat-col-side {
    width: 45% !important; /* BÊN PHẢI: CHATBOT ĐƯỢC NỚI RỘNG RA */
    min-width: 450px !important;
    max-width: 750px !important; /* DÀNH NHIỀU KHÔNG GIAN HƠN CHO CHAT */
    flex: 1 1 45% !important;
    transition: all 0.7s cubic-bezier(0.25, 1, 0.5, 1) !important;
}

/* ----------------------------------------- */
/* TRANG TRÍ CHATBOT */
/* ----------------------------------------- */
.chat-panel { background: rgba(15, 23, 42, 0.7) !important; backdrop-filter: blur(25px) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 24px !important; padding: 24px !important; box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5) !important; display: flex; flex-direction: column; gap: 15px; }
.chat-title { text-align: center; margin: 0 0 10px 0 !important; font-size: 2.2rem !important; font-weight: 800 !important; background: linear-gradient(to right, #60a5fa, #a78bfa) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; }
.gradio-chatbot { background: transparent !important; border: none !important; }
.message.bot { background: rgba(59, 130, 246, 0.15) !important; border: 1px solid rgba(59, 130, 246, 0.2) !important; font-size: 1.05rem !important; }
.message.user { background: rgba(255,255,255,0.08) !important; border: 1px solid rgba(255,255,255,0.1) !important; font-size: 1.05rem !important;}

/* Ô NHẬP LIỆU & NÚT GỬI */
.input-row { align-items: stretch !important; gap: 12px !important; background: rgba(0,0,0,0.25); padding: 8px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); }
.input-row textarea { background: transparent !important; border: none !important; box-shadow: none !important; color: white !important; font-size: 1.15rem !important;}
.send-btn { background: linear-gradient(135deg, var(--primary), #2563eb) !important; border: none !important; color: white !important; border-radius: 12px !important; font-size: 1.4rem !important; transition: 0.2s; min-width: 60px !important;}
.send-btn:hover { transform: scale(1.05); }
.clear-btn { background: rgba(239, 68, 68, 0.1) !important; color: #fca5a5 !important; border: 1px solid rgba(239, 68, 68, 0.3) !important; border-radius: 12px !important; margin-top: 10px; padding: 12px !important; font-weight: bold !important; font-size: 1.05rem !important; transition: 0.2s;}
.clear-btn:hover { background: rgba(239, 68, 68, 0.2) !important; }

/* ----------------------------------------- */
/* KẾT QUẢ HIỂN THỊ */
/* ----------------------------------------- */
.result-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 24px; padding-bottom: 40px; position: relative; }
.card-wrapper { position: relative; width: 100%; transition: all 0.3s ease; }
.laptop-card { background: rgba(30, 41, 59, 0.4) !important; backdrop-filter: blur(12px) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: var(--radius) !important; padding: 20px !important; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; display: flex; flex-direction: column; gap: 12px; width: 100%; }
.laptop-card:hover:not(.expanded) { transform: translateY(-5px); background: rgba(51, 65, 85, 0.6) !important; border-color: rgba(96, 165, 250, 0.5) !important; box-shadow: 0 0 20px rgba(59, 130, 246, 0.2) !important; }
.laptop-name { font-size: 1.15rem; font-weight: 700; color: white; margin-bottom: 4px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.laptop-price { font-size: 1.45rem; font-weight: 800; color: var(--accent); text-shadow: 0 0 15px rgba(16, 185, 129, 0.3); }
.badges { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
.badge { font-size: 0.8rem; padding: 4px 8px; border-radius: 6px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;}
.badge-cpu { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.2); }
.badge-gpu { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.2); }
.specs-row { display: flex; justify-content: space-between; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1); color: #cbd5e1; font-size: 0.95rem; }
.view-detail-btn { margin-top: auto; width: 100%; background: rgba(255,255,255,0.05); border: none; color: white; padding: 12px; border-radius: 8px; cursor: pointer; transition: 0.2s; font-weight: 600; font-size: 1rem;}
.view-detail-btn:hover { background: rgba(255,255,255,0.15); }

/* TRANG TRÍ PHẦN CẤU HÌNH CHI TIẾT & REVIEW */
.detail-section { margin-top: 18px; padding-top: 15px; border-top: 1px dashed rgba(255,255,255,0.1); }
.detail-section:first-child { border-top: none; padding-top: 0; }
.specs-list { list-style: none; padding: 0; margin: 0; color: #e2e8f0; font-size: 0.95rem; }
.specs-list li { margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.03); display: flex; align-items: flex-start; line-height: 1.4; }
.specs-list li b { color: #94a3b8; width: 100px; flex-shrink: 0; font-weight: 600; }
.review-item { margin-bottom: 10px; padding: 12px; background: rgba(255,255,255,0.04); border-radius: 8px; border-left: 3px solid var(--accent); color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; }
.review-item i { margin-right: 6px; color: #94a3b8; font-size: 1.1rem; }

/* HIỆU ỨNG POPUP NỔI */
.result-grid.has-expanded .card-wrapper:not(.is-active) { opacity: 0.15 !important; filter: blur(6px) !important; pointer-events: none !important; transform: scale(0.95); }
.laptop-card.expanded { z-index: 9999 !important; background: #0f172a !important; border: 2px solid rgba(59, 130, 246, 0.8) !important; box-shadow: 0 40px 80px rgba(0,0,0,0.8) !important; max-height: 85vh !important; overflow-y: auto !important; animation: popModal 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards !important; }
.laptop-card.expanded::-webkit-scrollbar { width: 8px; }
.laptop-card.expanded::-webkit-scrollbar-track { background: transparent; }
.laptop-card.expanded::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 10px; }
.laptop-card.expanded .laptop-name { font-size: 1.6rem; -webkit-line-clamp: unset; }
.laptop-card.expanded .laptop-price { font-size: 1.9rem; }
.card-detail { margin-top: 20px; padding-top: 20px; border-top: 1px dashed rgba(255,255,255,0.2); animation: fadeIn 0.4s ease-in-out; }
.detail-title { color: var(--primary); font-weight: 700; margin-bottom: 12px; font-size: 1.2rem; text-transform: uppercase; }
.detail-content { color: #e2e8f0; font-size: 1.05rem; line-height: 1.8; }
@keyframes popModal { 0% { opacity: 0; transform: translate(-50%, -45%) scale(0.9); } 100% { opacity: 1; transform: translate(-50%, -50%) scale(1); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.laptop-card.expanded .view-detail-btn { background: rgba(239, 68, 68, 0.15) !important; color: #fca5a5 !important; border: 1px solid rgba(239, 68, 68, 0.4) !important; margin-top: 20px;}
.laptop-card.expanded .view-detail-btn:hover { background: rgba(239, 68, 68, 0.3) !important; }
"""

head_js = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<script>
    function updateExpandedPosition() {
        const expandedCard = document.querySelector('.laptop-card.expanded');
        if (expandedCard) {
            const grid = expandedCard.closest('.result-grid');
            const rect = grid.getBoundingClientRect();
            expandedCard.style.left = (rect.left + rect.width / 2) + 'px';
            expandedCard.style.width = (rect.width * 0.92) + 'px';
        }
    }
    window.addEventListener('resize', updateExpandedPosition);

    function toggleDetail(btn) {
        const card = btn.closest('.laptop-card');
        const wrapper = btn.closest('.card-wrapper');
        const grid = btn.closest('.result-grid');
        const detailDiv = card.querySelector('.card-detail');
        const isExpanded = card.classList.contains('expanded');
        
        document.querySelectorAll('.laptop-card.expanded').forEach(c => {
            c.classList.remove('expanded');
            c.style = '';
            const w = c.closest('.card-wrapper');
            w.classList.remove('is-active');
            w.style.height = ''; 
            c.querySelector('.card-detail').style.display = 'none';
            c.querySelector('.view-detail-btn').innerText = 'Xem chi tiết';
        });

        if (!isExpanded) {
            wrapper.style.height = wrapper.offsetHeight + 'px';
            wrapper.classList.add('is-active');
            const rect = grid.getBoundingClientRect();
            card.style.position = 'fixed';
            card.style.top = '50%';
            card.style.left = (rect.left + rect.width / 2) + 'px'; 
            card.style.width = (rect.width * 0.92) + 'px'; 
            card.classList.add('expanded');
            grid.classList.add('has-expanded'); 
            detailDiv.style.display = 'block';
            btn.innerText = '✖ Thu gọn lại';
        } else {
            grid.classList.remove('has-expanded');
        }
    }
</script>
"""

# =========================
# JAVASCRIPT: TỰ ĐỘNG CUỘN 
# =========================
auto_scroll_js = """
function() {
    setTimeout(function() {
        let chatContainers = document.querySelectorAll('.gradio-chatbot .overflow-y-auto, .gradio-chatbot [class*="overflow-"]');
        chatContainers.forEach(container => {
            container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
        });
    }, 100);
    
    setTimeout(function() {
        let chatContainers = document.querySelectorAll('.gradio-chatbot .overflow-y-auto, .gradio-chatbot [class*="overflow-"]');
        chatContainers.forEach(container => {
            container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
        });
    }, 600);
}
"""

# =========================
# KHỞI TẠO GIAO DIỆN CHÍNH
# =========================
with gr.Blocks(css=custom_css, head=head_js) as interface:
    session_memory = gr.State(value="")
    chat_history   = gr.State(value=[]) 

    with gr.Row(elem_id="main-container"):
        
        # CỘT TRÁI (KẾT QUẢ)
        with gr.Column(elem_classes=["results-col-hidden"], elem_id="results-col") as results_col:
            output_display = gr.HTML(label="Kết quả", show_label=False)

        # CỘT PHẢI (CHATBOT)
        with gr.Column(elem_classes=["chat-col-center"], elem_id="chat-col") as chat_col:
            with gr.Group(elem_classes=["chat-panel"]):
                gr.Markdown("### 🤖 Trợ lý AI Tư Vấn Laptop", elem_classes=["chat-title"])
                
                chatbot_ui = gr.Chatbot(
                    value=[{"role": "assistant", "content": "Xin chào! Mình là trợ lý AI thông minh. Mình có thể giúp gì cho việc tìm kiếm Laptop của bạn?"}], 
                    height=650, 
                    show_label=False,
                    elem_classes=["gradio-chatbot"],
                    autoscroll=True
                )
                
                with gr.Row(elem_classes=["input-row"]):
                    query_input = gr.Textbox(
                        show_label=False, 
                        placeholder="VD: Mình tìm laptop gaming tầm 40 triệu...", 
                        lines=1,
                        scale=5
                    )
                    submit_btn = gr.Button("➤", elem_classes=["send-btn"], scale=1)
                
                clear_btn  = gr.Button("🗑️ Cuộc hội thoại mới", elem_classes=["clear-btn"])

    # ==== KẾT NỐI SỰ KIỆN ====
    submit_btn.click(
        fn=chat_logic, 
        inputs=[query_input, session_memory, chat_history, chatbot_ui], 
        outputs=[output_display, session_memory, chat_history, chatbot_ui, query_input, results_col, chat_col]
    ).then(fn=None, inputs=None, outputs=None, js=auto_scroll_js)
    
    query_input.submit(
        fn=chat_logic, 
        inputs=[query_input, session_memory, chat_history, chatbot_ui], 
        outputs=[output_display, session_memory, chat_history, chatbot_ui, query_input, results_col, chat_col]
    ).then(fn=None, inputs=None, outputs=None, js=auto_scroll_js)
    
    # Sử dụng hàm reset_chat từ logic thay cho lambda
    clear_btn.click(
        fn=reset_chat, 
        inputs=None, 
        outputs=[output_display, session_memory, chat_history, chatbot_ui, query_input, results_col, chat_col]
    )

if __name__ == "__main__":
    interface.launch(inbrowser=True)    