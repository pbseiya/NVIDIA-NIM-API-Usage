import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("NVIDIA_NIM_API")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

def categorize():
    try:
        models = client.models.list()
        model_names = sorted([model.id for model in models.data])
    except Exception as e:
        print(f"Error fetching models: {e}")
        return

    categories = {
        "🧠 Text Generation (Chat / Instruct)": [],
        "💻 Code Generation": [],
        "👁️ Vision / Image (VLM)": [],
        "🔍 Embedding / Retrieval": [],
        "🛡️ Safety / Reward (Guard)": [],
        "🎬 Video / 3D / Audio / Other": []
    }

    for name in model_names:
        name_lower = name.lower()
        
        # Guard / Reward
        if "guard" in name_lower or "reward" in name_lower or "safety" in name_lower:
            categories["🛡️ Safety / Reward (Guard)"].append(name)
        # Embedding / Retrieval
        elif "embed" in name_lower or "rerank" in name_lower or "retriever" in name_lower or "parse" in name_lower:
            categories["🔍 Embedding / Retrieval"].append(name)
        # Vision
        elif "vl" in name_lower or "vision" in name_lower or "neva" in name_lower or "vila" in name_lower or "pixtral" in name_lower or "clip" in name_lower:
            categories["👁️ Vision / Image (VLM)"].append(name)
        # Code
        elif "code" in name_lower or "coder" in name_lower or "sql" in name_lower:
            categories["💻 Code Generation"].append(name)
        # Video/Audio/Other
        elif "video" in name_lower or "audio" in name_lower or "streampetr" in name_lower:
            categories["🎬 Video / 3D / Audio / Other"].append(name)
        # Text
        else:
            categories["🧠 Text Generation (Chat / Instruct)"].append(name)

    # Write to Markdown
    with open("categorized_models.md", "w", encoding="utf-8") as f:
        f.write(f"# 📋 รายชื่อโมเดลทั้งหมดแยกตามประเภท (총 {len(model_names)} โมเดล)\n\n")
        f.write("ข้อมูลดึงจาก `https://integrate.api.nvidia.com/v1/models`\n\n")
        
        for cat, items in categories.items():
            f.write(f"## {cat} ({len(items)} โมเดล)\n")
            for item in items:
                f.write(f"- `{item}`\n")
            f.write("\n")
            
    print("Done. Saved to categorized_models.md")

if __name__ == "__main__":
    categorize()
