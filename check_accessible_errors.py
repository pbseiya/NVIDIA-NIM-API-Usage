import os
import csv

def find_accessible_errors():
    base_dir = "results"
    categories = ["Vision", "Code", "Embedding", "Safety", "Video_Other", "Text"]
    
    total_found = 0
    accessible_errors = {}
    
    for cat in categories:
        csv_path = os.path.join(base_dir, cat, "results.csv")
        if not os.path.exists(csv_path):
            continue
            
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if not headers:
                continue
                
            for row in reader:
                if len(row) < 3:
                    continue
                model_name = row[1]
                status = row[2]
                error = row[-1]
                
                # Check if Failed but NOT a permission issue
                if "Failed" in status and "404 Not Found" not in error and "Not found for account" not in error:
                    if cat not in accessible_errors:
                        accessible_errors[cat] = []
                    accessible_errors[cat].append((model_name, error))
                    total_found += 1
                    
    print("\n--- 🔎 โมเดลที่ 'เข้าถึงได้' แต่ยังมี Error อยู่ ---\n")
    if total_found == 0:
        print("✅ แจ่มมาก! ตอนนี้ไม่มีโมเดลไหนที่คุณเข้าถึงได้แล้วเด้ง Error เลย ทุกตัว Success หมดแล้วครับ")
    else:
        for cat, errors in accessible_errors.items():
            print(f"[{cat}] พบ {len(errors)} โมเดลที่มีปัญหา:")
            for m, err in errors:
                print(f"  ❌ {m}: {err}")
            print("")
            
if __name__ == "__main__":
    find_accessible_errors()
