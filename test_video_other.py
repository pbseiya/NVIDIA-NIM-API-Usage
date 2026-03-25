import time
from utils import client, get_categorized_models, init_csv, append_csv

def run():
    csv_file = "results/Video_Other/results.csv"
    init_csv(csv_file, ["TTFT (s)", "TPS (tokens/s)", "Total Tokens", "Error"])
    
    models = get_categorized_models().get("Video_Other", [])
    print(f"🎬 ทดสอบหมวด Video / Other ({len(models)} โมเดล)")
    
    prompt = "Analyze this video input. (Placeholder text)"
    
    for model in models:
        print(f"Testing: {model}...")
        start_time = time.time()
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=30,
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
        except Exception as e:
            err = str(e).replace("\n", " | ")
            append_csv(csv_file, model, "Failed", ["-", "-", "-", err])

if __name__ == "__main__":
    run()
