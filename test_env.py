import os
from dotenv import load_dotenv

load_dotenv()

print("CLIENT_ID:", os.getenv("SENTINELHUB_CLIENT_ID"))
print("CLIENT_SECRET:", os.getenv("SENTINELHUB_CLIENT_SECRET"))