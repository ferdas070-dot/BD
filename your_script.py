import threading
import subprocess
import time
import os
import uuid

URL = "https://new.bdcloud.eu.org/downloads/BDCLOUD_26_MARCH.exe?v=20260326"
THREADS = 200

total_downloaded = 0
lock = threading.Lock()


def format_size(bytes_val):
    """Convert bytes to MB / GB / TB automatically"""
    mb = bytes_val / 1024 / 1024
    gb = mb / 1024
    tb = gb / 1024

    if tb >= 1:
        return f"{tb:.2f} TB"
    elif gb >= 1:
        return f"{gb:.2f} GB"
    else:
        return f"{mb:.2f} MB"


def worker(thread_id):
    global total_downloaded

    while True:
        try:
            filename = f"file_{thread_id}_{uuid.uuid4().hex}.exe"

            subprocess.run([
                "aria2c",
                "-x", "16",
                "-s", "16",
                "-o", filename,
                URL
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if os.path.exists(filename):
                size = os.path.getsize(filename)

                with lock:
                    total_downloaded += size

                os.remove(filename)

        except:
            pass

        time.sleep(0.2)


def monitor():
    global total_downloaded
    last = 0

    while True:
        time.sleep(1)

        with lock:
            current = total_downloaded

        speed = (current - last) / 1024 / 1024  # MB/s
        total_str = format_size(current)

        print(f"\rSpeed: {speed:.2f} MB/s | Total Used: {total_str}", end="")

        last = current


# Start workers
for i in range(THREADS):
    t = threading.Thread(target=worker, args=(i,), daemon=True)
    t.start()

# Start monitor
threading.Thread(target=monitor, daemon=True).start()

# Keep alive
while True:
    time.sleep(0)
