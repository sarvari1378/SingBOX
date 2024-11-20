import os
import requests
from pathlib import Path

# Retrieve the GitHub Personal Access Token from the environment variable
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Make sure to set this environment variable
if not GITHUB_TOKEN:
    print("Error: GitHub token (PERIVATE_TOKEN_VIEWER) not found in the environment.")
    exit(1)

# Replace with your values
REPO_OWNER = 'sarvari1378'  # Replace with the owner of the repo
REPO_NAME = 'Telegram_Collector'  # Replace with the repository name
FOLDER_PATH = 'Subs'  # The folder in the repo you want to download
DEST_FOLDER = 'Collected_Links'  # Destination folder for the downloaded files

# GitHub API URL to list the contents of a folder in the repository
API_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FOLDER_PATH}'

# Headers for authentication
headers = {
    'Authorization': f'token {GITHUB_TOKEN}'
}

def download_file(file_url, dest_path):
    """Download a single file from GitHub and save it to the destination path."""
    print(f"Downloading {file_url} to {dest_path}...")
    response = requests.get(file_url, headers=headers)
    if response.status_code == 200:
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {dest_path}")
    else:
        print(f"Failed to download {file_url}, status code: {response.status_code}")

def download_folder(folder_url, dest_dir):
    """Download all files from a folder in a GitHub repository."""
    print(f"Accessing folder: {folder_url}")
    
    # Make sure the destination folder exists
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    # Request the contents of the folder
    response = requests.get(folder_url, headers=headers)

    if response.status_code == 200:
        contents = response.json()
        for item in contents:
            item_name = item['name']
            item_type = item['type']

            # If it's a file, download it
            if item_type == 'file':
                download_file(item['download_url'], os.path.join(dest_dir, item_name))

            # If it's a directory, recursively download its contents
            elif item_type == 'dir':
                download_folder(item['url'], os.path.join(dest_dir, item_name))
    else:
        print(f"Failed to access folder: {folder_url}, status code: {response.status_code}")

if __name__ == '__main__':
    # Start downloading the folder
    download_folder(API_URL, DEST_FOLDER)
