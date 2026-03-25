import os
import csv
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("NVIDIA_NIM_API")
base_url = "https://integrate.api.nvidia.com/v1"

client = OpenAI(base_url=base_url, api_key=api_key)

def get_categorized_models():
    """ 
    ดึงรายชื่อโมเดลทั้งหมดจาก API เเละจัดหมวดหมู่ 
    คืนค่า dict ที่มี list ของโมเดลในแต่ละหมวดหมู่
    """
    try:
        data = client.models.list()
        all_models = [m.id for m in data.data]
    except Exception as e:
        print(f"Error fetching models: {e}")
        return {}

    categories = {
        "Text": [], "Code": [], "Vision": [], 
        "Embedding": [], "Safety": [], "Video_Other": []
    }

    for name in all_models:
        name_lower = name.lower()
        if "guard" in name_lower or "reward" in name_lower or "safety" in name_lower:
            categories["Safety"].append(name)
        elif "embed" in name_lower or "rerank" in name_lower or "retriever" in name_lower or "parse" in name_lower:
            categories["Embedding"].append(name)
        elif "vl" in name_lower or "vision" in name_lower or "neva" in name_lower or "vila" in name_lower or "pixtral" in name_lower or "clip" in name_lower:
            categories["Vision"].append(name)
        elif "code" in name_lower or "coder" in name_lower or "sql" in name_lower:
            categories["Code"].append(name)
        elif "video" in name_lower or "audio" in name_lower or "streampetr" in name_lower:
            categories["Video_Other"].append(name)
        else:
            categories["Text"].append(name)
            
    return categories

def init_csv(filename, extra_headers=[]):
    """ สร้างไฟล์ CSV ที่มี 2 column เเรกตามโจทย์ """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    headers = ["Build NVIDIA URL (Model)", "API Model ID", "Status"] + extra_headers
    
    # ถ้าไฟล์ยังไม่มี ให้เขียน Header ไว้เลย
    if not os.path.exists(filename):
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    return headers

def append_csv(filename, model_name, status, extra_data=[]):
    """ เขียนผลทดสอบแต่ละโมเดลลงแถวใหม่ """
    build_url = f"https://build.nvidia.com/{model_name}" # URL ที่ถูกต้องของ NVIDIA NIM
    
    # ดักข้อความ Error ให้อ่านง่ายขึ้น
    for i in range(len(extra_data)):
        if isinstance(extra_data[i], str):
            if "status': 404" in extra_data[i] or "404 page not found" in extra_data[i] or "404 Not Found" in extra_data[i]:
                extra_data[i] = "404 Not Found (Account missing specific permission / Gated Model)"
            elif "Internal Server Error" in extra_data[i] or "status': 500" in extra_data[i]:
                extra_data[i] = "500 Internal Error (API Gateway issue or Invalid payload format)"
                
    row = [build_url, model_name, status] + extra_data
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)
