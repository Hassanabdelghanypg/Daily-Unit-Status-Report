import os
import json
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# ✅ Step 1 — Service account path
SERVICE_ACCOUNT_PATH = os.environ.get("GOOGLE_SA_PATH")

if not SERVICE_ACCOUNT_PATH:
    raise ValueError("❌ GOOGLE_SA_PATH not set!")

# ✅ Step 2 — Load JSON to get client_email
with open(SERVICE_ACCOUNT_PATH, "r") as f:
    service_account_info = json.load(f)

service_email = service_account_info.get("client_email")
if not service_email:
    raise ValueError("❌ client_email not found in service account JSON!")

# ✅ Step 3 — Authenticate with service account
gauth = GoogleAuth()
gauth.settings = {
    "client_config_backend": "service",
    "service_config": {
        "client_json_file_path": SERVICE_ACCOUNT_PATH,
        "client_user_email": service_email,
    },
    "oauth_scope": [
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive.metadata.readonly",
    ],
}

gauth.ServiceAuth()
drive = GoogleDrive(gauth)
print("✅ Authenticated successfully!")

# ✅ Step 4 — Test file
test_file_path = r"reports_data\reports.csv"

if not os.path.exists(test_file_path):
    with open(test_file_path, "w") as f:
        f.write("Date,Rig,Status\n2025-10-18,Rig-7,Running")

# ✅ Step 5 — Upload to Shared Drive
SHARED_FOLDER_ID = "1HDibOtgJec7nxwVfjLLepnkcpWN__iDf"

file = drive.CreateFile({
    "title": os.path.basename(test_file_path),
    "parents": [{"id": SHARED_FOLDER_ID}]  # uploads directly into the folder
})
file.SetContentFile(test_file_path)
file.Upload()

print(f"✅ File uploaded successfully to Shared Drive: {file['title']}")
print(f"🔗 File link: {file['alternateLink']}")
