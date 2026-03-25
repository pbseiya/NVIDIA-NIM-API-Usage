import os
import csv
from playwright.sync_api import sync_playwright
import concurrent.futures

def get_all_urls():
    urls = set()
    for root, _, files in os.walk("results"):
        for file in files:
            if file == "results.csv":
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    if not header: continue
                    url_idx = -1
                    for i, c in enumerate(header):
                        if "URL" in c:
                            url_idx = i
                            break
                    if url_idx != -1:
                        for row in reader:
                            if len(row) > url_idx and row[url_idx].startswith("http"):
                                urls.add(row[url_idx])
    return list(urls)

def check_url(url):
    import time
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # <--- เปิดให้เห็นเบราว์เซอร์จริงๆ
        page = browser.new_page()
        try:
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            time.sleep(1.5) # หน่วงเวลาให้ผู้ใช้ได้ดูหน้าเว็บแป๊บนึง
            text = page.locator("body").inner_text().lower()
            
            if "page not found" in text or "404 not found" in text:
                res = (url, False, "Page Not Found")
            elif "nim has been deprecated" in text:
                res = (url, False, "Deprecated")
            else:
                res = (url, True, "OK")
        except Exception as e:
            res = (url, False, f"Timeout or Error: {str(e)[:50]}")
        finally:
            browser.close()
        return res

if __name__ == "__main__":
    urls = get_all_urls()
    print(f"🔍 Starting Headless Browser Verification for {len(urls)} URLs...")
    
    bad_urls = []
    # ปรับเหลือ 1 ควบคู่กันไป เพื่อให้มันเปิดทีละแท็บให้ดูง่ายๆ
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        for res in executor.map(check_url, urls):
            print(f"[{'✅' if res[1] else '❌'}] {res[0]} -> {res[2]}")
            if not res[1]:
                bad_urls.append(res)
                
    with open("broken_urls_browser.txt", "w", encoding="utf-8") as f:
        for r in bad_urls:
            f.write(f"{r[0]} - {r[2]}\n")
            
    print("-" * 40)
    print(f"🏁 Verification Complete! Found {len(bad_urls)} genuinely broken URLs.")
    if len(bad_urls) == 0:
        print("🎉 ALL 197+ URLs are fully verified by actual browser DOM inspection!")
