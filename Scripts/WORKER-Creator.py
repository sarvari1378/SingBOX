# libraries
from telethon.sync import TelegramClient
from datetime import datetime, timedelta
import re
import requests
from datetime import datetime
import pytz
import requests
import regex
from collections import namedtuple
import os
import base64
import json
import jdatetime



# variables

# Telegram API credentials
api_id = os.environ.get('TELEGRAM_API_ID')
api_hash = os.environ.get('TELEGRAM_API_HASH')
session_file = 'Telegram/Session/@AliDelbaz.session'



# functions


def get_last_message_from_id(client, sender_id):
    # Get the last message sent by the specified sender_id
    messages = client.get_messages(sender_id, limit=1)
    
    # Return the message text if available, otherwise return None
    if messages:
        return messages[0].message
    else:
        return None
    
def extract_link(text):
    # Regular expression pattern to match HTTPS links
    pattern = r'https://\S+'
    
    # Find all matches of the pattern in the text
    matches = re.findall(pattern, text)
    
    # Return the first match (if any)
    if matches:
        return matches[0]
    else:
        return None

def check_url(url, phrase):
    try:
        # Make a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Search for the phrase in the raw content of the response
            if phrase in response.text:
                return True
            else:
                return False
        else:
            print(f"Request failed with status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        # Handle any exceptions that may occur during the request
        print(f"Error: {e}")
        return False


def Provide_Link ():
    client = TelegramClient(session_file, api_id, api_hash)
    client.start()
    Last_message = get_last_message_from_id(client,'@Qv2raybot')
    Last_Link = extract_link(Last_message)

    check_url (Last_Link, 'trojan://pooya')

    if check_url == True:
        print
        maghsad = "@Qv2raybot"
        message = "Xray"
        client.send_message(maghsad, message)
        Last_message = get_last_message_from_id(client,'@Qv2raybot')
        Last_Link = extract_link(Last_message)
        Using_link = Last_Link
    else:
        Using_link = Last_Link
    client.disconnect()

    return Using_link

#################### start of Functions fo creating subs
def get_config(urls):
    responses = {}
    for url in urls:
        if url:  # Check if the URL is not empty
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    responses[url] = response.text  # get the raw content of the response
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
    return responses
####################
def merge_content(responses):
    merged_content = ''
    for url in responses:
        content = responses[url]
        if content is not None:
            try:
                decoded_content = base64.b64decode(content).decode()
                merged_content += decoded_content + '\n'
            except Exception:
                # Content is not base64 encoded, add as it is
                merged_content += content + '\n'
    return merged_content
####################

def Simple_extract_flag(line):
    
    match = regex.search(r'\p{So}\p{So}', line)
    flag = match.group() if match else ''
    
    return flag

def extract_flag(line):
    if line.startswith('vmess://'):
        line = line[8:]
        line = json.loads(base64.b64decode(line))
        namePart = line["ps"]
        flag = Simple_extract_flag(namePart)
    else:
        flag = Simple_extract_flag(line)
    return flag

####################
def Vmess_rename(vmess_config, new_name):
    # Decode vmess
    vmess_data = vmess_config[8:]  # remove "vmess://"
    config = json.loads(base64.b64decode(vmess_data))
    
    # Rename
    config["ps"] = new_name

    # Encode vmess
    encoded_data = base64.b64encode(json.dumps(config).encode()).decode()
    vmess_config = "vmess://" + encoded_data

    return vmess_config

####################
def rename_configs(content, name):
    lines = content.split('\n')
    new_lines = []
    for i, line in enumerate(lines):
        if line.startswith('vmess://'):
            # Extract country flag
            
            flag = extract_flag(line)
            

            # Get current time and date
            now = datetime.now(pytz.timezone('Asia/Tehran'))
            hour = now.strftime('%H:%M')
            date = jdatetime.date.today().strftime('%Y-%m-%d')
            
            # Construct new name
            new_name = f'|{flag}|{hour}|{date}|{name}|{i+1}|'
            
            # Rename vmess configuration
            line = Vmess_rename(line, new_name)
        elif '#' in line:
            # Extract country flag
            flag = extract_flag(line)
            
            # Remove characters after '#'
            line = line.split('#')[0]
            
            now = datetime.now(pytz.timezone('Asia/Tehran'))
            hour = now.strftime('%H:%M')
            date = jdatetime.date.today().strftime('%Y-%m-%d')
            # Add flag to new name
            line += f'#|{flag}|{hour}|{date}|{name}|{i+1}|'
        new_lines.append(line)
    return '\n'.join(new_lines)


####################
def save_to_file(content, filename):
    with open(filename, 'w') as f:
        f.write(content)
####################
def remove_lines(content, num):
    lines = content.split('\n')
    # Remove the first 'num' lines
    del lines[:num]
    return '\n'.join(lines)
####################
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

####################
def Create_SUBs(users, responses, PROTOCOL):
    # Create 'SUB' directory if it doesn't exist
    if not os.path.exists('SUB'):
        os.makedirs('SUB')

    for user in users:
        # Check if user's date as a number is zero or less
        
        if float(user.date) <= 0:
            content = 'vless://64694D4A-2C05-4FFE-AEF1-68C0169CCCB7@146.248.115.39:443?encryption=none&fp=firefox&mode=gun&pbk=TXpA-KUEqsg6YlZUXf0gZIe14rFjKZZNAqWzjruNoh8&security=reality&serviceName=&sid=790D3C76&sni=www.speedtest.net&spx=%2F&type=grpc#اشتراک شما به پایان رسیده است.'
        else:
            merged_content = merge_content(responses)
            content = rename_configs(merged_content, user.username)
            line = f'vless://64694D4A-2C05-4FFE-AEF1-68C0169CCCB7@146.248.115.39:443?encryption=none&fp=firefox&mode=gun&pbk=TXpA-KUEqsg6YlZUXf0gZIe14rFjKZZNAqWzjruNoh8&security=reality&serviceName=&sid=790D3C76&sni=www.speedtest.net&spx=%2F&type=grpc#|👤نام: {user.username}|⌛️روز های باقی مانده: {user.date}|'
            if float(user.date) >= 999:
                Limit = 'vless://64694D4A-2C05-4FFE-AEF1-68C0169CCCB7@146.248.115.39:443?encryption=none&fp=firefox&mode=gun&pbk=TXpA-KUEqsg6YlZUXf0gZIe14rFjKZZNAqWzjruNoh8&security=reality&serviceName=&sid=790D3C76&sni=www.speedtest.net&spx=%2F&type=grpc#سرویس رایگان در تاریخ ۱۰ اسفند جمع آوری خواهد شد'
            else:
                Limit= ''
                
            content = line + '\n' + Limit + '\n' + content

        filename = f'SUB/{PROTOCOL}-{user.username}'
        with open(filename, 'w') as f:
            f.write(content)            

###########################

########################### end of functions for creating subs

#Ceate SUBS

Using_link = Provide_Link()
User_url = 'https://raw.githubusercontent.com/sarvari1378/SingBOX/main/Users.txt'
users = get_users(User_url)
urls = ['https://af5734d8-de4d-4ce3-9572-be8d6fc682ae.qconnect.top/6a7952bd-1d7d-4f87-7bcd-223358afd3f9U083']
urls.append(Using_link)
responses = get_config(urls)
Create_SUBs(users, responses, 'WORKER')
