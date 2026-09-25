# SEPHORiA London resale watcher

Checks the official resale page every ~10 minutes and pings your phone when
tickets may be available or the page changes. It does **not** buy tickets —
you tap the notification and check out yourself.

## 1. Get alerts on your phone (2 minutes)
1. Install the free **ntfy** app (iOS / Android).
2. Tap **+ Subscribe** and invent a long, hard-to-guess topic name,
   e.g. `sephoria-yourname-8k3x9q`. Anyone who knows it can see alerts, so keep it private.

## 2. Run it free in the cloud with GitHub (10 minutes)
1. Create a free account at github.com.
2. Create a new **public** repository (public repos get unlimited free Actions minutes).
3. Upload all files from this folder, keeping the `.github/workflows/` folder structure.
4. Go to **Settings → Secrets and variables → Actions → New repository secret**.
   Name: `NTFY_TOPIC`, Value: your topic name from step 1.
5. Go to the **Actions** tab, enable workflows if asked, open
   "SEPHORiA resale watcher" and click **Run workflow** to test it.

The first run saves a baseline; after that you'll get alerts on changes.

## Alternative: run on your own computer
```
pip install -r requirements.txt
python -m playwright install chromium
export NTFY_TOPIC=your-topic-name       # Windows: set NTFY_TOPIC=your-topic-name
python monitor.py --test-alert           # confirm your phone gets a ping
python monitor.py --loop 5               # check every 5 minutes
```
Your computer needs to stay on and awake for this to work.

## When the event is over
Delete the repository (or disable the workflow) — resale closes 15 Oct at 6pm.
