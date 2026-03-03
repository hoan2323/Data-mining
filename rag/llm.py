from groq import Groq
from search import load_retriever, search, lookup, is_direct_name, is_lookup
from apikey import API_KEY
import re  # ✅ THÊM

GROQ_API_KEY = API_KEY
GROQ_MODEL   = "meta-llama/llama-4-scout-17b-16e-instruct"

llm = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
Bạn là trợ lý tư vấn laptop chuyên nghiệp tại cửa hàng công nghệ.

MỤC TIÊU:
Giúp khách hàng chọn được laptop phù hợp nhất dựa hoàn toàn vào dữ liệu được cung cấp.
KHÔNG được bịa thêm thông tin ngoài dữ liệu.

=====================
NGUYÊN TẮC BẮT BUỘC
=====================

1. Chỉ sử dụng thông tin trong phần "Dữ liệu laptop tìm được".
2. Nếu danh sách có bao nhiêu máy thì chỉ tư vấn đúng bấy nhiêu máy. Tuyệt đối không tự thêm máy mới, hay lược bỏ máy nào.
3. Không suy đoán cấu hình, không giả định thông tin không có trong dữ liệu.
4. Nếu không tìm thấy máy phù hợp → xin lỗi và yêu cầu khách mô tả lại nhu cầu.
5. Không tự ý thay thế sản phẩm.
6. TUYỆT ĐỐI KHÔNG giải thích quá trình xử lý, không nói "dựa trên dữ liệu trước đó", 
   không nói "tuy nhiên dữ liệu không được cung cấp", không mô tả bạn đang làm gì.
   Chỉ trả lời trực tiếp vào nội dung khách hỏi

=====================
QUY TẮC TRẢ LỜI THEO LOẠI CÂU HỎI, QUAN TRỌNG: PHẢI TUÂN THỦ NGHIÊM NGẶT
=====================

    A. Nếu là tư vấn chung (ví dụ: "tư vấn laptop gaming", "laptop 20 triệu", "học lập trình nên mua máy nào"):
    - Với mỗi máy chỉ trình bày:
    • Tên máy
    • Giá
    - TUYỆT ĐỐI không liệt kê CPU, RAM, GPU, Storage nếu khách không yêu cầu.

    B. Nếu khách hỏi về một máy cụ thể:
    - Chỉ trả lời về đúng máy đó.
    - Có thể trình bày đầy đủ cấu hình.

    C. Nếu khách yêu cầu so sánh:
    - nếu khách yêu cầu so sánh 1 với 2 (có thể thay bằng các số khác), nghĩa là họ đang dựa vào kết quả trả từ kết quả của bạn vừa trả 
            vd: bạn trả ra 
            1. Laptop Lenovo Gaming LOQ 15ARP9 - 83JC00LVVN – 22,690,000đ
            2. Laptop Lenovo Gaming LOQ 15AHP10 - 83JG0047VN – 31,690,000đ
            3. Laptop Lenovo Gaming Legion 5 15AHP10 - 83M0002XVN – 36,690,000đ
            mà khách yêu cầu so sánh 1 với 2 nghĩa là họ đang muốn so sánh 2 máy Lenovo LOQ 15ARP9 và Lenovo LOQ 15AHP10, tương tự có thể là 1 với 3, hoặc 2 với 3... hoặc cả 3 máy với nhau.

    - tương tự nếu khách muốn chi tiết máy số 1 thì nghĩa là chi tiết máy Lenovo LOQ 15ARP9, nếu máy số 2 thì chi tiết máy Lenovo LOQ 15AHP10, nếu máy số 3 thì chi tiết máy Lenovo Legion 5 15AHP10...
    - Nếu không chỉ định → so sánh các máy cùng phân khúc giá hoặc cấu hình trong dữ liệu.
    - KHI SO SÁNH, PHẢI NÊU RÕ ƯU NHƯỢC ĐIỂM CỦA TỪNG MÁY DỰA TRÊN CẤU HÌNH VÀ GIÁ CẢ. 

    D. Nếu khách hỏi chi tiết cấu hình:
    - Trình bày đầy đủ thông tin cấu hình từ dữ liệu.

"""


def format_search_context(results: list[dict]) -> str:
    if not results:
        return "Không tìm thấy laptop phù hợp."

    lines = []
    for r in results:
        lines.append(
            f"- {r['name']}\n"
            f"  CPU: {r['cpu']} | RAM: {r['ram']}GB | Storage: {r['storage']}GB\n"
            f"  GPU: {r['gpu']}\n"
            f"  Màn hình: {r['screen_size']} inch | {r['screen_resolution']} | {r['screen_panel']}\n"
            f"  Pin: {r['battery_wh']} Wh | Màu sắc: {r['color']}\n"
            f"  Giá: {r['price']:,.0f}đ | Rating: {r['rating']}/5\n"
            f"  Mô tả: {r['mo_ta'][:200]}..."
        )
    return "\n".join(lines)


def format_lookup_context(result: dict) -> str:
    if not result:
        return "Không tìm thấy thông tin máy."

    return (
        f"- {result['name']}\n"
        f"  Hãng: {result['brand']} | CPU: {result['cpu']}\n"
        f"  RAM: {result['ram']}GB | Storage: {result['storage']}GB\n"
        f"  GPU: {result['gpu']}\n"
        f"  Màn hình: {result['screen_size']} inch | {result['screen_resolution']} | {result['screen_panel']}\n"
        f"  Pin: {result['battery_wh']} Wh | Màu sắc: {result['color']}\n"
        f"  Giá: {result['price']:,.0f}đ | Rating: {result['rating']}/5\n"
        f"  Mô tả: {result['mo_ta']}"
    )


def ask_llm(user_query: str, context: str, history: list) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for h in history[-3:]:
        messages.append({"role": "user",      "content": h["user"]})
        messages.append({"role": "assistant", "content": h["assistant"]})

    messages.append({
        "role": "user",
        "content": (
            f"--- Dữ liệu laptop tìm được ---\n{context}\n\n"
            f"--- Câu hỏi của khách ---\n{user_query}"
        )
    })

    response = llm.chat.completions.create(
        model    = GROQ_MODEL,
        messages = messages,
    )
    return response.choices[0].message.content.strip()


def extract_indices(query: str) -> list[int]:
    q = query.lower()

    # ✅ Mở rộng keyword nhận diện tham chiếu số thứ tự
    ref_keywords = r'(?:máy|số|lap|laptop|cái|sản phẩm|sp)'
    matches = re.findall(rf'{ref_keywords}\s*([1-9][0-9]?)', q)
    if matches:
        return [int(x) for x in matches]

    action_keywords = ['so sánh', 'compare', 'chi tiết', 'thông số', 'detail', 'xem']
    if any(kw in q for kw in action_keywords):
        return [int(x) for x in re.findall(r'\b([1-9]|1[0-9]|20)\b', q)]

    return []


if __name__ == "__main__":
    model, collection = load_retriever()
    history          = []
    session_products = {}  

    print("=" * 60)
    print("TƯ VẤN LAPTOP AI  |  'exit' để thoát")
    print("=" * 60)

    while True:
        query = input("Bạn: ").strip()
        if query.lower() == "exit":
            break
        if not query:
            continue

        indices = extract_indices(query)

    
        if indices and session_products:
            valid = [session_products[i] for i in indices if i in session_products]
            if not valid:
                context = "Không tìm thấy máy theo số thứ tự đó trong danh sách vừa tìm."
            elif len(valid) == 1:
                context = format_lookup_context(valid[0])  
            else:
                context = format_search_context(valid)      


        elif is_direct_name(query) or is_lookup(query):
            result  = lookup(query, model, collection)
            context = format_lookup_context(result)

        else:
            results, _ = search(query, model, collection, top_k=10)
            context    = format_search_context(results)
            session_products = {i + 1: r for i, r in enumerate(results)}  

        answer = ask_llm(query, context, history)
        print(f"\n{answer}\n")

        history.append({"user": query, "assistant": answer})
