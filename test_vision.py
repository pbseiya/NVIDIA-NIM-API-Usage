import time
import base64
import requests
from utils import client, get_categorized_models, init_csv, append_csv

def get_base64_image(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch image. Status: {response.status_code}")
    encoded = base64.b64encode(response.content).decode('utf-8')
    mime_type = response.headers.get('content-type', 'image/jpeg')
    if not mime_type.startswith('image/'):
        mime_type = 'image/jpeg'
    return f"data:{mime_type};base64,{encoded}"

def run():
    csv_file = "results/Vision/results.csv"
    init_csv(csv_file, ["TTFT (s)", "TPS (tokens/s)", "Total Tokens", "Error"])
    
    models = get_categorized_models().get("Vision", [])
    print(f"👁️ ทดสอบหมวด Vision ({len(models)} โมเดล)")
    
    img_url = "https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg"
    try:
        print("Downloading test image and encoding to Base64...")
        b64_image = get_base64_image(img_url)
    except Exception as e:
        print(f"Failed to fetch image: {e}")
        return

    for model in models:
        print(f"Testing: {model}...")
        max_retries = 3
        for attempt in range(max_retries):
            start_time = time.time()
            try:
                # ใช้ Base64 เพื่อป้องกัน Internal Server Error (500) จากปัญหาฝั่งเซิร์ฟเวอร์ดึง URL รูป
                response = client.chat.completions.create(
                    model=model,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe the main color of this cat briefly."},
                            {"type": "image_url", "image_url": {"url": b64_image}}
                        ]
                    }],
                    max_tokens=50,
                    stream=True,
                    temperature=0.1
                )
                
                first_token_time = None
                token_count = 0
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        if first_token_time is None:
                            first_token_time = time.time()
                        token_count += 1
                        
                end_time = time.time()
                if first_token_time:
                    ttft = first_token_time - start_time
                    gen_time = end_time - first_token_time
                    tps = token_count / gen_time if gen_time > 0 else 0
                    append_csv(csv_file, model, "Success", [f"{ttft:.4f}", f"{tps:.2f}", token_count, "-"])
                else:
                    append_csv(csv_file, model, "Failed: No Content", ["-", "-", "-", "Empty response"])
                break # Success, exit retry loop
                    
            except Exception as e:
                err = str(e).replace("\n", " | ")
                # 404 ปกติแปลว่าโดนบล็อคสิทธิ์ หรือโมเดลนั้นเรียกผ่าน HTTP API ไม่ได้
                if "404" in err:
                    err = "404 Not Found (Model requires specific enterprise access or different endpoint)"
                
                err_lower = err.lower()
                retriable = any(x in err_lower for x in ["504", "500", "503", "429", "timeout", "peer closed", "empty response", "chunked"])
                if retriable and attempt < max_retries - 1:
                    sleep_time = 2 ** attempt
                    print(f"⚠️ [Retry {attempt+1}/{max_retries}] Intermittent error: {err[:60]}... Waiting {sleep_time}s")
                    time.sleep(sleep_time)
                else:
                    print(f"  ❌ Failed: {err}")
                    append_csv(csv_file, model, "Failed", ["-", "-", "-", err])
                    break # Stop retrying

if __name__ == "__main__":
    run()
