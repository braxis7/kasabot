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

def islemleri_oku(page):
    metin = page.locator("body").inner_text()
    satirlar = [s.strip() for s in metin.splitlines() if s.strip()]
    islemler = []
    aktif_cuzdan = "Genel"
    
    for i, satir in enumerate(satirlar):
        if satir in ["Efe Bulduk", "Oslo Bot"] or "Bot" in satir:
            aktif_cuzdan = satir
        if satir == "TICKER" and i + 1 < len(satirlar):
            coin = satirlar[i + 1]
            yon = ""
            giris = ""
            for j in range(i, min(i + 10, len(satirlar))):
                if satirlar[j] in ["LONG", "SHORT"]:
                    yon = satirlar[j]
                if satirlar[j] == "GİRİŞ" and j + 1 < len(satirlar):
                    giris = satirlar[j + 1]
            islemler.append(f"👤 {aktif_cuzdan} | 🪙 {coin} | 📊 {yon} | 💰 Giriş: {giris}")
    return islemler

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page()
    page.goto(SITE_URL, wait_until="networkidle")
    time.sleep(5)
    
    bilinen_islemler = set(islemleri_oku(page))
    mevcut_liste = "\n".join(bilinen_islemler) if bilinen_islemler else "Henüz açık işlem okunamadı."
    gonder(f"✅ WinningCircle Akıllı Takip Başladı!\n\nŞu Anki Açık İşlemler:\n{mevcut_liste}")

    while True:
        try:
            page.reload(wait_until="networkidle")
            time.sleep(4)
            guncel_islemler = islemleri_oku(page)
            for islem in guncel_islemler:
                if islem not in bilinen_islemler:
                    gonder(f"🚨 YENİ SİNYAL / İŞLEM TESPİT EDİLDİ!\n\n{islem}\n\n🔗 {SITE_URL}")
                    bilinen_islemler.add(islem)
            # Kapanan işlemler olursa hafızadan temizle ki tekrar açılırsa bildirim gelsin
            bilinen_islemler = set(guncel_islemler)
        except Exception as e:
            print("Kontrol hatasi:", e)
        time.sleep(15)
