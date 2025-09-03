from dotenv import load_dotenv
import os

load_dotenv()  # همین پوشه را برای .env می‌خواند

client_id = os.getenv("SENTINELHUB_CLIENT_ID")
client_secret = os.getenv("SENTINELHUB_CLIENT_SECRET")

print("Client ID:", client_id)
print("Client Secret:",client_secret)