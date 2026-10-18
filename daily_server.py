"""
Dead Cells Daily Challenge Emulator Server
===========================================
Emulates Motion Twin's online backend for Dead Cells Daily Challenge / Leaderboard mode.
Runs locally at http://127.0.0.1:18050.

Author: whoami-28
Repository: https://github.com/whoami-28/daily-cells
Version: 1.0.0
"""

import http.server
import socketserver
import json
import datetime
import hashlib
import sys
import os
import time
import threading
import ctypes
import urllib.parse
from ctypes import wintypes

PORT = 18050
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs", "daily_server.log")
SCORES_FILE = os.path.join(BASE_DIR, "save", "daily_scores.json")

TH32CS_SNAPPROCESS = 0x00000002

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(wintypes.ULONG)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260)
    ]

def is_game_running():
    target_names = {b"deadcells.exe", b"deadcells_gl.exe"}
    hSnapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if hSnapshot == -1:
        return False
    entry = PROCESSENTRY32()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
    success = ctypes.windll.kernel32.Process32First(hSnapshot, ctypes.byref(entry))
    found = False
    while success:
        name = entry.szExeFile.lower()
        if name in target_names:
            found = True
            break
        success = ctypes.windll.kernel32.Process32Next(hSnapshot, ctypes.byref(entry))
    ctypes.windll.kernel32.CloseHandle(hSnapshot)
    return found

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def get_today_seed(date_str=None):
    if not date_str:
        date_str = datetime.date.today().isoformat()
    h = hashlib.md5(date_str.encode("utf-8")).hexdigest()
    seed = (int(h[:8], 16) % 899999) + 100000
    return date_str, seed

def load_saved_scores():
    try:
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        log(f"Error loading saved scores: {e}")
    return {}

def save_player_score(score, time_s=0):
    today, _ = get_today_seed()
    data = load_saved_scores()
    current = data.get(today, {}).get("score", 0)
    if score > current:
        data[today] = {
            "score": score,
            "time": time_s,
            "date": today,
            "name": "Beheaded",
            "uname": "Beheaded"
        }
        try:
            os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
            with open(SCORES_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            log(f"Saved new personal best: {score} pts (time: {time_s}s)")
        except Exception as e:
            log(f"Error saving score: {e}")

class DailyRunHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def handle_request(self, method):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""
        
        snippet = body[:200].decode("utf-8", errors="replace")
        log(f"Handling {method} {self.path} (Body size: {len(body)} bytes: {snippet})")

        path = self.path.split("?")[0]

        if path.startswith("/daily/seed"):
            today_str, seed = get_today_seed()
            saved_scores = load_saved_scores()
            today_entry = saved_scores.get(today_str, {
                "score": 0,
                "time": 0,
                "name": "Beheaded"
            })
            my_score = today_entry.get("score", 0)
            my_time = today_entry.get("time", 0)

            # Matches Dead Cells HashLink Type 1057:
            # ('date', String), ('index', Int), ('runId', String), ('seed', Int),
            # ('user', Type 1058), ('validVersion', Bool)
            resp = {
                "validVersion": True,
                "hasBug": False,
                "date": today_str,
                "index": 0,
                "runId": str(datetime.date.today().strftime("%Y%m%d")),
                "seed": seed,
                "user": {
                    "pos": 1,
                    "run": 0,
                    "score": my_score,
                    "state": 0,
                    "time": my_time
                },
                "run": {
                    "seed": seed,
                    "boss": False,
                    "bonus": 0,
                    "duration": 270
                },
                "daily": {
                    "seed": seed,
                    "boss": False,
                    "bonus": 0,
                    "duration": 270
                }
            }
            log(f"Delivering Daily Seed: {seed} for date {today_str}")
            self.send_json(resp)

        elif path.startswith("/daily/leaderboard"):
            rewind_days = 0
            try:
                if b"rewindDays=" in body:
                    for param in body.decode("utf-8", errors="ignore").split("&"):
                        if param.startswith("rewindDays="):
                            rewind_days = int(param.split("=")[1])
                            break
            except Exception:
                rewind_days = 0

            target_date = datetime.date.today() - datetime.timedelta(days=rewind_days)
            date_str = target_date.strftime("%Y-%m-%d")
            _, seed = get_today_seed(date_str)

            saved_scores = load_saved_scores()
            today_entry = saved_scores.get(date_str, {
                "score": 0,
                "time": 0,
                "name": "Beheaded"
            })

            my_score = today_entry.get("score", 0)
            my_time = today_entry.get("time", 0)

            # Matches Dead Cells HashLink Type 23710:
            # ('date', Float), ('isFriend', Bool), ('isMine', Bool), ('name', String),
            # ('pos', Int), ('run', Int), ('score', Int), ('state', Int), ('time', Int)
            entry = {
                "name": "Beheaded",
                "pos": 1,
                "rank": 1,
                "score": my_score,
                "time": my_time,
                "isMine": True,
                "isFriend": False,
                "date": float(time.time() * 1000.0),
                "run": 0,
                "state": 0,
                "user": "Beheaded",
                "uname": "Beheaded",
                "boss": False
            }

            # Matches Dead Cells HashLink Type 1275:
            # ('date', String), ('index', Int), ('scores', Array), ('seed', Int)
            resp = {
                "date": date_str,
                "index": 0,
                "seed": seed,
                "scores": [entry],
                "mine": entry,
                "total": 1,
                "hasMore": False,
                "rewindDays": rewind_days,
                "leaderboard": [entry],
                "status": "ok",
                "success": True
            }
            log(f"Delivering Leaderboard for {date_str} (score={my_score}, rewindDays={rewind_days})")
            self.send_json(resp)

        elif path.startswith("/daily/save"):
            log(f"Received /daily/save upload (size: {len(body)})")
            try:
                if body:
                    try:
                        data = json.loads(body.decode("utf-8", errors="replace"))
                    except Exception:
                        data = dict(urllib.parse.parse_qsl(body.decode("utf-8", errors="replace")))
                    score = int(data.get("score", 0))
                    time_s = int(data.get("time", 0))
                    save_player_score(score, time_s)
            except Exception as e:
                log(f"Error parsing save payload: {e}")
            self.send_json({"status": "ok", "success": True})

        elif path.startswith("/collect") or path.startswith("/stats/collect"):
            self.send_json({"status": "ok", "success": True})

        elif path.startswith("/streamer"):
            self.send_json({"status": "ok", "success": True})

        elif path.startswith("/lastNews"):
            self.send_json([])

        else:
            log(f"Fallback response for: {path}")
            self.send_json({"status": "ok", "success": True})

    def send_json(self, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def watchdog(server):
    log("Watchdog started. Waiting for Dead Cells process...")
    # Phase 1: Wait up to 60s for game to start
    started = False
    for _ in range(60):
        if is_game_running():
            started = True
            log("Dead Cells detected running!")
            break
        time.sleep(1)

    if not started:
        log("Dead Cells was not started within 60 seconds. Stopping server.")
        server.shutdown()
        return

    # Phase 2: Monitor until game exits
    while True:
        time.sleep(2)
        if not is_game_running():
            log("Dead Cells has exited. Shutting down emulator server.")
            server.shutdown()
            break

def main():
    log(f"=== Dead Cells Daily Run Emulator ===")
    try:
        server = ReusableTCPServer(("127.0.0.1", PORT), DailyRunHandler)
    except OSError as e:
        log(f"Port {PORT} already in use or cannot bind: {e}. Another instance might be running.")
        sys.exit(0)

    wd_thread = threading.Thread(target=watchdog, args=(server,), daemon=True)
    wd_thread.start()

    log(f"Server is listening on http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except Exception as e:
        log(f"Server exception: {e}")
    finally:
        server.server_close()
        log("Server stopped cleanly.")

if __name__ == "__main__":
    main()
