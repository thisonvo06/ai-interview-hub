import os
import sys
import json
import urllib.request
import subprocess
import asyncio
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

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

URLS_TO_TEST = [
    # Public
    ("/", None),
    ("/jobs", None),
    ("/jobs/1", None),
    ("/companies/1", None),
    ("/features", None),
    ("/about", None),
    ("/help", None),
    ("/login", None),
    ("/register", None),
    # Personal
    ("/personal/dashboard", ("student", tok_student["access_token"], student_info)),
    ("/personal/jobs", ("student", tok_student["access_token"], student_info)),
    ("/personal/applications", ("student", tok_student["access_token"], student_info)),
    ("/personal/resumes", ("student", tok_student["access_token"], student_info)),
    ("/personal/resumes/1/edit", ("student", tok_student["access_token"], student_info)),
    ("/personal/resumes/1/analysis", ("student", tok_student["access_token"], student_info)),
    ("/personal/assessment", ("student", tok_student["access_token"], student_info)),
    ("/personal/interviews", ("student", tok_student["access_token"], student_info)),
    ("/personal/interviews/create", ("student", tok_student["access_token"], student_info)),
    ("/personal/interviews/1/room", ("student", tok_student["access_token"], student_info)),
    ("/interviews/1/report", ("student", tok_student["access_token"], student_info)),
    ("/personal/growth", ("student", tok_student["access_token"], student_info)),
    ("/personal/learning", ("student", tok_student["access_token"], student_info)),
    ("/personal/notifications", ("student", tok_student["access_token"], student_info)),
    ("/personal/profile", ("student", tok_student["access_token"], student_info)),
    ("/personal/settings", ("student", tok_student["access_token"], student_info)),
    # Enterprise
    ("/enterprise/dashboard", ("hr", tok_hr["access_token"], hr_info)),
    ("/enterprise/jobs", ("hr", tok_hr["access_token"], hr_info)),
    ("/enterprise/jobs/create", ("hr", tok_hr["access_token"], hr_info)),
    ("/enterprise/jobs/1/edit", ("hr", tok_hr["access_token"], hr_info)),
    ("/enterprise/candidates", ("hr", tok_hr["access_token"], hr_info)),
    ("/enterprise/candidates/1", ("hr", tok_hr["access_token"], hr_info)),
    ("/enterprise/pipeline", ("hr", tok_hr["access_token"], hr_info)),
    ("/enterprise/interviews", ("hr", tok_hr["access_token"], hr_info)),
    ("/enterprise/talent-pool", ("hr", tok_hr["access_token"], hr_info)),
    ("/enterprise/analytics", ("hr", tok_hr["access_token"], hr_info)),
    ("/enterprise/members", ("hr", tok_hr["access_token"], hr_info)),
    ("/enterprise/settings", ("hr", tok_hr["access_token"], hr_info)),
]

async def audit_network_console():
    port = 9444
    user_data = os.path.abspath("backend/scratch/chrome_audit_profile_9444")
    os.makedirs(user_data, exist_ok=True)
    
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
    audit_summary = []

    try:
        tabs_url = f"http://127.0.0.1:{port}/json"
        req = urllib.request.urlopen(tabs_url)
        tabs = json.loads(req.read().decode())
        page_tabs = [t for t in tabs if t.get("type") == "page"]
        ws_url = page_tabs[0]["webSocketDebuggerUrl"]

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
            await send("Network.enable")
            await send("Log.enable")

            for path, auth_tuple in URLS_TO_TEST:
                full_url = f"http://localhost:5173{path}"

                if auth_tuple:
                    role_type, token, uinfo = auth_tuple
                    await send("Page.navigate", {"url": "http://localhost:5173/"})
                    await asyncio.sleep(0.3)
                    js_set = f"""
                    localStorage.setItem('zh_access_token', '{token}');
                    localStorage.setItem('zh_user_info', JSON.stringify({json.dumps(uinfo)}));
                    """
                    await send("Runtime.evaluate", {"expression": js_set})
                else:
                    await send("Page.navigate", {"url": "http://localhost:5173/"})
                    await asyncio.sleep(0.2)
                    await send("Runtime.evaluate", {"expression": "localStorage.clear();"})

                # Navigate
                await send("Page.navigate", {"url": full_url})
                await asyncio.sleep(1.8)

                # Check page title and DOM for errors
                eval_res = await send("Runtime.evaluate", {"expression": "document.title"})
                title = eval_res.get("result", {}).get("value", "")

                # Check if StateContainer error or 404 is showing
                has_404 = await send("Runtime.evaluate", {"expression": "document.body.innerText.includes('404')"})
                is_404 = has_404.get("result", {}).get("value", False)
                has_error = await send("Runtime.evaluate", {"expression": "document.body.innerText.includes('数据加载失败')"})
                is_err = has_error.get("result", {}).get("value", False)
                has_empty = await send("Runtime.evaluate", {"expression": "document.body.innerText.includes('暂无')"})
                is_empty = has_empty.get("result", {}).get("value", False)

                res_item = {
                    "path": path,
                    "title": title,
                    "is_404": is_404,
                    "has_error_state": is_err,
                    "has_empty_state": is_empty
                }
                audit_summary.append(res_item)
                print(f"[{'FAIL' if is_404 or is_err else 'OK'}] {path} -> 404:{is_404}, err:{is_err}, empty:{is_empty}", flush=True)

        with open("backend/scratch/route_audit_summary.json", "w", encoding="utf-8") as f:
            json.dump(audit_summary, f, ensure_ascii=False, indent=2)

    finally:
        chrome_proc.terminate()

if __name__ == "__main__":
    asyncio.run(audit_network_console())
