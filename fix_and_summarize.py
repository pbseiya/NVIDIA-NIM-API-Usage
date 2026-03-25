import os
import csv

def summarize():
    base_dir = "results"
    categories = ["Vision", "Code", "Embedding", "Safety", "Video_Other", "Text"]
    
    summary_report = "# 🚨 สรุปโมเดลที่ยังพบข้อผิดพลาด (Failed Models)\n\n"
    summary_report += "จากการรันชุดทดสอบ พบโมเดลที่ติด Error จากระบบ API ของ NVIDIA ดังนี้ (ได้ทำการปรับปรุงข้อความ Error ในไฟล์ CSV ให้กระชับอ่านง่ายขึ้นแล้ว):\n\n"
    
    total_errors = 0
    
    for cat in categories:
        csv_path = os.path.join(base_dir, cat, "results.csv")
        if not os.path.exists(csv_path):
            continue
            
        rows = []
        errors_in_cat = []
        
        # อ่านไฟล์
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if not headers:
                continue
                
            for row in reader:
                if len(row) < 3:
                    continue
                status = row[2]
                model_name = row[1]
                
                # ถ้า Failed
                if "Failed" in status:
                    error_msg = row[-1]
                    
                    # แปลงข้อความให้กระชับลงใน CSV
                    if "404" in error_msg:
                        error_msg = "404 Not Found (Missing API Permission / Gated Model)"
                    elif "500" in error_msg or "Internal" in error_msg:
                        error_msg = "500 Internal Error (Gateway Issue / Payload Mismatch)"
                    elif "input_type" in error_msg:
                        error_msg = "400 Bad Request (Requires specific 'input_type' payload)"
                    elif "Empty response" in error_msg:
                        error_msg = "Model generated empty response"
                        
                    row[-1] = error_msg
                    errors_in_cat.append((model_name, error_msg))
                    
                rows.append(row)
                
        # อัพเดทเขียนทับ CSV เดิมด้วยข้อความที่ ক্লিনแล้ว
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
            
        # เติมลงใน Report
        if errors_in_cat:
            summary_report += f"## 🔹 กลุ่ม {cat} ({len(errors_in_cat)} โมเดล)\n"
            for model, err in errors_in_cat:
                summary_report += f"- **`{model}`**: {err}\n"
            summary_report += "\n"
            total_errors += len(errors_in_cat)
            
    if total_errors == 0:
        summary_report += "✅ ไม่พบโมเดลที่มี Error เลยในขณะนี้!"
    else:
        summary_report += f"---\n**รวมทั้งหมด:** {total_errors} โมเดลที่เข้าถึงไม่ได้ผ่านชุดคำสั่งมาตรฐาน"

    # เขียนลงไฟล์ Report
    with open("error_summary.md", "w", encoding="utf-8") as f:
        f.write(summary_report)
    print("Done generating error_summary.md")

if __name__ == "__main__":
    summarize()
