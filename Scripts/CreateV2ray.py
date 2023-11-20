
from datetime import datetime
import pytz
import requests
import regex
from collections import namedtuple
import os

def get_config(urls):
    for url in urls:
        if url:  # Check if the URL is not empty
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return response.text  # get the raw content of the response
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
    return None

def extract_flag(line):
    match = regex.search(r'\p{So}\p{So}', line)
    flag = match.group() if match else ''
    return flag

def rename_configs(content, name):
    lines = content.split('\n')
    new_lines = []
    for i, line in enumerate(lines):
        if '#' in line:
            # Extract country flag
            flag = extract_flag(line)
            
            # Remove characters after '#'
            line = line.split('#')[0]
            
            now = datetime.now(pytz.timezone('Asia/Tehran'))
            hour = now.strftime('%H:%M:%S')
            date = now.strftime('%Y-%m-%d')
            # Add flag to new name
            line += f'#|{flag}|{hour}|{date}|{name}|{i+1}|'
        new_lines.append(line)
    return '\n'.join(new_lines)

def save_to_file(content, filename):
    with open(filename, 'w') as f:
        f.write(content)

def remove_lines(content, num):
    lines = content.split('\n')
    # Remove the first 'num' lines
    del lines[:num]
    return '\n'.join(lines)

def get_users(url):
    response = requests.get(url)
    content = response.text.splitlines()

    User = namedtuple('User', ['username', 'date'])
    users = []

    for line in content:
        items = line.split(',')
        if len(items) >= 2:
            users.append(User(items[0].strip(), items[1].strip()))

    return users

def Create_SUBs(users, urls,PROCTCOLE):
    # Create 'SUB' directory if it doesn't exist
    if not os.path.exists('SUB'):
        os.makedirs('SUB')

    for user in users:
        # Check if user's date as a number is zero or less
        if float(user.date) <= 0:
            content = 'vless://64694d4a-2c05-4ffe-aef1-68c0169cccb7@146.248.115.39:443?encryption=none&fp=firefox&mode=gun&pbk=TXpA-KUEqsg6YlZUXf0gZIe14rFjKZZNAqWzjruNoh8&security=reality&serviceName=&sid=790d3c76&sni=www.speedtest.net&spx=%2F&type=grpc#Your-subscription-has-ended'
        else:
            content = get_config(urls)
            content = remove_lines(content,6)
            if content is not None:
                content = rename_configs(content, user.username)
                line = f'vless://64694d4a-2c05-4ffe-aef1-68c0169cccb7@146.248.115.39:443?encryption=none&fp=firefox&mode=gun&pbk=TXpA-KUEqsg6YlZUXf0gZIe14rFjKZZNAqWzjruNoh8&security=reality&serviceName=&sid=790d3c76&sni=www.speedtest.net&spx=%2F&type=grpc#|👤User: {user.username}|⌛️Remain Days: {user.date}|'
                content = line + '\n' + content

        filename = f'SUB/{PROCTCOLE}-{user.username}'
        with open(filename, 'w') as f:
            f.write(content)


url = 'https://raw.githubusercontent.com/sarvari1378/SingBOX/main/Users.txt'
users = get_users(url)
urls = [
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/reality"
]

Create_SUBs(users, urls,'REALITY')
