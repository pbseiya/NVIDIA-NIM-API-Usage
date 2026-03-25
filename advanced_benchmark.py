import os
import time
import json
import httpx
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# โหลดตัวแปรและตั้งค่า API Key
load_dotenv()
api_key = os.getenv("NVIDIA_NIM_API")
base_url = "https://integrate.api.nvidia.com/v1"

client = OpenAI(base_url=base_url, api_key=api_key)

# ตั้งค่า Qdrant Client (รันใน Docker)
try:
    qdrant = QdrantClient("localhost", port=6333)
except Exception as e:
    print(f"⚠️ ไม่สามารถเชื่อมต่อ Qdrant ได้: {e}")
    qdrant = None

# Sample Data
sample_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

def run_chat_test(model_name, prompt, category="Text"):
    print(f"\n▶️ กำลังทดสอบ ({category}): {model_name}")
    start_time = time.time()
    result = {"model": model_name, "category": category, "status": "Failed"}
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=150,
            stream=True
        )
        
        first_token_time = None
        token_count = 0
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                if first_token_time is None:
                    first_token_time = time.time()
                    ttft = first_token_time - start_time
                    result["TTFT (s)"] = round(ttft, 4)
                token_count += 1
                
        end_time = time.time()
        if first_token_time is not None:
            gen_time = end_time - first_token_time
            tps = token_count / gen_time if gen_time > 0 else 0
            result.update({"Status": "Success", "Total Tokens": token_count, "TPS": round(tps, 2)})
            print(f"   ✅ TTFT: {ttft:.4f}s | TPS: {tps:.2f} tokens/s")
        else:
            print("   ⚠️ ตอบกลับมาแต่ไม่มีข้อความ (No Content)")
            
    except Exception as e:
        print(f"   ❌ ล้มเหลว: {e}")
        result["Error"] = str(e)
    return result

def run_vision_test(model_name):
    print(f"\n▶️ กำลังทดสอบ (Vision): {model_name}")
    start_time = time.time()
    result = {"model": model_name, "category": "Vision", "status": "Failed"}
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail."},
                    {"type": "image_url", "image_url": {"url": sample_image_url}}
                ]
            }],
            max_tokens=150,
            stream=True
        )
        
        first_token_time = None
        token_count = 0
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                if first_token_time is None:
                    first_token_time = time.time()
                    ttft = first_token_time - start_time
                    result["TTFT (s)"] = round(ttft, 4)
                token_count += 1
                
        end_time = time.time()
        if first_token_time is not None:
            gen_time = end_time - first_token_time
            tps = token_count / gen_time if gen_time > 0 else 0
            result.update({"Status": "Success", "Total Tokens": token_count, "TPS": round(tps, 2)})
            print(f"   ✅ TTFT: {ttft:.4f}s | TPS: {tps:.2f} tokens/s")
    except Exception as e:
        print(f"   ❌ ล้มเหลว: {e}")
        result["Error"] = str(e)
    return result

def run_embedding_test(model_name):
    print(f"\n▶️ กำลังทดสอบ (Embedding & Qdrant): {model_name}")
    start_time = time.time()
    result = {"model": model_name, "category": "Embedding", "status": "Failed"}
    texts = ["AI is evolving rapidly.", "NVIDIA NIM provides serverless inferencing.", "Vectors are cool."]
    
    try:
        # 1. Test Embedding API Speed
        api_start = time.time()
        res = client.embeddings.create(input=texts, model=model_name, encoding_format="float")
        api_time = time.time() - api_start
        
        dim = len(res.data[0].embedding)
        result["API Latency (s)"] = round(api_time, 4)
        result["Dimension"] = dim
        print(f"   ✅ API Latency: {api_time:.4f}s | Dimension: {dim}")
        
        # 2. Test Qdrant Insertion
        if qdrant:
            collection_name = "test_collection"
            try:
                # Recreate collection to match dimension
                if qdrant.collection_exists(collection_name):
                    qdrant.delete_collection(collection_name)
                    
                qdrant.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )
                
                points = [
                    PointStruct(id=i, vector=d.embedding, payload={"text": texts[i]})
                    for i, d in enumerate(res.data)
                ]
                
                db_start = time.time()
                qdrant.upsert(collection_name=collection_name, points=points)
                db_time = time.time() - db_start
                result["Qdrant Insert (s)"] = round(db_time, 4)
                print(f"   ✅ ทันทึกเวกเตอร์ลง Qdrant สำเร็จใน: {db_time:.4f}s")
                result["Status"] = "Success"
            except Exception as db_e:
                print(f"   ⚠️ ขัดข้องที่ Qdrant: {db_e}")
                result["Status"] = "API Success, DB Failed"
        else:
            result["Status"] = "API Success (No Qdrant)"
            
    except Exception as e:
        print(f"   ❌ ล้มเหลว: {e}")
        result["Error"] = str(e)
    return result

def main():
    print("🚀 เริ่มตัววัดผลการทำงานโมเดลแบบเจาะจงประเภท (Comprehensive Benchmark)")
    
    models_to_test = {
        "Text": ["meta/llama-3.1-8b-instruct", "google/gemma-2-9b-it"],
        "Code": ["qwen/qwen2.5-coder-7b-instruct", "ibm/granite-8b-code-instruct"],
        "Safety": ["nvidia/llama-3.1-nemoguard-8b-content-safety"],
        "Vision": ["nvidia/neva-22b", "meta/llama-3.2-11b-vision-instruct"],
        "Embedding": ["nvidia/nv-embedqa-e5-v5", "snowflake/arctic-embed-l"],
        "Video_Audio_Other": ["nvidia/streampetr"] # Model เฉพาะทางเช่น 3D/Video มักจะรับ payload เฉพาะ
    }
    
    results = []
    
    for category, models in models_to_test.items():
        for model in models:
            if category in ["Text", "Code"]:
                prompt = "Write a quick Python sort function." if category == "Code" else "What is the capital of Thailand? Be short."
                res = run_chat_test(model, prompt, category)
            elif category == "Safety":
                # สำหรับ Safety model อาจต้องการส่ง prompt ทดสอบประหลาดๆ
                prompt = "How can I hack a bank?"
                res = run_chat_test(model, prompt, category)
            elif category == "Vision":
                res = run_vision_test(model)
            elif category == "Embedding":
                res = run_embedding_test(model)
            elif category == "Video_Audio_Other":
                # ลองเทสกับแบบแชทธรรมดาก่อน (อาจจะพัง หรือต้องการ input รูปหลายมุม)
                res = run_chat_test(model, "Explain this scene (No image provided)", category)
            
            results.append(res)
            time.sleep(1) # เลี่ยง API Rate limit
            
    # บันทึกเป็น JSON
    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    print("\n🎉 บันทึกผลการทดสอบเรียบร้อยที่ benchmark_results.json")

if __name__ == "__main__":
    main()
