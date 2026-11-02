
# Generating music for my Mars game using Lyria!
# Each type of room gets its own soundtrack.

import base64
import json
import os
import subprocess
import sys

from google.oauth2 import service_account
from google.auth.transport.requests import Request
#PRompts with Chat because mine were not doing what I wanted.
prompts = {
    "discovery": "Mysterious ambient music for exploring ancient ruins on Mars. Instrumental only.",
    "hazard": "Tense electronic music for danger in a Martian cave. Instrumental only.",
    "treasure": "Sparkling adventurous music for discovering treasure on Mars. Instrumental only.",
    "puzzle": "Curious rhythmic sci-fi music for solving an alien puzzle. Instrumental only.",
    "rest": "Soft peaceful ambient music for resting in a Martian shelter. Instrumental only."
}

room_type = sys.argv[1].lower() if len(sys.argv) > 1 else "discovery"

if room_type not in prompts:
    print("Unknown room type!")
    sys.exit()

# Get my credentials from the private keys folder.
creds = service_account.Credentials.from_service_account_file(
    "keys/service.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

creds.refresh(Request())
token = creds.token

url = "https://aiplatform.googleapis.com/v1beta1/projects/wpp-cto-smartprod-sandbox/locations/global/interactions"

params = {
    "model": "lyria-3-clip-preview",
    "input": [
        {
            "type": "text",
            "text": prompts[room_type]
        }
    ]
}

# Making a real cURL request!
# I send the configuration through stdin so the access token
# doesn't appear in the command arguments.

curl_config = "\n".join([
    "request = \"POST\"",
    "url = " + json.dumps(url),
    "header = " + json.dumps("Authorization: Bearer " + token),
    "header = \"Content-Type: application/json\"",
    "data = " + json.dumps(json.dumps(params))
])

response = subprocess.run(
    ["curl", "--config", "-", "--silent", "--show-error",
     "--fail-with-body", "--max-time", "120"],
    input=curl_config,
    capture_output=True,
    text=True
)

if response.returncode != 0:
    print("Music request failed:", response.returncode)
    sys.exit(1)

data = json.loads(response.stdout)

# Decode the music into an MP3 file.
music_databytes = data["outputs"][2]["data"]
mp3_bytes = base64.b64decode(music_databytes)

os.makedirs("generated_music", exist_ok=True)

with open(f"generated_music/{room_type}.mp3", "wb") as file:
    file.write(mp3_bytes)

print(f"Saved {room_type} music!")

