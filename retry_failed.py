import time
import requests
import base64
from utils import client

def get_base64_image(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    encoded = base64.b64encode(response.content).decode('utf-8')
    return f"data:image/jpeg;base64,{encoded}"

def retry_run():
    print("🔄 กำลังรีทาย 6 โมเดลที่เข้าถึงได้แต่ Error")
    models_to_test = [
        "google/paligemma",
        "bytedance/seed-oss-36b-instruct",
        "deepseek-ai/deepseek-r1-distill-qwen-14b",
        "deepseek-ai/deepseek-r1-distill-qwen-32b",
        "deepseek-ai/deepseek-r1-distill-qwen-7b",
        "ibm/granite-3.3-8b-instruct"
    ]
    
    img_url = "https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg"
    b64_image = get_base64_image(img_url)
    
    for model in models_to_test:
        print(f"\nTesting: {model}...")
        try:
            if "paligemma" in model.lower():
                payload = [
                    {"type": "text", "text": "Describe this image."},
                    {"type": "image_url", "image_url": {"url": b64_image}}
                ]
            else:
                payload = [{"type": "text", "text": "Hello, write a short poem about a cat."}]
                
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": payload}],
                max_tokens=30,
                stream=False,
                temperature=0.7
            )
            
            # Since stream=False, response is parsed straight
            repl = response.choices[0].message.content
            print(f"✅ Success! Length of response: {len(str(repl))} chars")
            print(f"Snippet: {str(repl)[:50]}...")
            
        except Exception as e:
            print(f"❌ Still Failed: {str(e)}")

if __name__ == "__main__":
    retry_run()
