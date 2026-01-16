import pandas as pd
import re

# Load data
df = pd.read_csv('test_set_no_label.csv')

# Define keywords
keywords_thai = {
    "Taste": ["อร่อย", "รสชาติ", "เค็ม", "หวาน", "เผ็ด", "จืด", "ปรุง", "นัว", "แซ่บ", "ขม", "เปรี้ยว", "กลมกล่อม", "เลี่ยน", "หอม", "รสดี", "ถูกปาก", "ทานง่าย", "รสจัด"],
    "Portion": ["เยอะ", "น้อย", "จานใหญ่", "อิ่ม", "คุ้ม", "ขนาด", "จุก", "เติม", "ไม่อั้น", "ชิ้นใหญ่", "ตัวใหญ่"],
    "Price": ["ราคา", "แพง", "ถูก", "บาท", "คุ้ม", "จ่าย", "ตังค์", "เงิน", "บิล", "แพงมาก", "ไม่แพง"],
    "Quality": ["สด", "เน่า", "คาว", "เกรด", "คุณภาพ", "พรีเมียม", "วัตถุดิบ", "สะอาด", "สกปรก", "ใหม่", "เก่า", "เนื้อดี", "เนื้อเน่า"],
    "Service": ["บริการ", "พนักงาน", "เสิร์ฟ", "พูดจา", "ยิ้มแย้ม", "หน้าบึ้ง", "ดูแล", "มารยาท", "ต้อนรับ", "เรียก", "ชาร์จ", "คนขาย"],
    "Speed": ["ช้า", "เร็ว", "รอนาน", "ไว", "ด่วน", "ทันใจ", "รอ", "นาน", "คิว"],
    "Location": ["ที่จอดรถ", "เดินทาง", "ใกล้", "ไกล", "bts", "mrt", "ร้าน", "บรรยากาศ", "วิว", "ตกแต่ง", "หาง่าย", "หายาก", "ซอย", "ถนน", "จอด", "สถานที่", "แอร์", "ร้อน", "เย็น"]
}

keywords_eng = {
    "Taste": ["taste", "tasted", "delicious", "yummy", "flavor", "flavour", "salty", "sweet", "spicy", "bland", "bitter", "sour", "tasty", "good food"],
    "Portion": ["portion", "portions", "big", "small", "full", "amount", "size", "quantity", "filling"],
    "Price": ["price", "prices", "expensive", "cheap", "cost", "worth", "bill", "money", "baht", "value"],
    "Quality": ["quality", "fresh", "stale", "rotten", "grade", "premium", "ingredient", "ingredients", "clean", "dirty", "hygiene"],
    "Service": ["service", "staff", "waiter", "waitress", "serve", "served", "serving", "rude", "polite", "friendly", "helpful", "attitude", "manager"],
    "Speed": ["speed", "slow", "fast", "wait", "waited", "waiting", "quick", "rush", "rushed", "late", "queue", "line", "hour", "hours", "minute", "minutes"],
    "Location": ["location", "parking", "park", "view", "atmosphere", "decor", "near", "far", "place", "restaurant", "access", "station", "walk"]
}

def classify_review(text):
    if not isinstance(text, str):
        return []
    
    text_lower = text.lower()
    found_cats = set()

    # Thai Matching
    for cat, words in keywords_thai.items():
        for word in words:
            if word in text_lower:
                found_cats.add(cat)
                break
    
    # English Matching (using word boundaries)
    for cat, words in keywords_eng.items():
        if cat in found_cats: continue
        pattern = r'\b(' + '|'.join([re.escape(w) for w in words]) + r')\b'
        if re.search(pattern, text_lower):
            found_cats.add(cat)

    ordered_cats = ["Taste", "Portion", "Price", "Quality", "Service", "Speed", "Location"]
    return [c for c in ordered_cats if c in found_cats]

# Apply classification
df['catagory_label'] = df['text'].apply(classify_review)

# Save result
df.to_csv('test_set_with_label.csv', index=False)