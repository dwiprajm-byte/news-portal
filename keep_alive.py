import threading
import time
import requests

def ping_loop():
    url = "https://24earlynews.com"
    while True:
        try:
            time.sleep(600)
            res = requests.get(url, timeout=10)
            print(f"[Keep-Alive] Pinged {url} -> {res.status_code}")
        except Exception as err:
            print(f"[Keep-Alive] Error: {err}")

threading.Thread(target=ping_loop, daemon=True).start()
