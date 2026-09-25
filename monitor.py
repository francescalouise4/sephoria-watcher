"""
SEPHORiA London resale watcher.
Loads the official Weezevent resale page, and sends a push notification
(via ntfy.sh) when tickets look available or when the page content changes.

Usage:
  python monitor.py            # check once (used by GitHub Actions)
  python monitor.py --loop 5   # check every 5 minutes (run on your own computer)
"""
import argparse, hashlib, os, re, sys, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

RESALE_URL = "https://widget.weezevent.com/ticket/resale-sephoria-london-2026?locale=en-gb"
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")        # your private topic name
STATE_FILE = Path(os.environ.get("STATE_FILE", "state.txt"))

# Phrases that suggest nothing is on sale right now
EMPTY_HINTS = ["sold out", "no ticket", "not available", "unavailable", "complet", "épuisé"]


def notify(title: str, message: str, priority: str = "urgent"):
    if not NTFY_TOPIC:
        print(f"[no NTFY_TOPIC set] {title}: {message}")
        return
    req = urllib.request.Request(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={"Title": title, "Priority": priority, "Tags": "ticket,sparkles",
                 "Click": RESALE_URL},
    )
    urllib.request.urlopen(req, timeout=20)


def fetch_page_text() -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(RESALE_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)  # let the widget finish rendering
        text = page.inner_text("body")
        browser.close()
    # Normalise whitespace and strip things like timers that change every load
    text = re.sub(r"\d{1,2}:\d{2}(:\d{2})?", "", text)
    return re.sub(r"\s+", " ", text).strip()


def looks_available(text: str) -> bool:
    lower = text.lower()
    has_price = "£" in text
    says_empty = any(h in lower for h in EMPTY_HINTS)
    return has_price and not says_empty


def check_once():
    text = fetch_page_text()
    digest = hashlib.sha256(text.encode()).hexdigest()
    previous = STATE_FILE.read_text().strip() if STATE_FILE.exists() else ""
    print(f"Fetched {len(text)} chars. Snippet: {text[:300]!r}")

    if looks_available(text):
        notify("🎟️ SEPHORiA resale tickets may be available!",
               "Tap to open the official resale page and check out quickly.")
    elif previous and digest != previous:
        notify("SEPHORiA resale page changed",
               "Something changed on the resale page. Worth a quick look!", priority="high")
    elif not previous:
        print("First run: baseline saved, no alert sent.")

    STATE_FILE.write_text(digest)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--loop", type=float, help="minutes between checks")
    ap.add_argument("--test-alert", action="store_true", help="send a test notification")
    args = ap.parse_args()

    if args.test_alert:
        notify("Test alert", "Your SEPHORiA watcher is set up correctly 🎉", priority="default")
        sys.exit(0)
    if args.loop:
        while True:
            try:
                check_once()
            except Exception as e:
                print("Check failed:", e)
            time.sleep(args.loop * 60)
    else:
        check_once()
