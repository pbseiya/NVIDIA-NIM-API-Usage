import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

# ดึงค่า API Key จาก .env
api_key = os.getenv("NVIDIA_NIM_API")

# ตั้งค่า Client เพื่อชี้ไปยัง NVIDIA URL
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

def test_model_performance(model_name, prompt):
    print(f"\n--- เริ่มทดสอบโมเดล: {model_name} ---")
    
    start_time = time.time()
    
    try:
        # เรียกใช้ API แบบ Streaming
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
            stream=True
        )
        
        first_token_time = None
        token_count = 0
        full_response = ""
        
        for index, chunk in enumerate(response):
            if chunk.choices[0].delta.content is not None:
                # บันทึกเวลาเมื่อได้รับ Token แรก
                if first_token_time is None:
                    first_token_time = time.time()
                    ttft = first_token_time - start_time
                    print(f"⏱️ Time to First Token (TTFT): {ttft:.4f} วินาที")
                
                # นับจำนวน token (โดยประมาณจาก chunk ที่ส่งมา)
                token_count += 1
                full_response += chunk.choices[0].delta.content
                
        end_time = time.time()
        
        if first_token_time is not None:
            # คำนวณเวลาที่ใช้สร้าง Token ทั้งหมดหลังได้ Token แรก
            generation_time = end_time - first_token_time
            # คำนวณ Tokens Per Second (TPS)
            tps = token_count / generation_time if generation_time > 0 else 0
            
            print(f"📊 จำนวน Token ที่สร้าง: ~{token_count} tokens")
            print(f"🚀 Tokens Per Second (TPS): {tps:.2f} tokens/sec")
            print(f"⏲️ เวลาทั้งหมด: {end_time - start_time:.4f} วินาที")
        else:
            print("ไม่ได้รับ Token ใดๆ จาก API")
            
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    prompt = "Tell me a short story about a time traveler who goes back to the dinosaur age. (Around 200 words)"
    
    # ตัวอย่างโมเดลที่สามารถทดสอบได้ สามารถเปลี่ยนชื่อได้จาก https://build.nvidia.com/explore/discover
    models_to_test = [
        "meta/llama3-70b-instruct",
        "meta/llama3-8b-instruct",
        "mistralai/mixtral-8x22b-instruct-v0.1"
    ]
    
    for model in models_to_test:
        test_model_performance(model, prompt)
