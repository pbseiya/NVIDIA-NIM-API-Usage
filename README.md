# NVIDIA NIM & Alibaba Qwen: Model Benchmarking & Cataloging

ระบบทดสอบประสิทธิภาพ (Benchmarking), ตรวจสอบ (Validation), และจัดทำสารบัญ (Cataloging) สำหรับโมเดล AI ในกลุ่ม NVIDIA NIM และ Alibaba Cloud (Qwen) โดยเน้นความเสถียร ระบบ Auto-Retry และการสร้างเนื้อหาขนาดยาว (Novel Generation)

---

## 🚀 การติดตั้งและเตรียมความพร้อม (Setup)

โปรเจกต์นี้จัดการด้วย `uv` สำหรับ Environment และ Dependencies

1. **เตรียมไฟล์ `.env`**:
   สร้างไฟล์ `.env` ที่ Root Directory และใส่ API Keys ดังนี้:
   ```bash
   NVIDIA_NIM_API=nvapi-... (คีย์จาก NVIDIA Build)
   ALIBABA_API_KEY=sk-sp-... (คีย์จาก Alibaba Model Studio - Global/Singapore)
   ```

2. **ติดตั้ง Dependencies**:
   ```bash
   uv sync
   ```

---

## 🛠️ วิธีการใช้งานสคริปต์ (.py)

### 1. การ Benchmark ตามหมวดหมู่ (Modalities)
คุณสามารถรันการทดสอบแยกตามประเภทของโมเดลได้:

*   **Text Models**: ทดสอบ LLM มาตรฐาน (Llama, Mistral, Qwen)
    ```bash
    uv run python test_text.py
    ```
*   **Vision Models**: ทดสอบโมเดลประมวลผลภาพ (VLM) โดยใช้ Base64 Payload
    ```bash
    uv run python test_vision.py
    ```
*   **Audio Models (gRPC)**: ทดสอบ STT/TTS ผ่านโปรโตคอล gRPC (Canary, Parakeet)
    ```bash
    uv run python test_audio_grpc.py
    ```
*   **Media Generation**: ทดสอบโมเดลสร้างภาพและวิดีโอ (SD3, Flux.1)
    ```bash
    uv run python test_image_video_gen.py
    ```

---

## 📊 การอ่านค่าผลลัพธ์ (.csv)

### 1. Master Catalog (สารบัญรวมแม่ข่าย)
ไฟล์สารบัญหลักจะถูกสร้างและอัปเดตโดยสคริปต์ [**`generate_master_csv.py`**](file:///home/pongsak/projects/nvidia-mim/generate_master_csv.py) ซึ่งจะรวบรวมผลลัพธ์จากการทดสอบ API ทุกตัวมาไว้ที่เดียว

*   **ไฟล์**: [**`master_models_catalog.csv`**](file:///home/pongsak/projects/nvidia-mim/master_models_catalog.csv)
*   **รายละเอียดข้อมูล (Columns):**
    *   `Model Name`: ชื่อโมเดลที่ใช้เรียกผ่าน API
    *   `Modality`: ประเภทข้อมูล (Text, Vision, Audio, Media Generation)
    *   `Sub-Category`: รายละเอียดเจาะจง (เช่น Image/Video Understanding, TTS, STT)
    *   `Status`: สถานะปัจจุบัน (Success / Failed)
    *   `Error Detail`: สาเหตุที่ Error (เช่น 404 Gated Model, Deprecated)
    *   `Metrics`: ประสิทธิภาพจริงที่วัดได้
        *   **TTFT (s)**: ความเร็วในการตอบสนองคำแรก (Time to First Token)
        *   **TPS**: ความเร็วในการส่งข้อมูลต่อเนื่อง (Tokens Per Second)
    *   `Build NVIDIA URL`: ลิงค์ตรงไปยังหน้า Catalog ของ NVIDIA เพื่อดูเอกสารเพิ่มเติม
    *   `API Payload Example`: ตัวอย่าง JSON Payload ที่ใช้ยิงจริง (สามารถ Copy ไปใส่ใน Postman หรือ Code ของคุณได้เลย)
    *   `Reasoning`: ติดแท็ก **(Reasoning)** สำหรับโมเดลที่มีความสามารถในการคิดวิเคราะห์สูง (เช่น DeepSeek-R1, O1)

---

## 2. รายละเอียดแยกหมวดหมู่ (Raw Results)
หากต้องการดู Log การรันดิบแยกตามประเภท สามารถดูได้ในโฟลเดอร์ `results/`:
*   `results/Text/results.csv`: รายชื่อและผล Test ของ LLM ทั้งหมด
*   `results/Vision/results.csv`: ผลการทดสอบโมเดลประมวลผลคลิปและภาพ
*   `results/Audio/results.csv`: ผลการทดสอบโมเดลแปลงเสียงเป็นข้อความและข้อความเป็นเสียง
*   `results/MediaGen/results.csv`: ผลการทดสอบการสร้างรูปภาพจากข้อความ (Text-to-Image)

---

## 3. การสร้างนิยายขนาดยาว (Novel Generation)
เรามีระบบ **Auto-Continue** เพื่อก้าวข้ามขีดจำกัด Timeout 2 นาทีของ API:

*   **NVIDIA Version** (ใช้ Qwen 397B):
    ```bash
    uv run python generate_novel.py
    ```
*   **Alibaba Version** (ใช้ Qwen-Plus/3.5-Plus):
    ```bash
    uv run python generate_novel_alibaba.py
    ```
    *ผลลัพธ์จะถูกบันทึกเป็นไฟล์ `.docx` พร้อมจัดรูปแบบสีสันสวยงามแยกตามผู้พูด ความยาวเฉลี่ย 11,000 - 12,000 คำไทย*

---

## 🔧 ระบบการจัดการข้อผิดพลาด (Error Handling)

*   **Auto-Retry**: สคริปต์ Benchmark ส่วนใหญ่จะทำการรันซ้ำอัตโนมัติ (Exponential Backoff) เมื่อเจอ Error 504 (Gateway Timeout) หรือ 500 (Internal Error)
*   **Model Is Deprecated**: หากเจอข้อความนี้ หมายความว่า NVIDIA ถอดโมเดลนั้นออกจากระบบแล้ว (รันไม่ได้)
*   **404 Not Found (Gated)**: หมายถึงโมเดลนั้นต้องมีการขอสิทธิ์ใช้งานเพิ่ม (Enterprise Enrollment) หรือคีย์ API ไม่มีสิทธิ์เข้าถึง (ไม่สามารถแก้ด้วยโค้ดได้)

---

## 📝 ลำดับการรันทั้งหมด (Global Run)
หากต้องการรันการทดสอบและสรุปผลใหม่ทั้งหมดในครั้งเดียว:
```bash
bash run_all.sh
```
สคริปต์นี้จะไล่รัน Text -> Vision -> Audio -> MediaGen และปิดท้ายด้วยการสร้าง Master CSV ครับ
