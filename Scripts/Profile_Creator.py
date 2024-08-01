# libraries
import pickle
import time
from datetime import datetime, timedelta
import random
import re
import requests
from datetime import datetime
import pytz
import regex
from collections import namedtuple
import os
import base64
import json
import jdatetime
import binascii  # Added binascii import

def add_base64_padding(base64_string):
    padding_needed = 4 - (len(base64_string) % 4)
    if padding_needed:
        base64_string += "=" * padding_needed
    return base64_string

def check_url_content(url, check_string):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            if check_string in response.text:
                return False
            else:
                return True
        else:
            print(f"Failed to fetch content from URL: {url}. Status code: {response.status_code}")
            return True
    except requests.RequestException as e:
        print(f"Request Exception: {e}")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return True

def get_config(urls):
    responses = {}
    for url in urls:
        if url:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    responses[url] = response.text
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
    return responses

def merge_content(responses):
    merged_content = ''
    for url in responses:
        content = responses[url]
        if content is not None:
            try:
                decoded_content = base64.b64decode(content).decode()
                merged_content += decoded_content + '\n'
            except Exception:
                merged_content += content + '\n'
    return merged_content

def Simple_extract_flag(line):
    match = regex.search(r'\p{So}\p{So}', line)
    flag = match.group() if match else ''
    return flag

def extract_flag(line):
    if line.startswith('vmess://'):
        line = line[8:]
        line = add_base64_padding(line)
        try:
            line = json.loads(base64.b64decode(line).decode('utf-8'))
            namePart = line["ps"]
            flag = Simple_extract_flag(namePart)
        except (json.JSONDecodeError, binascii.Error) as e:
            print(f"Error decoding base64 or JSON: {e}")
            flag = ''
    else:
        flag = Simple_extract_flag(line)
    return flag

def Vmess_rename(vmess_config, new_name):
    vmess_data = vmess_config[8:]
    vmess_data = add_base64_padding(vmess_data)
    try:
        config = json.loads(base64.b64decode(vmess_data).decode('utf-8'))
        config["ps"] = new_name
        encoded_data = base64.b64encode(json.dumps(config).encode()).decode()
        vmess_config = "vmess://" + encoded_data
    except (json.JSONDecodeError, binascii.Error) as e:
        print(f"Error decoding or encoding JSON: {e}")
    return vmess_config

def rename_configs(content, name):
    lines = content.split('\n')
    new_lines = []
    for i, line in enumerate(lines):
        if line.startswith('vmess://'):
            flag = extract_flag(line)
            now = datetime.now(pytz.timezone('Asia/Tehran'))
            hour = now.strftime('%H:%M')
            date = jdatetime.date.today().strftime('%Y-%m-%d')
            new_name = f'|{flag}|{hour}|{date}|{name}|{i+1}|'
            line = Vmess_rename(line, new_name)
        elif '#' in line:
            flag = extract_flag(line)
            line = line.split('#')[0]
            now = datetime.now(pytz.timezone('Asia/Tehran'))
            hour = now.strftime('%H:%M')
            date = jdatetime.date.today().strftime('%Y-%m-%d')
            line += f'#|{flag}|{hour}|{date}|{name}|{i+1}|'
        new_lines.append(line)
    return '\n'.join(new_lines)

def save_to_file(content, filename):
    with open(filename, 'w') as f:
        f.write(content)

def remove_lines(content, num):
    lines = content.split('\n')
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

def Create_SUBs(users, responses, protocol_name):
    if not os.path.exists('SUB'):
        os.makedirs('SUB')
    for user in users:
        if float(user.date) <= 0:
            content = 'vless://64694D4A-2C05-4FFE-AEF1-68C0169CCCB7@146.248.115.39:443?encryption=none&fp=firefox&mode=gun&pbk=TXpA-KUEqsg6YlZUXf0gZIe14rFjKZZNAqWzjruNoh8&security=reality&serviceName=&sid=790D3C76&sni=www.speedtest.net&spx=%2F&type=grpc#اشتراک شما به پایان رسیده است.'
        else:
            merged_content = merge_content(responses)
            content = rename_configs(merged_content, user.username)
            line = f'vless://64694D4A-2C05-4FFE-AEF1-68C0169CCCB7@146.248.115.39:443?encryption=none&fp=firefox&mode=gun&pbk=TXpA-KUEqsg6YlZUXf0gZIe14rFjKZZNAqWzjruNoh8&security=reality&serviceName=&sid=790D3C76&sni=www.speedtest.net&spx=%2F&type=grpc#|👤نام: {user.username}|⌛️روز های باقی مانده: {user.date}|'
            content = line + '\n' + content
        filename = f'SUB/{protocol_name}-{user.username}'
        with open(filename, 'w') as f:
            f.write(content)

# Read JSON configuration file
json_file_path = 'Jsons/config.json'  # Adjust the path to your JSON file
with open(json_file_path, 'r') as f:
    config_data = json.load(f)

protocols = config_data['Protocol']

# Get users
User_url = 'https://raw.githubusercontent.com/sarvari1378/SingBOX/main/Users.txt'
users = get_users(User_url)

# Process each protocol in the JSON file
for protocol in protocols:
    protocol_name = protocol['Name']
    protocol_links = protocol['Links']
    responses = get_config(protocol_links)
    Create_SUBs(users, responses, protocol_name)
