import time
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = "9240133902:AAEeLcTrMRJpplBBlRrNRxjHFwEDKS5ctlY"
CHAT_ID = "5813357047"
SITE_URL = "https://winningcircle.io" + "/panel/canlicuzdan"

OTURUM_JSON = '''BURAYA_OTURUM_ANAHTARINI_YAPISTIR'''

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Aktif")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

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
    if "Giriş bilgilerinizi doldurunuz" in metin:
        return None, "OTURUM_DUSTU", metin[:300]
    
    satirlar = [s.strip() for s in metin.splitlines() if s.strip()]
    acik_islemler = []
    aktif_cuzdan = "Genel"
    
    for i, satir in enumerate(satirlar):
        if "geçmiş işlem" in satir.lower():
            break
            
        if satir in ["Efe Bulduk", "Oslo Bot"] or ("Bot" in satir and len(satir) < 25):
            aktif_cuzdan = satir
            
        if "-USDT" in satir.upper() and len(satir) < 20:
            coin = satir.upper()
            yon = ""
            giris = ""
            for j in range(i, min(i + 15, len(satirlar))):
                if satirlar[j].upper() in ["LONG", "SHORT"]:
                    yon = satirlar[j].upper()
                if satirlar[j].upper() == "GİRİŞ" and j + 1 < len(satirlar):
                    giris = satirlar[j + 1]
            kayit = f"👤 {aktif_cuzdan} | 🪙 {coin} | 📊 {yon} | 💰 Giriş: {giris}"
            if kayit not in acik_islemler:
                acik_islemler.append(kayit)
                
    return acik_islemler, "OK", metin[:450]

with sync_playwright() as p:
    b = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
    )
    context = b.new_context()
    
    try:
        veri = json.loads(OTURUM_JSON)
        if veri.get("ck"):
            cerezler = []
            for parca in veri["ck"].split(";"):
                if "=" in parca:
                    k, v = parca.strip().split("=", 1)
                    cerezler.append({"name": k, "value": v, "domain": ".winningcircle.io", "path": "/"})
            if cerezler:
                context.add_cookies(cerezler)
        if veri.get("ls"):
            ls_script = "".join([f"localStorage.setItem({json.dumps(k)}, {json.dumps(v)});" for k, v in veri["ls"].items()])
            context.add_init_script(ls_script)
    except Exception as e:
        print("Oturum yukleme hatasi:", e)

    page = context.new_page()
    page.goto(SITE_URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(12)
    page.reload(wait_until="domcontentloaded", timeout=60000)
    time.sleep(15)
    
    okunanlar, durum, onizleme = islemleri_oku(page)
    
    if durum == "OTURUM_DUSTU":
        gonder("⚠️ Oturum açılmadı (Giriş ekranında kaldı)! Oturum anahtarını güncellememiz gerekiyor.")
        bilinen_islemler = set()
    else:
        bilinen_islemler = set(okunanlar)
        if bilinen_islemler:
            mevcut_liste = "\n".join(bilinen_islemler)
            gonder(f"✅ WinningCircle 7/24 Takip Başladı!\n\nŞu Anki Açık İşlemler:\n{mevcut_liste}")
        else:
            gonder(f"⚠️ Açık işlem bulunamadı. Botun sayfada gördüğü metin:\n\n{onizleme}")

    while True:
        try:
            page.reload(wait_until="domcontentloaded", timeout=60000)
            time.sleep(15)
            guncel_liste, durum, _ = islemleri_oku(page)
            
            if durum == "OK":
                guncel_set = set(guncel_liste)
                for islem in guncel_set:
                    if islem not in bilinen_islemler:
                        gonder(f"🚨 YENİ SİNYAL / İŞLEM AÇILDI!\n\n{islem}\n\n🔗 {SITE_URL}")
                
                for eski_islem in bilinen_islemler:
                    if eski_islem not in guncel_set:
                        gonder(f"🛑 İŞLEM KAPATILDI!\n\n{eski_islem}\n\n🔗 {SITE_URL}")
                bilinen_islemler = guncel_set
        except Exception as e:
            print("Kontrol hatasi:", e)
        time.sleep(20)
