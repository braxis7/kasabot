import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = "9240133902:AAEeLcTrMRJpplBBlRrNRxjHFwEDKS5ctlY"
CHAT_ID = "5813357047"
SITE_URL = "https://winningcircle.io" + "/panel/canlicuzdan"

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Aktif")

def web_sunucusu():
    HTTPServer(("0.0.0.0", 8000), HealthHandler).serve_forever()

threading.Thread(target=web_sunucusu, daemon=True).start()

def gonder(msg):
    u = "https://api.telegram." + "org/bot" + BOT_TOKEN + "/sendMessage"
    try:
        requests.post(u, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("Hata:", e)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page()
    page.goto(SITE_URL, wait_until="networkidle")
    time.sleep(5)
    son = ""
    gonder("✅ WinningCircle Botu 7/24 Bulut Sunucuda Baslatildi!")
    while True:
        try:
            page.reload(wait_until="networkidle")
            time.sleep(3)
            satirlar = page.locator("table tbody tr").all_inner_texts()
            guncel = satirlar.strip() if len(satirlar) > 0 else page.locator("main").inner_text().strip()[:400]
            if guncel and guncel != son:
                if son != "":
                    gonder("🚨 Yeni Cuzdan Islemi!\n\n" + guncel + "\n\n" + SITE_URL)
                son = guncel
        except Exception as e:
            print("Kontrol hatasi:", e)
        time.sleep(15)
