import grpc
import os
import time
import csv
import wave
from dotenv import load_dotenv
import riva.client
import riva.client.proto.riva_asr_pb2 as rasr
import riva.client.proto.riva_asr_pb2_grpc as rasr_grpc
import riva.client.proto.riva_tts_pb2 as rtts
import riva.client.proto.riva_tts_pb2_grpc as rtts_grpc
from riva.client.proto import riva_audio_pb2

# Load environment
load_dotenv()
API_KEY = os.getenv("NVIDIA_NIM_API")
SERVER_URL = "grpc.nvcf.nvidia.com:443"

MODELS = [
    {"name": "canary-1b", "type": "ASR", "id": "b0e8b4a5-217c-40b7-9b96-17d84e666317", "mode": "offline", "api_id": "nvidia/canary-1b"},
    {"name": "parakeet-ctc-1.1b-asr", "type": "ASR", "id": "1598d209-5e27-4d3c-8079-4751568b1081", "mode": "offline", "api_id": "nvidia/parakeet-ctc-1_1b-asr"},
    {"name": "parakeet-ctc-0.6b-asr", "type": "ASR", "id": "d8dd4e9b-fbf5-4fb0-9dba-8cf436c8d965", "mode": "offline", "api_id": "nvidia/parakeet-ctc-0_6b-asr"},
    {"name": "parakeet-tdt-0.6b-v2", "type": "ASR", "id": "d3fe9151-442b-4204-a70d-5fcc597fd610", "mode": "offline", "api_id": "nvidia/parakeet-tdt-0_6b-v2"},
    {"name": "nemotron-asr-streaming", "type": "ASR", "id": "bb0837de-8c7b-481f-9ec8-ef5663e9c1fa", "mode": "streaming", "api_id": "nvidia/nemotron-asr-streaming"},
    {"name": "magpie-tts-multilingual", "type": "TTS", "id": "877104f7-e885-42b9-8de8-f6e4c6303969", "api_id": "nvidia/magpie-tts-multilingual"}
]

RESULTS_DIR = "results/Audio"
os.makedirs(RESULTS_DIR, exist_ok=True)
CSV_FILE = f"{RESULTS_DIR}/results.csv"

def get_metadata(function_id):
    return [
        ("authorization", f"Bearer {API_KEY}"),
        ("function-id", function_id)
    ]

def test_tts(model_info, text="Experience the future of speech AI with Riva - where every word comes to life."):
    print(f"🎤 Testing TTS: {model_info['name']}...")
    try:
        start_time = time.time()
        channel = grpc.secure_channel(SERVER_URL, grpc.ssl_channel_credentials())
        stub = rtts_grpc.RivaSpeechSynthesisStub(channel)
        
        request = rtts.SynthesizeSpeechRequest()
        request.text = text
        request.language_code = "en-US"
        request.encoding = riva_audio_pb2.LINEAR_PCM
        request.sample_rate_hz = 16000
        # Voice name found via browser
        request.voice_name = "Magpie-Multilingual.EN-US.Aria"
        
        response = stub.Synthesize(request, metadata=get_metadata(model_info['id']))
        
        output_path = f"{RESULTS_DIR}/{model_info['name'].replace('/', '_')}.wav"
        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(response.audio)
        
        latency = time.time() - start_time
        print(f"✅ TTS Success! Latency: {latency:.2f}s | Saved to {output_path}")
        return True, latency, f"Voice: Aria, Characters: {len(text)}"
    except Exception as e:
        print(f"❌ TTS Failed: {e}")
        return False, 0, str(e)

def test_asr_offline(model_info, wav_path):
    print(f"📝 Testing ASR (Offline): {model_info['name']}...")
    try:
        start_time = time.time()
        channel = grpc.secure_channel(SERVER_URL, grpc.ssl_channel_credentials())
        stub = rasr_grpc.RivaSpeechRecognitionStub(channel)
        
        with open(wav_path, "rb") as f:
            audio_data = f.read()
            
        config = rasr.RecognitionConfig(
            encoding=riva_audio_pb2.LINEAR_PCM,
            sample_rate_hertz=16000,
            language_code="en-US",
            max_alternatives=1,
            enable_automatic_punctuation=True
        )
        
        request = rasr.RecognizeRequest(config=config, audio=audio_data)
        response = stub.Recognize(request, metadata=get_metadata(model_info['id']))
        
        transcript = ""
        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            
        latency = time.time() - start_time
        print(f"✅ ASR Success! Latency: {latency:.2f}s | Transcript: {transcript}")
        return True, latency, transcript
    except Exception as e:
        print(f"❌ ASR Failed: {e}")
        return False, 0, str(e)

def test_asr_streaming(model_info, wav_path):
    print(f"🌊 Testing ASR (Streaming): {model_info['name']}...")
    try:
        start_time = time.time()
        channel = grpc.secure_channel(SERVER_URL, grpc.ssl_channel_credentials())
        stub = rasr_grpc.RivaSpeechRecognitionStub(channel)
        
        # Audio generator for streaming
        def generator():
            config = rasr.StreamingRecognitionConfig(
                config=rasr.RecognitionConfig(
                    encoding=riva_audio_pb2.LINEAR_PCM,
                    sample_rate_hertz=16000,
                    language_code="en-US",
                    max_alternatives=1,
                    enable_automatic_punctuation=True
                )
            )
            yield rasr.StreamingRecognizeRequest(streaming_config=config)
            
            with open(wav_path, "rb") as f:
                # Skip wav header (approx 44 bytes) for simple raw feed if needed, 
                # but usually Riva handles it or we should use raw pcm.
                data = f.read()
                chunk_size = 4096
                for i in range(0, len(data), chunk_size):
                    yield rasr.StreamingRecognizeRequest(audio_content=data[i:i+chunk_size])

        responses = stub.StreamingRecognize(generator(), metadata=get_metadata(model_info['id']))
        
        transcript = ""
        for response in responses:
            if response.results:
                for result in response.results:
                    if result.is_final:
                        transcript += result.alternatives[0].transcript
            
        latency = time.time() - start_time
        print(f"✅ Streaming ASR Success! Latency: {latency:.2f}s | Transcript: {transcript}")
        return True, latency, transcript
    except Exception as e:
        print(f"❌ Streaming ASR Failed: {e}")
        return False, 0, str(e)

def main():
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Build NVIDIA URL (Model)", "API Model ID", "Model Name", "Type", "Status", "Latency (s)", "Result/Transcript"])
        
        # 1. Run TTS first
        tts_model = next(m for m in MODELS if m["type"] == "TTS")
        success, latency, result = test_tts(tts_model)
        
        tts_url = f"https://build.nvidia.com/{tts_model['api_id']}"
        writer.writerow([tts_url, tts_model["api_id"], tts_model["name"], tts_model["type"], "Success" if success else "Failed", f"{latency:.2f}", result])
        
        if success:
            sample_wav = f"{RESULTS_DIR}/{tts_model['name'].replace('/', '_')}.wav"
            # 2. Run all ASR models
            for model in MODELS:
                if model["type"] == "ASR":
                    if model["mode"] == "streaming":
                        success, latency, result = test_asr_streaming(model, sample_wav)
                    else:
                        success, latency, result = test_asr_offline(model, sample_wav)
                    
                    url = f"https://build.nvidia.com/{model['api_id']}"
                    writer.writerow([url, model["api_id"], model["name"], model["type"], "Success" if success else "Failed", f"{latency:.2f}", result])
        else:
            print("Skipping ASR tests because TTS failed.")

if __name__ == "__main__":
    main()
