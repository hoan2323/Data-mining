import re
import chromadb
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer

CHROMA_DIR           = r"chroma_db"
COLLECTION           = "laptops"
MODEL_NAME           = "intfloat/multilingual-e5-large"
SIMILARITY_THRESHOLD = 0.75
LOOKUP_THRESHOLD     = 0.6

LOOKUP_KEYWORDS = [
    "thông tin", "tra cứu", "cho tôi biết", "cho mình biết",
    "cấu hình", "thông số", "specs", "chi tiết", "xem chi tiết",
    "cấu hình của", "thông số của", "specs của",
]

DEDICATED_KEYWORDS = [
    "gaming", "game", "chơi game", "chiến game", "điện tử",
    "render", "dựng phim", "edit video", "chỉnh phim",
    "đồ họa", "thiết kế", "3d",
    "gpu rời", "card rời",
    "rtx", "gtx", "rx 6", "rx 7", "nvidia", "radeon",
    "stream",
]

INTEGRATED_KEYWORDS = [
    "văn phòng", "office", "card tích hợp", "không cần gpu",
    "học tập", "sinh viên cơ bản", "lướt web", "xem phim",
    "mỏng nhẹ", "pin trâu", "di chuyển nhiều",
]

BRAND_MAP = {
    "apple": "Apple",    "macbook": "Apple",   "mac": "Apple",
    "dell": "Dell",      "xps": "Dell",        "inspiron": "Dell",
    "hp": "HP",          "pavilion": "HP",     "envy": "HP",
    "spectre": "HP",     "omen": "HP",
    "asus": "ASUS",      "vivobook": "ASUS",   "zenbook": "ASUS",
    "rog": "ASUS",       "tuf": "ASUS",
    "lenovo": "Lenovo",  "thinkpad": "Lenovo", "ideapad": "Lenovo",
    "yoga": "Lenovo",    "legion": "Lenovo",
    "acer": "Acer",      "aspire": "Acer",     "swift": "Acer",
    "nitro": "Acer",     "predator": "Acer",
    "msi": "MSI",        "raider": "MSI",      "stealth": "MSI",
    "prestige": "MSI",   "katana": "MSI",
    "samsung": "Samsung","galaxy book": "Samsung",
    "gigabyte": "GIGABYTE", "aorus": "GIGABYTE",
}

BRAND_NAMES = [
    "macbook", "apple", "dell", "hp", "asus", "lenovo", "acer",
    "msi", "samsung", "gigabyte", "vivobook", "zenbook", "rog",
    "tuf", "thinkpad", "ideapad", "legion", "aspire", "swift",
    "nitro", "predator", "pavilion", "envy", "spectre", "omen",
    "xps", "inspiron", "raider", "stealth", "katana", "aorus",
]

BRAND_ONLY = [
    "apple", "dell", "hp", "asus", "lenovo", "acer",
    "msi", "samsung", "gigabyte", "mac", "macbook",
]

SEARCH_INTENT_WORDS = [
    "tôi cần", "tôi muốn", "cho tôi", "gợi ý", "tư vấn",
    "nên mua", "laptop nào", "máy nào", "tìm kiếm",
    "dưới", "tầm", "khoảng", "gaming", "sinh viên",
]


def load_retriever():
    model      = SentenceTransformer(MODEL_NAME)
    client     = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION)
    print(f"[LOAD] '{COLLECTION}' — {collection.count()} vectors")
    return model, collection


def is_direct_name(query: str) -> bool:
    q             = query.lower().strip()
    has_brand     = any(b in q for b in BRAND_NAMES)
    is_short      = len(q.split()) <= 8
    is_not_search = not any(w in q for w in SEARCH_INTENT_WORDS)
    is_brand_only = any(q == b or q == f"laptop {b}" for b in BRAND_ONLY)
    return has_brand and is_short and is_not_search and not is_brand_only


def is_lookup(query: str) -> bool:
    return any(kw in query.lower() for kw in LOOKUP_KEYWORDS)


def parse_intent(query: str) -> dict:
    q = query.lower()
    filters = {}

    m = re.search(r"(?:dưới|<|max|tối đa|không quá)\s*(\d+(?:[.,]\d+)?)\s*(tr(?:iệu)?|m(?:iệu)?)?", q)
    if m:
        val = float(m.group(1).replace(",", "."))
        filters["max_price"] = val * 1_000_000 if val < 1000 else val

    m = re.search(r"(?:tầm|khoảng|trong tầm|tầm giá)\s*(\d+(?:[.,]\d+)?)\s*(tr(?:iệu)?|m(?:iệu)?)?", q)
    if m:
        val = float(m.group(1).replace(",", "."))
        mid = val * 1_000_000 if val < 1000 else val
        filters["min_price"] = mid * 0.90
        filters["max_price"] = mid * 1.15

    m = re.search(r"(?:trên|từ|tối thiểu|ít nhất|>=|min)\s*(\d+(?:[.,]\d+)?)\s*(tr(?:iệu)?|m(?:iệu)?)?", q)
    if m:
        val = float(m.group(1).replace(",", "."))
        filters["min_price"] = val * 1_000_000 if val < 1000 else val

    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:tr(?:iệu)?)?\s*[-–~đến tới]+\s*(\d+(?:[.,]\d+)?)\s*(tr(?:iệu)?)?", q)
    if m:
        lo = float(m.group(1).replace(",", "."))
        hi = float(m.group(2).replace(",", "."))
        if lo < 1000: lo, hi = lo * 1_000_000, hi * 1_000_000
        filters["min_price"] = lo
        filters["max_price"] = hi

    m = re.search(r"(?:ram\s*(\d+)|(\d+)\s*gb\s*ram|(?:ít nhất|tối thiểu|>=|min)\s*(\d+)\s*gb)", q)
    if m:
        filters["min_ram"] = float(next(v for v in m.groups() if v))

    m = re.search(r"(?:(\d+)\s*tb\s*ssd|ssd\s*(\d+)\s*tb|(\d+)\s*gb\s*ssd|ssd\s*(\d+)\s*gb)", q)
    if m:
        val = float(next(v for v in m.groups() if v))
        filters["min_storage"] = val * 1024 if "tb" in q and val < 10 else val

    if any(kw in q for kw in DEDICATED_KEYWORDS):
        filters["gpu_type"] = "dedicated"
    elif any(kw in q for kw in INTEGRATED_KEYWORDS):
        filters["gpu_type"] = "integrated"

    for keyword, brand_val in BRAND_MAP.items():
        if keyword in q:
            filters["brand"] = brand_val
            break

    return filters



def build_where_filter(
    max_price  : float = None,
    min_price  : float = None,
    min_ram    : float = None,
    min_storage: float = None,
    gpu_type   : str   = None,
    brand      : str   = None,
) -> dict | None:
    filters = []
    if max_price  : filters.append({"price"   : {"$lte": max_price}})
    if min_price  : filters.append({"price"   : {"$gte": min_price}})
    if min_ram    : filters.append({"ram"     : {"$gte": min_ram}})
    if min_storage: filters.append({"storage" : {"$gte": min_storage}})
    if gpu_type   : filters.append({"gpu_type": {"$eq" : gpu_type}})
    if brand      : filters.append({"brand"   : {"$eq" : brand}})

    if   len(filters) == 0: return None
    elif len(filters) == 1: return filters[0]
    else                  : return {"$and": filters}


def search(
    query      : str,
    model      : SentenceTransformer,
    collection : chromadb.Collection,
    top_k      : int   = 10,
    max_price  : float = None,
    min_price  : float = None,
    min_ram    : float = None,
    min_storage: float = None,
    gpu_type   : str   = None,
    brand      : str   = None,
) -> tuple[list[dict], dict]:

    auto_filters  = parse_intent(query)
    manual        = {k: v for k, v in {
        "max_price": max_price, "min_price": min_price,
        "min_ram"  : min_ram,   "min_storage": min_storage,
        "gpu_type" : gpu_type,  "brand": brand,
    }.items() if v is not None}
    final_filters = {**auto_filters, **manual}

    where        = build_where_filter(**final_filters)
    query_vector = model.encode([f"query: {query}"], normalize_embeddings=True).tolist()

    results = collection.query(
        query_embeddings = query_vector,
        n_results        = top_k,
        where            = where,
        include          = ["documents", "metadatas", "distances"],
    )

    output = []
    for i in range(len(results["ids"][0])):
        similarity = round(1 - results["distances"][0][i], 3)
        if similarity < SIMILARITY_THRESHOLD:
            continue
        meta = results["metadatas"][0][i]
        output.append({
        "rank"  : i + 1,
        "name"  : meta["name"],
        "brand" : meta.get("brand", "Đang cập nhật"), 
        "cpu"   : meta["cpu"],
        "ram"   : meta["ram"],
        "gpu"   : meta["gpu"],
        "storage"          : meta["storage"],
        "screen_size"      : meta["screen_size"],
        "screen_resolution": meta["screen_resolution"],
        "screen_panel"     : meta["screen_panel"],
        "battery_wh"       : meta["battery_wh"],
        "color"            : meta["color"],
        "price"            : meta["price"],
        "rating"           : meta["rating"],
        "similarity"       : similarity,
        "mo_ta"            : results["documents"][0][i],  
    })

    return output, final_filters


def name_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def lookup(
    query      : str,
    model      : SentenceTransformer,
    collection : chromadb.Collection,
    top_k      : int = 10,
) -> dict | None:
    query_vector = model.encode([f"query: {query}"], normalize_embeddings=True).tolist()

    results = collection.query(
        query_embeddings = query_vector,
        n_results        = top_k,
        include          = ["documents", "metadatas", "distances"],
    )

    if not results["ids"][0]:
        return None

    candidates = []
    for i in range(len(results["ids"][0])):
        sem_score  = round(1 - results["distances"][0][i], 3)
        if sem_score < LOOKUP_THRESHOLD:
            continue
        meta        = results["metadatas"][0][i]
        name_score  = name_similarity(query, meta["name"])
        final_score = round(0.4 * sem_score + 0.6 * name_score, 4)
        candidates.append({
            "name"       : meta["name"],
            "brand"      : meta["brand"],
            "cpu"        : meta["cpu"],
            "ram"        : meta["ram"],
            "gpu"        : meta["gpu"],
            "storage"    : meta["storage"],
            "screen_size": meta["screen_size"],
            "screen_resolution": meta["screen_resolution"],
            "screen_panel"     : meta["screen_panel"],
            "battery_wh"      : meta["battery_wh"],
            "color"           : meta["color"],
            "price"      : meta["price"],
            "rating"     : meta["rating"],
            "similarity" : sem_score,
            "final_score": final_score,
            "mo_ta"      : results["documents"][0][i],
        })

    if not candidates:
        return None

    return max(candidates, key=lambda x: x["final_score"])


def print_card(r: dict):
    print(f"\n  {'★' * int(r['rating'])}  [{r['similarity']}]  {r['name']} - {r['price']:,.0f} VNĐ")
    print(f"  {'─' * 55}")


def print_lookup_card(r: dict):
    print("\n" + "=" * 60)
    print(f"  📋 {r['name']}  (similarity: {r['similarity']})")
    print("=" * 60)
    print(f"  Hãng     : {r['brand']}")
    print(f"  CPU      : {r['cpu']}")
    print(f"  RAM      : {r['ram']}GB   |  Storage : {r['storage']}GB")
    print(f"  GPU      : {r['gpu']}")
    print(f"  Màn hình : {r['screen_size']} inch")
    print(f"  Giá      : {r['price']:,.0f} VNĐ")
    print(f"  Rating   : {r['rating']}/5")
    print(f"  Màn hình : {r['screen_resolution']} | {r['screen_panel']}")
    print(f"  Pin      : {r['battery_wh']} Wh")
    print(f"  Màu sắc  : {r['color']}")
    print(f"\n  Mô tả:\n  {r['mo_ta']}")
    print("=" * 60)


if __name__ == "__main__":
    model, collection = load_retriever()

    print("=" * 60)
    print("   LAPTOP ASSISTANT  |  'exit' để thoát")
    print("=" * 60)

    while True:
        query = input("\nNhập câu hỏi: ").strip()
        if query.lower() == "exit":
            print("Tạm biệt")
            break
        if not query:
            continue

        if is_direct_name(query) or is_lookup(query):
            print("\nChế độ: TRA CỨU")
            result = lookup(query, model, collection)
            if result:
                print_lookup_card(result)
            else:
                print("Không tìm thấy máy phù hợp hoặc câu hỏi không liên quan đến laptop.")

        else:
            results, used_filters = search(query, model, collection, top_k=10)
            mode = "Hybrid" if used_filters else "🔵 Semantic"
            print(f"\n{mode}  |  Filters: {used_filters or 'none'}")
            print("=" * 60)

            if not results:
                print("Không tìm thấy kết quả phù hợp.")
                print("Thử hỏi: 'laptop gaming dưới 25 triệu' hoặc 'cấu hình MacBook Air M4'")
                continue

            for r in results:
                print_card(r)
