# batch_process.py
import csv
import subprocess
import os
from datetime import datetime

INPUT_CSV = "batch/locations.csv"

def process_row(lat, lon, mode):
    date_from = "2024-08-01"
    date_to = datetime.now().strftime("%Y-%m-%d")
    cmd = f"python subsurface_analyze.py --mode {mode} --lat {lat} --lon {lon} --radius 300 --from {date_from} --to {date_to}"
    print("🔄 Running:", cmd)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Done:", lat, lon)
        else:
            print("❌ Error:", result.stderr)
    except Exception as e:
        print("❌ Exception:", e)

def main():
    if not os.path.exists(INPUT_CSV):
        print("❌ فایل CSV پیدا نشد:", INPUT_CSV)
        return

    with open(INPUT_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lat = float(row["lat"])
            lon = float(row["lon"])
            mode = row["mode"].strip()
            if mode in ["void", "metal"]:
                process_row(lat, lon, mode)
            else:
                print(f"⚠️ حالت نامعتبر: {mode}")

if __name__ == "__main__":
    main()