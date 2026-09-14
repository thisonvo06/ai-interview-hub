import os
import sys
import json
import time
import base64
import urllib.request
import subprocess
import asyncio
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_DIR = os.path.abspath("docs/ui-audit/before")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Login tokens
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)

tok_student = client.post("/api/v1/auth/login", json={"account": "student@example.com", "password": "123456"}).json()["data"]
tok_hr = client.post("/api/v1/auth/login", json={"account": "hr@example.com", "password": "123456"}).json()["data"]

student_info = {
    "id": tok_student["user_id"],
    "email": "student@example.com",
    "account_type": "PERSONAL",
    "roles": ["PERSONAL_USER"],
    "name": "张同学",
    "avatar_url": None,
    "company_id": None
}

hr_info = {
    "id": tok_hr["user_id"],
    "email": "hr@example.com",
    "account_type": "ENTERPRISE",
    "roles": ["RECRUITER"],
    "name": "华为招聘HR",
    "avatar_url": None,
    "company_id": tok_hr["company_id"]
}

PAGES = [
    {
        "id": "01",
        "name": "01-home.png",
        "url": "http://localhost:5173/",
        "auth": None
    },
    {
        "id": "02",
        "name": "02-job-market.png",
        "url": "http://localhost:5173/jobs",
        "auth": None
    },
    {
        "id": "03",
        "name": "03-job-detail.png",
        "url": "http://localhost:5173/jobs/1",
        "auth": None
    },
    {
        "id": "04",
        "name": "04-login.png",
        "url": "http://localhost:5173/login",
        "auth": None
    },
    {
        "id": "05",
        "name": "05-register.png",
        "url": "http://localhost:5173/register",
        "auth": None
    },
    {
        "id": "06",
        "name": "06-personal-dashboard.png",
        "url": "http://localhost:5173/personal/dashboard",
        "auth": ("student", tok_student["access_token"], student_info)
    },
    {
        "id": "07",
        "name": "07-ai-interview.png",
        "url": "http://localhost:5173/personal/interviews/1/room",
        "auth": ("student", tok_student["access_token"], student_info)
    },
    {
        "id": "08",
        "name": "08-interview-report.png",
        "url": "http://localhost:5173/interviews/1/report",
        "auth": ("student", tok_student["access_token"], student_info)
    },
    {
        "id": "09",
        "name": "09-enterprise-dashboard.png",
        "url": "http://localhost:5173/enterprise/dashboard",
        "auth": ("hr", tok_hr["access_token"], hr_info)
    }
]

async def capture_all():
    port = 9333
    user_data = os.path.abspath("backend/scratch/chrome_audit_profile_9333")
    os.makedirs(user_data, exist_ok=True)
    
    # Launch Chrome
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data}",
        "--headless=new",
        "--disable-gpu",
        "--disable-extensions",
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1440,900"
    ])

    await asyncio.sleep(2)

    try:
        # Get websocket URL for actual page
        tabs_url = f"http://127.0.0.1:{port}/json"
        req = urllib.request.urlopen(tabs_url)
        tabs = json.loads(req.read().decode())
        page_tabs = [t for t in tabs if t.get("type") == "page"]
        if not page_tabs:
            print("No page tab found, creating one...")
            new_tab_url = f"http://127.0.0.1:{port}/json/new"
            req2 = urllib.request.urlopen(new_tab_url)
            page_tabs = [json.loads(req2.read().decode())]
        
        ws_url = page_tabs[0]["webSocketDebuggerUrl"]
        print(f"Connecting to CDP: {ws_url}")

        async with websockets.connect(ws_url, max_size=25_000_000) as ws:
            msg_id = 1

            async def send(method, params=None):
                nonlocal msg_id
                mid = msg_id
                msg_id += 1
                payload = {"id": mid, "method": method, "params": params or {}}
                await ws.send(json.dumps(payload))
                while True:
                    raw = await ws.recv()
                    resp = json.loads(raw)
                    if resp.get("id") == mid:
                        return resp

            await send("Page.enable")
            await send("Runtime.enable")
            await send("Emulation.setDeviceMetricsOverride", {
                "width": 1440,
                "height": 900,
                "deviceScaleFactor": 1,
                "mobile": False
            })

            for page in PAGES:
                p_name = page["name"]
                p_url = page["url"]
                print(f"Auditing page: {p_name} -> {p_url}", flush=True)

                # Set or clear localStorage
                if page["auth"]:
                    role_type, token, uinfo = page["auth"]
                    await send("Page.navigate", {"url": "http://localhost:5173/"})
                    await asyncio.sleep(0.8)
                    js_set = f"""
                    localStorage.setItem('zh_access_token', '{token}');
                    localStorage.setItem('zh_user_info', JSON.stringify({json.dumps(uinfo)}));
                    """
                    await send("Runtime.evaluate", {"expression": js_set})
                else:
                    await send("Page.navigate", {"url": "http://localhost:5173/"})
                    await asyncio.sleep(0.4)
                    js_clear = "localStorage.clear();"
                    await send("Runtime.evaluate", {"expression": js_clear})

                # Navigate to target page
                await send("Page.navigate", {"url": p_url})
                await asyncio.sleep(2.5)

                # Capture screenshot
                shot_resp = await send("Page.captureScreenshot", {"format": "png"})
                if "result" in shot_resp and "data" in shot_resp["result"]:
                    img_data = base64.b64decode(shot_resp["result"]["data"])
                    out_file = os.path.join(OUTPUT_DIR, p_name)
                    with open(out_file, "wb") as f:
                        f.write(img_data)
                    print(f"Saved: {out_file} ({len(img_data)} bytes)", flush=True)
                else:
                    print(f"Failed to capture: {p_name}", flush=True)

    finally:
        chrome_proc.terminate()

if __name__ == "__main__":
    asyncio.run(capture_all())
