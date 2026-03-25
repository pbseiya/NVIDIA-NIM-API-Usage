import os
import time
import json
import base64
import requests
from dotenv import load_dotenv
from utils import init_csv, append_csv

# นำเข้า API Key จากไฟล์ .env
load_dotenv()
api_key = os.getenv("NVIDIA_NIM_API")

if not api_key:
    raise ValueError("ไม่พบ NVIDIA_NIM_API ใน .env")

# สร้างโฟลเดอร์สำหรับเก็บภาพ/CSV
output_dir = "results/Media"
os.makedirs(output_dir, exist_ok=True)
csv_file = os.path.join(output_dir, "results.csv")

# รายชื่อโมเดลสร้างรูปภาพ/วิดีโอชื่อดังบน NVIDIA NIM พร้อม Endpoint ของตัวเอง
media_models = [
    {"name": "stabilityai/stable-diffusion-3-medium", "url": "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-3-medium", "type": "image"},
    {"name": "stabilityai/sdxl-turbo", "url": "https://ai.api.nvidia.com/v1/genai/stabilityai/sdxl-turbo", "type": "image"},
    {"name": "black-forest-labs/flux.1-schnell", "url": "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-schnell", "type": "image"},
    {"name": "black-forest-labs/flux.1-dev", "url": "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-dev", "type": "image"},
    {"name": "nvidia/edify", "url": "https://ai.api.nvidia.com/v1/genai/nvidia/edify", "type": "image"},
    {"name": "stabilityai/stable-video-diffusion", "url": "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-video-diffusion", "type": "video"},
    {"name": "kling", "url": "https://ai.api.nvidia.com/v1/genai/kling", "type": "video"},
    {"name": "nvidia/trellis", "url": "https://ai.api.nvidia.com/v1/genai/nvidia/trellis", "type": "3d"},
    {"name": "nvidia/latte3d", "url": "https://ai.api.nvidia.com/v1/genai/nvidia/latte3d", "type": "3d"},
    {"name": "nvidia/edify-3d", "url": "https://ai.api.nvidia.com/v1/genai/nvidia/edify-3d", "type": "3d"}
]

def get_payload(model_name, mtype):
    base_prompt = "A futuristic cyber-cat wearing neon glasses, highly detailed 8k rendering"
    if mtype == "video":
        return {"image": "base64_placeholder", "seed": 0, "cfg_scale": 1.8}
    elif mtype == "3d":
        return {"prompt": base_prompt} 
    else:
        # Custom image payloads
        if "stable-diffusion-3" in model_name or "sdxl" in model_name:
            if "sdxl-turbo" in model_name:
                return {
                    "prompt": base_prompt,
                    "seed": 0,
                    "steps": 4
                }
            return {
                "prompt": base_prompt,
                "cfg_scale": 5,
                "aspect_ratio": "16:9",
                "seed": 42,
                "steps": 40,
                "negative_prompt": ""
            }
        elif "flux" in model_name:
            return {
                "prompt": base_prompt,
                "seed": 42,
                "steps": 4 if "schnell" in model_name else 25
            }
        else:
            return {
                "prompt": base_prompt
            }

def decode_and_save(base64_string, filepath):
    # ถอดรหัส base64 กลับเป็นไบต์ และบันทึกลงไฟล์
    image_data = base64.b64decode(base64_string)
    with open(filepath, "wb") as f:
        f.write(image_data)

def test_media_generation():
    print(f"🎨 เริ่มการทดสอบ Media Generation ({len(media_models)} โมเดล)")
    print(f"เตรียมจัดเก็บไฟล์ในโฟลเดอร์: {output_dir}\n")
    
    # สร้าง CSV หัวตารางหลัก
    init_csv(csv_file, ["Latency (s)", "Media Type", "Error"])
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    for model in media_models:
        model_name = model["name"]
        mtype = model.get("type", "image")
        print(f"Generating media with: {model_name}...")
        
        start_time = time.time()
        try:
            payload = get_payload(model_name, mtype)
            response = requests.post(model["url"], headers=headers, json=payload)
            response.raise_for_status() # โยน Exception ถ้า HTTP Code ไม่ใช่ 200
            
            res_json = response.json()
            latency = time.time() - start_time
            
            # NVIDIA API มักคืนรูปภาพ Base64 มาในฟิลด์ "image" หรือ "artifacts"[0].base64
            b64_data = None
            if "image" in res_json:
                b64_data = res_json["image"]
            elif "artifacts" in res_json and len(res_json["artifacts"]) > 0:
                b64_data = res_json["artifacts"][0].get("base64")
                
            if b64_data:
                safe_name = model_name.replace("/", "_") + ".png"
                output_path = os.path.join(output_dir, safe_name)
                decode_and_save(b64_data, output_path)
                print(f"✅ Success! Latency: {latency:.2f}s | Saved to: {output_path}\n")
                append_csv(csv_file, model_name, "Success", [f"{latency:.2f}", mtype, "-"])
            else:
                print(f"⚠️ Failed: ไม่พบข้อมูล Base64 ใน Response ของ {model_name}\n")
                append_csv(csv_file, model_name, "Failed", ["-", mtype, "No Base64 data returned"])
                
        except Exception as e:
            # ดัก 404, 403, 401 และ 422 ให้แสดงอ่านง่าย พร้อมพิมพ์ Response Body สำหรับ Debug
            err_msg = str(e).replace("\n", " | ")
            response_body = ""
            if hasattr(e, 'response') and e.response is not None:
                response_body = f" | Response Body: {e.response.text}"
            
            if "403" in err_msg or "404" in err_msg or "401" in err_msg:
                err_msg += " (Model requires an Enterprise specific entitlement on your NVIDIA account)"
            elif "422" in err_msg:
                err_msg += f" (Payload format mismatch{response_body})"
            elif "500" in err_msg:
                err_msg += f" (Internal Error (API Gateway issue or Invalid payload format){response_body})"
            
            print(f"❌ Failed: {err_msg}\n")
            append_csv(csv_file, model_name, "Failed", ["-", mtype, err_msg])
            
if __name__ == "__main__":
    test_media_generation()
