import time
from utils import client, get_categorized_models, init_csv, append_csv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

def run():
    csv_file = "results/Embedding/results.csv"
    init_csv(csv_file, ["API Latency (s)", "Dimension", "Error"])
    
    # เชื่อมต่อกับ Qdrant
    try:
        qdrant = QdrantClient("http://localhost:6333")
    except Exception as e:
        print(f"⚠️ ไม่สามารถเชื่อมต่อ Qdrant ได้: {e}")
        qdrant = None
        
    models = get_categorized_models().get("Embedding", [])
    print(f"🔍 ทดสอบหมวด Embedding ({len(models)} โมเดล) พร้อมบันทึกเวกเตอร์ลง Qdrant")
    
    texts = ["AI is evolving rapidly.", "NVIDIA NIM provides serverless inferencing."]
    
    for model in models:
        print(f"Testing: {model}...")
        try:
            extra_args = {}
            name_lower = model.lower()
            if "nv-embed" in name_lower or "nemoretriever" in name_lower or "nemotron-embed" in name_lower or "parse" in name_lower:
                extra_args["extra_body"] = {"input_type": "query"}
                
            api_start = time.time()
            res = client.embeddings.create(input=texts, model=model, encoding_format="float", **extra_args)
            api_time = time.time() - api_start
            
            dim = len(res.data[0].embedding)
            
            # บันทึกลง Qdrant
            if qdrant:
                # ตั้งชื่อ Collection ให้ตรงกับชื่อโมเดล (ปรับตัวอักษรให้รองรับ Qdrant)
                collection_name = model.replace("/", "_").replace("-", "_")
                
                # เช็คว่ามี Collection หรือยัง ถ้ายังไม่มีก็สร้างใหม่โดยอ้างอิง Dimension ปัจจุบัน
                if not qdrant.collection_exists(collection_name):
                    qdrant.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                    )
                
                # นำข้อมูล Vector Insert เข้า Collection
                points = []
                for i, record in enumerate(res.data):
                    points.append(PointStruct(
                        id=str(uuid.uuid4()), 
                        vector=record.embedding, 
                        payload={"text": texts[i], "model": model}
                    ))
                    
                qdrant.upsert(
                    collection_name=collection_name,
                    points=points
                )
                print(f"  ✅ Saved {len(points)} vectors to Qdrant collection: {collection_name}")
                
            append_csv(csv_file, model, "Success", [f"{api_time:.4f}", dim, "-"])
        except Exception as e:
            err = str(e).replace("\n", " | ")
            print(f"  ❌ Failed: {err}")
            append_csv(csv_file, model, "Failed", ["-", "-", err])

if __name__ == "__main__":
    run()
