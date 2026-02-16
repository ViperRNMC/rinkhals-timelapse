"""
Rinkhals Timelapse - Automatic Timelapse creator for Rinkhals based Anycubic 3D Printer
Fork / maintained by: ViperRNMC (https://github.com/ViperRNMC/rinkhals-timelapse)
License: MIT
Description: Automatically detects print status via Moonraker API and
calculates ideal intervals for perfect 15s timelapses.
"""

import requests, time, os, threading, subprocess, json, glob
from flask import Flask, render_template_string, send_from_directory, request, redirect, jsonify
from collections import deque

app = Flask(__name__)
# Support overriding paths and printer IP via environment (useful for Home Assistant add-on)
CONFIG_FILE = os.environ.get("CONFIG_FILE", "config.json")
ENV_PRINTER = os.environ.get("PRINTER_IP")
MEDIA_PATH = os.environ.get("MEDIA_PATH", "").strip()

if MEDIA_PATH:
    SNAPSHOT_DIR = os.path.join(MEDIA_PATH, "snapshots")
    VIDEO_DIR = os.path.join(MEDIA_PATH, "videos")
    THUMB_DIR = os.path.join(VIDEO_DIR, "thumbs")
else:
    SNAPSHOT_DIR = "snapshots"
    VIDEO_DIR = "videos"
    THUMB_DIR = "videos/thumbs"

for d in [SNAPSHOT_DIR, VIDEO_DIR, THUMB_DIR]: 
    os.makedirs(d, exist_ok=True)

def load_config():
    defaults = {"printer_ip": "10.10.10.99", "mode": "layer"}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return {**defaults, **json.load(f)}
    return defaults

config = load_config()
# Apply environment overrides if present
if ENV_PRINTER:
    config['printer_ip'] = ENV_PRINTER
if MEDIA_PATH:
    config['media_path'] = MEDIA_PATH

LOG_STACK = deque(maxlen=10)

is_printing = False
last_layer = -1
print_progress = 0
current_interval = 0
last_snap_time = 0
last_image_ts = 0 

def log_it(msg):
    LOG_STACK.appendleft(f"[{time.strftime('%H:%M:%S')}] {msg}")

def render_video(job_name="manual_render"):
    timestamp = time.strftime("%Y-%m-%d_%H-%M")
    safe_name = "".join([c for c in job_name if c.isalnum()]).rstrip() or "print"
    vid_name = f"{timestamp}_{safe_name}.mp4"
    output_file = os.path.join(VIDEO_DIR, vid_name)
    thumb_file = os.path.join(THUMB_DIR, f"{vid_name}.jpg")
    
    images = sorted(glob.glob(f"{SNAPSHOT_DIR}/*.jpg"))
    if len(images) < 2:
        log_it("Error: Not enough frames for video.")
        return

    log_it(f"Rendering {vid_name} ({len(images)} frames)...")
    try:
        subprocess.run(f"ffmpeg -y -framerate 30 -pattern_type glob -i '{SNAPSHOT_DIR}/*.jpg' -c:v libx264 -pix_fmt yuv420p -crf 23 {output_file}", shell=True, check=True)
        if images:
            subprocess.run(f"cp {images[-1]} {thumb_file}", shell=True)
        for f in images: os.remove(f)
        log_it("Render Success!")
    except Exception as e:
        log_it(f"Render Error: {e}")

def get_smart_interval(filename):
    try:
        url = f"http://{config['printer_ip']}/server/files/metadata?filename={filename}"
        r = requests.get(url, timeout=2)
        meta = r.json()
        estimated_time = meta['result'].get('estimated_time', 0)
        if estimated_time > 0:
            calc = max(5, min(estimated_time / 450, 60))
            return int(calc)
    except: pass
    return 15

def monitor_loop():
    global last_layer, is_printing, print_progress, current_interval, last_snap_time, last_image_ts
    log_it("System ready.")
    job_filename = ""
    
    while True:
        try:
            r = requests.get(f"http://{config['printer_ip']}:7125/printer/objects/query?virtual_sdcard&print_stats", timeout=3).json()
            stats = r["result"]["status"]
            state = stats["print_stats"]["state"]
            filename = stats["print_stats"]["filename"]
            is_active = stats["virtual_sdcard"].get("is_active", False)
            current_layer = stats["virtual_sdcard"].get("current_layer", 0)
            print_progress = int(stats["virtual_sdcard"].get("progress", 0) * 100)
            
            if state == "printing" and is_active and not is_printing:
                is_printing = True
                job_filename = filename
                log_it("Print started.")
                if config['mode'] == 'time':
                    current_interval = get_smart_interval(filename)
                    log_it(f"Smart Mode: {current_interval}s")
                else:
                    current_interval = 0
            
            if is_printing:
                if not is_active or state in ["complete", "standby", "error", "cancelled"] or print_progress >= 100:
                    is_printing = False
                    log_it(f"Print stopped (State: {state})")
                    if state == "complete" or print_progress >= 100:
                        log_it("Auto-Render...")
                        threading.Thread(target=render_video, args=(job_filename,)).start()
                    last_layer = -1
                    continue
                
                take_snap = False
                if config['mode'] == 'layer':
                    if current_layer > 0 and current_layer != last_layer:
                        take_snap = True
                        last_layer = current_layer
                elif config['mode'] == 'time':
                    now = time.time()
                    if (now - last_snap_time) > current_interval:
                        take_snap = True
                        last_snap_time = now

                if take_snap:
                    ts_idx = int(time.time() * 10) 
                    img_data = requests.get(f"http://{config['printer_ip']}/webcam/?action=snapshot", timeout=5).content
                    with open(f"{SNAPSHOT_DIR}/frame_{ts_idx}.jpg", "wb") as f:
                        f.write(img_data)
                    last_image_ts = time.time()

        except: pass
        time.sleep(2)

# --- API ENDPOINTS ---
@app.route('/status')
def status_api():
    video_count = len([f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')])
    return jsonify({
        "is_printing": is_printing,
        "progress": print_progress,
        "logs": list(LOG_STACK),
        "img_ts": last_image_ts,
        "video_count": video_count,
        "mode": config['mode'],
        "interval": current_interval
    })

@app.route('/manual_render')
def manual_render():
    if is_printing:
        return "Not possible during active print", 400
    threading.Thread(target=render_video, args=("manual_job",)).start()
    return redirect('/')

# --- WEB INTERFACE ---
HTML_TEMPLATE = """
<...TRUNCATED FOR BREVITY...>
"""

@app.route('/')
def index():
    vids = sorted([f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')], reverse=True)
    return render_template_string(HTML_TEMPLATE, logs=list(LOG_STACK), vids=vids, ip=config['printer_ip'], mode=config['mode'])

@app.route('/save_config', methods=['POST'])
def save_config():
    global config
    config['printer_ip'], config['mode'] = request.form.get('ip'), request.form.get('mode')
    with open(CONFIG_FILE, "w") as f: json.dump(config, f)
    return redirect('/')

@app.route('/last_snap')
def last_snap():
    snaps = sorted(glob.glob(f"{SNAPSHOT_DIR}/*.jpg"))
    if snaps: return send_from_directory(SNAPSHOT_DIR, os.path.basename(max(snaps, key=os.path.getmtime)))
    return redirect("https://via.placeholder.com/320x180/1a1d23/3b82f6?text=Ready")

@app.route('/thumb/<path:filename>')
def thumb(filename): return send_from_directory(THUMB_DIR, filename)

@app.route('/video_file/<path:filename>')
def video_file(filename): return send_from_directory(VIDEO_DIR, filename)

@app.route('/delete/<path:filename>')
def delete(filename):
    try: 
        os.remove(os.path.join(VIDEO_DIR, filename))
        os.remove(os.path.join(THUMB_DIR, filename + ".jpg"))
    except: pass
    return redirect('/')

if __name__ == '__main__':
    threading.Thread(target=monitor_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=5005)
