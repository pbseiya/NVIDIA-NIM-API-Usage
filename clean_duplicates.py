import os
import csv

def clean_csvs():
    base_dir = "results"
    categories = ["Vision", "Code", "Embedding", "Safety", "Video_Other", "Text", "Media"]
    
    for cat in categories:
        csv_path = os.path.join(base_dir, cat, "results.csv")
        if not os.path.exists(csv_path):
            continue
            
        # ใช้ Dictionary จัดเก็บ row ล่าสุดของแต่ละ model
        model_latest_row = {}
        headers = []
        
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if not headers:
                continue
            
            for row in reader:
                if len(row) < 3:
                    continue
                model_name = row[1]
                model_latest_row[model_name] = row
                
        # อัพเดทกลับลงไปเฉพาะการทดสอบล่าสุดเท่านั้น
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(model_latest_row.values())
            
    print(" cleaned up duplicate rows in all CSV files.")

if __name__ == "__main__":
    clean_csvs()
