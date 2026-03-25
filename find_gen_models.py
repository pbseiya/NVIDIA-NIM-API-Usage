from utils import client
import json

def find_gen_models():
    models = client.models.list()
    keywords = ['diffusion', 'sdxl', 'edify', 'gen', 'image', 'video', '3d', 'audio', 'seed', 'streampetr']
    gen_models = []
    
    for m in models.data:
        name = m.id.lower()
        if any(kw in name for kw in keywords):
            gen_models.append(m.id)
            
    print("Found potential generative models:")
    for gm in gen_models:
        print(f"- {gm}")

if __name__ == "__main__":
    find_gen_models()
