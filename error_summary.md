# 🚨 สรุปโมเดลที่ยังพบข้อผิดพลาด (Failed Models)

จากการรันชุดทดสอบ พบโมเดลที่ติด Error จากระบบ API ของ NVIDIA ดังนี้ (ได้ทำการปรับปรุงข้อความ Error ในไฟล์ CSV ให้กระชับอ่านง่ายขึ้นแล้ว):

## 🔹 กลุ่ม Vision (4 โมเดล)
- **`microsoft/phi-3-vision-128k-instruct`**: 404 Not Found (Missing API Permission / Gated Model)
- **`nvidia/neva-22b`**: 404 Not Found (Missing API Permission / Gated Model)
- **`nvidia/nvclip`**: 404 Not Found (Missing API Permission / Gated Model)
- **`nvidia/vila`**: 404 Not Found (Missing API Permission / Gated Model)

## 🔹 กลุ่ม Code (10 โมเดล)
- **`bigcode/starcoder2-15b`**: 404 Not Found (Missing API Permission / Gated Model)
- **`bigcode/starcoder2-7b`**: 404 Not Found (Missing API Permission / Gated Model)
- **`deepseek-ai/deepseek-coder-6.7b-instruct`**: 404 Not Found (Missing API Permission / Gated Model)
- **`google/codegemma-1.1-7b`**: 404 Not Found (Missing API Permission / Gated Model)
- **`google/codegemma-7b`**: 404 Not Found (Missing API Permission / Gated Model)
- **`ibm/granite-34b-code-instruct`**: 404 Not Found (Missing API Permission / Gated Model)
- **`ibm/granite-8b-code-instruct`**: 404 Not Found (Missing API Permission / Gated Model)
- **`meta/codellama-70b`**: 404 Not Found (Missing API Permission / Gated Model)
- **`mistralai/codestral-22b-instruct-v0.1`**: 404 Not Found (Missing API Permission / Gated Model)
- **`nvidia/usdcode-llama-3.1-70b-instruct`**: 404 Not Found (Missing API Permission / Gated Model)

## 🔹 กลุ่ม Embedding (6 โมเดล)
- **`nvidia/embed-qa-4`**: 404 Not Found (Missing API Permission / Gated Model)
- **`nvidia/llama-3.2-nv-embedqa-1b-v1`**: 404 Not Found (Missing API Permission / Gated Model)
- **`nvidia/nemoretriever-parse`**: 404 Not Found (Missing API Permission / Gated Model)
- **`nvidia/nemotron-parse`**: 404 Not Found (Missing API Permission / Gated Model)
- **`nvidia/nv-embedqa-mistral-7b-v2`**: 404 Not Found (Missing API Permission / Gated Model)
- **`snowflake/arctic-embed-l`**: 404 Not Found (Missing API Permission / Gated Model)

## 🔹 กลุ่ม Safety (1 โมเดล)
- **`nvidia/nemotron-4-340b-reward`**: 404 Not Found (Missing API Permission / Gated Model)

## 🔹 กลุ่ม Video_Other (1 โมเดล)
- **`nvidia/streampetr`**: 404 Not Found (Missing API Permission / Gated Model)

## 🔹 กลุ่ม Text (17 โมเดล)
- **`01-ai/yi-large`**: 404 Not Found (Missing API Permission / Gated Model)
- **`adept/fuyu-8b`**: 404 Not Found (Missing API Permission / Gated Model)
- **`ai21labs/jamba-1.5-large-instruct`**: 404 Not Found (Missing API Permission / Gated Model)
- **`aisingapore/sea-lion-7b-instruct`**: 404 Not Found (Missing API Permission / Gated Model)
- **`baai/bge-m3`**: 404 Not Found (Missing API Permission / Gated Model)
- **`bytedance/seed-oss-36b-instruct`**: Model generated empty response
- **`databricks/dbrx-instruct`**: 404 Not Found (Missing API Permission / Gated Model)
- **`deepseek-ai/deepseek-r1-distill-qwen-14b`**: peer closed connection without sending complete message body (incomplete chunked read)
- **`deepseek-ai/deepseek-r1-distill-qwen-32b`**: peer closed connection without sending complete message body (incomplete chunked read)
- **`deepseek-ai/deepseek-r1-distill-qwen-7b`**: peer closed connection without sending complete message body (incomplete chunked read)
- **`google/deplot`**: 404 Not Found (Missing API Permission / Gated Model)
- **`google/gemma-2b`**: 404 Not Found (Missing API Permission / Gated Model)
- **`google/paligemma`**: 500 Internal Error (Gateway Issue / Payload Mismatch)
- **`google/recurrentgemma-2b`**: 404 Not Found (Missing API Permission / Gated Model)
- **`ibm/granite-3.0-3b-a800m-instruct`**: 404 Not Found (Missing API Permission / Gated Model)
- **`ibm/granite-3.0-8b-instruct`**: 404 Not Found (Missing API Permission / Gated Model)
- **`ibm/granite-3.3-8b-instruct`**: Error code: 504

## 🔹 กลุ่ม Media Generation (10 โมเดล)
- **สเปกตรัมที่ใช้งานได้:**
    - ✅ **`stabilityai/stable-diffusion-3-medium`**: สำเร็จ (Fixed 422 Payload)
    - ✅ **`black-forest-labs/flux.1-dev`**: สำเร็จ (Fixed 422/500 Issues)
- **สเปกตรัมที่ติดปัญหา:**
    - `stabilityai/sdxl-turbo`: 404 Not Found (Missing API Permission)
    - `nvidia/edify`, `stable-video-diffusion`, `kling`, `trellis`, `latte3d`, `edify-3d`: 404 Not Found (Missing API Permission)

---
**รวมทั้งหมด:** 46 โมเดลที่เข้าถึงไม่ได้ หรือต้องใช้สิทธิ์ Enterprise ในการเรียกใช้งานสถาปัตยกรรมแบบพิเศษครับ (Vision, Media, Embedding)