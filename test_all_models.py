import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

# ดึงค่า API Key จาก .env
api_key = os.getenv("NVIDIA_NIM_API")

# ตั้งค่า Client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

def test_model(model_name, prompt):
    print(f"\n--- เริ่มทดสอบโมเดล: {model_name} ---")
    start_time = time.time()
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            stream=True
        )
        
        first_token_time = None
        token_count = 0
        
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                if first_token_time is None:
                    first_token_time = time.time()
                    ttft = first_token_time - start_time
                    print(f"✅ สำเร็จ! TTFT: {ttft:.4f} วินาที")
                token_count += 1
                
        end_time = time.time()
        
        if first_token_time is not None:
            generation_time = end_time - first_token_time
            tps = token_count / generation_time if generation_time > 0 else 0
            print(f"🚀 TPS: {tps:.2f} tokens/sec")
            return {"status": "success", "ttft": ttft, "tps": tps}
        else:
            print("❌ ไม่ได้รับข้อมูล")
            return {"status": "no_data"}
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    prompt = "Hello"
    
    # 1. ดึงรายชื่อโมเดลทั้งหมดจาก NVIDIA (ที่เป็นไปตามมาตรฐาน OpenAI API)
    try:
        models = client.models.list()
        model_names = [model.id for model in models.data]
        print(f"พบโมเดลทั้งหมด {len(model_names)} โมเดลใน API")
    except Exception as e:
        print(f"ไม่สามารถดึงรายชื่อโมเดลได้: {e}")
        model_names = []
    
    # 2. ทดสอบแต่ละโมเดล
    results = {}
    for model_name in sorted(model_names):
        result = test_model(model_name, prompt)
        results[model_name] = result
        
    # สรุปผล
    success_count = sum(1 for v in results.values() if v.get("status") == "success")
    print(f"\n=========================================")
    print(f"สรุปผลการทดสอบ: ทดสอบทั้งหมด {len(model_names)} โมเดล")
    print(f"ใช้งาน chat.completions ได้สำเร็จ: {success_count} โมเดล")
    print(f"=========================================")
