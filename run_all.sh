#!/bin/bash
echo "🚀 Starting Full Benchmark for 189 models across all categories..."

echo "--------------------------------------------------------"
uv run python test_vision.py

echo "--------------------------------------------------------"
uv run python test_code.py

echo "--------------------------------------------------------"
uv run python test_embedding.py

echo "--------------------------------------------------------"
uv run python test_safety.py

echo "--------------------------------------------------------"
uv run python test_video_other.py

echo "--------------------------------------------------------"
uv run python test_text.py

echo "--------------------------------------------------------"
echo "🎵 Testing Audio (gRPC) Models..."
uv run python test_audio_grpc.py

echo "--------------------------------------------------------"
echo "🖼️ Testing Image/3D/Video Generation Models..."
uv run python test_image_video_gen.py

echo "--------------------------------------------------------"
echo "📊 Compiling Master CSV Catalog..."
uv run python generate_master_csv.py

echo "✅ All tests completed! Check the 'master_models_catalog.csv' for the final aggregated catalog."
