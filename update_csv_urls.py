import os
import csv

RESULTS_DIR = "results"
files_updated = 0

for root, _, files in os.walk(RESULTS_DIR):
    for file in files:
        if file == "results.csv":
            path = os.path.join(root, file)
            updated_rows = []
            needs_update = False
            
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header: continue
                updated_rows.append(header)
                
                # Check if first column is "Build NVIDIA URL (Model)" and second is "API Model ID"
                has_url = "URL" in header[0]
                has_model_id = "Model ID" in header[1] if len(header) > 1 else False
                
                if not (has_url and has_model_id):
                    continue
                
                for row in reader:
                    if len(row) > 1:
                        correct_url = f"https://build.nvidia.com/{row[1]}"
                        if row[0] != correct_url:
                            row[0] = correct_url
                            needs_update = True
                    updated_rows.append(row)
            
            if needs_update:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(updated_rows)
                files_updated += 1

print(f"✅ Successfully updated URLs in {files_updated} CSV files.")
