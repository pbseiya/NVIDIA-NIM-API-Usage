import os
import csv
import json

RESULTS_DIR = "results"
MASTER_CSV = "master_models_catalog.csv"

def get_modality_and_payload(category, model_name):
    cat_lower = category.lower()
    
    # default to text/text
    input_mod = "text"
    output_mod = "text"
    
    is_reasoning = any(k in model_name.lower() for k in ["r1", "reasoning", "math", "phi-4-mini-flash-reasoning"])
    reasoning_tag = " (Reasoning)" if is_reasoning else ""

    if cat_lower == "vision":
        input_mod = "text, image"
        if "streampetr" in model_name.lower():
            input_mod = "text, video, image"
        return ("Image/Video Understanding" + reasoning_tag, input_mod, output_mod,
                "test_vision.py",
                '{"messages": [{"role": "user", "content": [{"type": "text", "text": "What is in this image?"}, {"type": "image_url", "image_url": {"url": "data:image/png;base64,...(b64 string)..."}}]}]}')
    elif cat_lower == "audio":
        if "tts" in model_name.lower():
            return ("Text-to-Speech (TTS)" + reasoning_tag, "text", "audio", "test_audio_grpc.py", 'gRPC: riva.client.SynthesizeSpeechRequest(text="Hello", language_code="en-US")')
        else:
            return ("Automatic Speech Recognition (ASR)" + reasoning_tag, "audio", "text", "test_audio_grpc.py", 'gRPC: riva.client.RecognizeRequest(audio_content=bytes, config=...)')
    elif cat_lower == "media":
        if "video" in model_name.lower():
            return ("Video Generation" + reasoning_tag, "text, image", "video", "test_image_video_gen.py", '{"model": "' + model_name + '", "prompt": "A cinematic shot...", "cfg_scale": 7.0}')
        elif "3d" in model_name.lower():
            return ("3D Generation" + reasoning_tag, "text, image", "3d", "test_image_video_gen.py", '{"prompt": "A 3D character..."}')
        else:
            return ("Image Generation" + reasoning_tag, "text", "image", "test_image_video_gen.py", '{"prompt": "A beautiful landscape", "steps": 50, "seed": 42}')
    elif cat_lower == "code":
        return ("Code Generation" + reasoning_tag, "text", "text", "test_code.py", '{"messages": [{"role": "user", "content": "Write a python function for fibonacci"}]}')
    elif cat_lower == "embedding":
        return ("Vector Embeddings" + reasoning_tag, "text", "vector", "test_embedding.py", '{"input": ["Sentence to embed"], "input_type": "query"}')
    elif cat_lower == "safety":
        return ("Content Safety / Guardrails" + reasoning_tag, "text", "text (safety rating)", "test_safety.py", '{"messages": [{"role": "user", "content": "How to hack a bank?"}]}')
    else:
        # Text/Chat
        if "moe" in model_name.lower() or "mixtral" in model_name.lower():
            subtype = "Text / Chat (MoE)"
        else:
            subtype = "Text / Chat"
        return (subtype + reasoning_tag, "text", "text", "test_text.py", '{"messages": [{"role": "user", "content": "Tell me a joke."}], "max_tokens": 512}')

def parse_deprecated(model_name):
    deps = ["neva", "nvclip", "vila"]
    for d in deps:
        if d in model_name.lower():
            return "Yes"
    return "No"

def main():
    rows = []
    
    headers = [
        "Model Name", "Category", "Modality Type", "Input Modalities", "Output Modalities", 
        "Is Deprecated?", "Status", "Error Info", "Benchmark Type", "Benchmark Result", 
        "Example API Payload", "Example Code File", "NVIDIA NIM URL", "API Model ID"
    ]
    rows.append(headers)
    
    for root, _, files in os.walk(RESULTS_DIR):
        for file in files:
            if file == "results.csv":
                category = os.path.basename(root)
                path = os.path.join(root, file)
                
                with open(path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    file_header = next(reader, None)
                    if not file_header: continue
                    
                    for row in reader:
                        # Extract basic info depending on column length
                        if len(row) >= 7 and "URL" in file_header[0]:
                            url = row[0]
                            api_id = row[1]
                            model_name = row[2]
                            row_cat = category
                            status = row[4]
                            latency = row[5]
                            extra = row[6]
                            
                            # Different benchmark types
                            if category == "Audio":
                                bench_type = "Latency (s)"
                                bench_val = latency
                                error_info = "-" if status == "Success" else extra
                            elif category == "Media":
                                bench_type = "Generation Time (s)"
                                bench_val = latency
                                error_info = "-" if status == "Success" else extra
                            elif category == "Embedding":
                                bench_type = "Latency (s)"
                                bench_val = latency
                                error_info = "-" if status == "Success" else extra
                            else:
                                # Text, Vision, Code, Safety have TTFT, TPS, Tokens, Error
                                if len(row) >= 8: # actually in updated we have Build URL(0), API ID(1), Status(2), TTFT(3), TPS(4), Tokens(5), Error(6)
                                    # Wait, my update_csv_urls.py didn't shift columns, it just replaced col 0.
                                    pass
                        
                        # Let's extract carefully by trying to match header names
                        row_dict = dict(zip(file_header, row))
                        
                        # Fallbacks
                        url = row_dict.get("Build NVIDIA URL (Model)", "")
                        api_id = row_dict.get("API Model ID", "")
                        
                        if not api_id: 
                            if len(row) > 1 and "/" in row[1]: api_id = row[1]
                            elif "/" in row[0]: api_id = row[0]
                            
                        # Model Name is sometimes derived from API ID
                        model_name = row_dict.get("Model Name", api_id.split("/")[-1] if "/" in api_id else api_id)
                        
                        status = row_dict.get("Status", "Unknown")
                        
                        bench_type = "TTFT / TPS"
                        bench_val = "-"
                        error_info = "-"
                        
                        if category in ["Audio"]:
                            bench_type = "Latency (s)"
                            bench_val = row_dict.get("Latency (s)", "-")
                            if status != "Success":
                                error_info = row_dict.get("Result/Transcript", "-")
                        elif category in ["Media"]:
                            bench_type = "Generation Time (s)"
                            bench_val = row_dict.get("Latency (s)", "-")
                            if status != "Success":
                                error_info = row_dict.get("Error", "-")
                        elif category in ["Embedding"]:
                            bench_type = "Latency (s)"
                            bench_val = row_dict.get("Latency (s)", "-")
                            if status != "Success":
                                error_info = row_dict.get("Error", "-")
                        else:
                            ttft = row_dict.get("TTFT (s)", "-")
                            tps = row_dict.get("TPS (tokens/s)", "-")
                            err = row_dict.get("Error", "-")
                            if status == "Success":
                                bench_val = f"TTFT: {ttft}s, TPS: {tps}"
                            else:
                                error_info = err
                                
                        is_dep = parse_deprecated(model_name)
                        if is_dep == "Yes" and error_info != "-":
                            error_info = "Model is Deprecated (No longer available)"
                            
                        modality, in_mod, out_mod, code_file, payload = get_modality_and_payload(category, model_name)
                        
                        rows.append([
                            model_name, category, modality, in_mod, out_mod, is_dep, status,
                            error_info, bench_type, bench_val, payload, code_file, url, api_id
                        ])
                        
    with open(MASTER_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
        
    print(f"✅ Generated {MASTER_CSV} with {len(rows)-1} models.")

if __name__ == "__main__":
    main()
