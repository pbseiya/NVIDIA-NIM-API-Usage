import os
import csv
import urllib.request
from urllib.error import URLError, HTTPError
import concurrent.futures

RESULTS_DIR = "results"
urls_to_test = set()

for root, _, files in os.walk(RESULTS_DIR):
    for file in files:
        if file == "results.csv":
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header: continue
                # find URL column
                url_idx = -1
                for i, col in enumerate(header):
                    if "URL" in col or col == "Build NVIDIA URL (Model)":
                        url_idx = i
                        break
                if url_idx == -1:
                    # In audio tests, maybe url isn't the first col, let's just check all cols
                    # Wait, Audio results don't have URL col! 
                    continue
                
                for row in reader:
                    if len(row) > url_idx:
                        urls_to_test.add(row[url_idx])

print(f"Total unique URLs to test: {len(urls_to_test)}")

def check_url(url):
    # Some URLs might be "N/A"
    if not url.startswith("http"):
        return url, False, "Invalid Format"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req, timeout=5)
        if response.status == 200:
            return url, True, "200 OK"
        return url, False, f"Status: {response.status}"
    except HTTPError as e:
        return url, False, f"HTTP Error {e.code}"
    except URLError as e:
        return url, False, f"URL Error: {e.reason}"
    except Exception as e:
        return url, False, str(e)

bad_urls = []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(check_url, urls_to_test)
    for url, ok, msg in results:
        if not ok:
            bad_urls.append((url, msg))

print(f"Found {len(bad_urls)} broken URLs out of {len(urls_to_test)}.")
with open("broken_urls.txt", "w") as f:
    for u, m in bad_urls:
        f.write(f"{u} => {m}\n")
        print(f"BROKEN: {u} => {m}")

if len(bad_urls) == 0:
    print("✅ All URLs are valid!")
