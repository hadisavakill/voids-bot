import subprocess
import time

def run_ngrok():
    # اجرای ngrok روی پورت 8501
    try:
        ngrok_process = subprocess.Popen(
            ["start", "cmd", "/k", "ngrok.exe http 8501"],
            shell=True
        )
        print("✅ Ngrok اجرا شد! لطفاً چند ثانیه منتظر بمانید و سپس URL عمومی را در ترمینال ببینید.")
        time.sleep(5)
    except Exception as e:
        print("❌ خطا در اجرای Ngrok:", e)

if __name__ == "__main__":
    run_ngrok()