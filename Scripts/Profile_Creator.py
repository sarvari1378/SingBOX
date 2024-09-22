# libraries
from datetime import datetime
import requests
import pytz
import regex
from collections import namedtuple
import os
import base64
import json
import jdatetime
import binascii
from concurrent.futures import ThreadPoolExecutor, as_completed

def add_base64_padding(base64_string):
    padding_needed = 4 - (len(base64_string) % 4)
    if padding_needed:
        base64_string += "=" * padding_needed
    return base64_string

def fetch_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return url, response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return url, None

def get_config(urls):
    responses = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fetch_url, url): url for url in urls}
        for future in as_completed(future_to_url):
            url, content = future.result()
            if content:
                responses[url] = content
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
        line = line[8:]  # Remove the 'vmess://' prefix
        line = add_base64_padding(line)  # Add padding to Base64 string
        
        try:
            # Decode Base64 content
            decoded_data = base64.b64decode(line)
            
            # Try decoding as UTF-8. If it fails, return an empty flag.
            line = decoded_data.decode('utf-8')
            
            # Try to load JSON and extract the "ps" field
            json_data = json.loads(line)
            namePart = json_data.get("ps", "")
            
            # Extract and return the flag
            flag = Simple_extract_flag(namePart)
        except (json.JSONDecodeError, binascii.Error, UnicodeDecodeError) as e:
            # Log or handle the error
            print(f"Error while decoding or extracting flag: {e}")
            flag = ''  # Return an empty flag in case of error
    else:
        # Handle non-vmess lines
        flag = Simple_extract_flag(line)
    
    return flag




def Vmess_rename(vmess_config, new_name):
    vmess_data = vmess_config[8:]  # Remove the 'vmess://' prefix
    vmess_data = add_base64_padding(vmess_data)  # Ensure base64 string is properly padded
    
    try:
        # Decode base64 data
        decoded_data = base64.b64decode(vmess_data)
        
        # Attempt to decode to a string (UTF-8)
        config_str = decoded_data.decode('utf-8')
        
        # Parse JSON, modify the configuration, and encode it back
        config = json.loads(config_str)
        config["ps"] = new_name
        
        # Re-encode the modified config back to base64
        encoded_data = base64.b64encode(json.dumps(config).encode('utf-8')).decode('utf-8')
        
        # Return the modified vmess config
        vmess_config = "vmess://" + encoded_data
    
    except (json.JSONDecodeError, binascii.Error, UnicodeDecodeError) as e:
        # Log the error for debugging purposes
        print(f"Error while processing vmess config: {e}")
    
    return vmess_config



def rename_configs(content, name):
    lines = content.split('\n')
    new_lines = []
    now = datetime.now(pytz.timezone('Asia/Tehran'))
    hour = now.strftime('%H:%M')
    date = jdatetime.date.today().strftime('%Y-%m-%d')
    
    for i, line in enumerate(lines):
        if line.startswith('vmess://'):
            flag = extract_flag(line)
            new_name = f'|{flag}|{hour}|{date}|{name}|{i+1}|'
            line = Vmess_rename(line, new_name)
        elif '#' in line:
            flag = extract_flag(line)
            line = line.split('#')[0]
            line += f'#|{flag}|{hour}|{date}|{name}|{i+1}|'
        new_lines.append(line)
    return '\n'.join(new_lines)

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

def write_to_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

def Create_SUBs(users, responses, protocol_name, links=None):
    if not os.path.exists('SUB'):
        os.makedirs('SUB')
    
    tasks = []
    if links is None:
        for user in users:
            if float(user.date) <= 0:
                content = 'vless://64694D4A-2C05-4FFE-AEF1-68C0169CCCB7@146.248.115.39:443?encryption=none&fp=firefox&mode=gun&pbk=TXpA-KUEqsg6YlZUXf0gZIe14rFjKZZNAqWzjruNoh8&security=reality&serviceName=&sid=790D3C76&sni=www.speedtest.net&spx=%2F&type=grpc#اشتراک شما به پایان رسیده است.'
            else:
                merged_content = merge_content(responses)
                content = rename_configs(merged_content, user.username)
                line = f'vless://64694D4A-2C05-4FFE-AEF1-68C0169CCCB7@146.248.115.39:443?encryption=none&fp=firefox&mode=gun&pbk=TXpA-KUEqsg6YlZUXf0gZIe14rFjKZZNAqWzjruNoh8&security=reality&serviceName=&sid=790D3C76&sni=www.speedtest.net&spx=%2F&type=grpc#|👤نام: {user.username}|⌛️روز های باقی مانده: {user.date}|'
                content = line + '\n' + content
            filename = f'SUB/{protocol_name}-{user.username}'
            tasks.append((filename, content))
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            for filename, content in tasks:
                executor.submit(write_to_file, filename, content)
    else:
        num_links = len(links)
        num_users = len(users)
        
        if num_links == 0:
            print(f"No links available for protocol: {protocol_name}")
            return

        users_per_link = num_users // num_links
        remainder = num_users % num_links

        user_index = 0
        for i, link in enumerate(links):
            if i >= num_links:
                break
            
            start_index = user_index
            end_index = user_index + users_per_link + (1 if i < remainder else 0)
            link_users = users[start_index:end_index]
            user_index = end_index
            
            if link in responses:
                content = responses[link]
            else:
                print(f"No content found for link: {link}")
                continue

            merged_content = merge_content({link: content})
            for user in link_users:
                if float(user.date) <= 0:
                    content = 'vless://64694D4A-2C05-4FFE-AEF1-68C0169CCCB7@146.248.115.39:443?encryption=none&fp=firefox&mode=gun&pbk=TXpA-KUEqsg6YlZUXf0gZIe14rFjKZZNAqWzjruNoh8&security=reality&serviceName=&sid=790D3C76&sni=www.speedtest.net&spx=%2F&type=grpc#اشتراک شما به پایان رسیده است.'
                else:
                    content = rename_configs(merged_content, user.username)
                    line = f'vless://64694D4A-2C05-4FFE-AEF1-68C0169CCCB7@146.248.115.39:443?encryption=none&fp=firefox&mode=gun&pbk=TXpA-KUEqsg6YlZUXf0gZIe14rFjKZZNAqWzjruNoh8&security=reality&serviceName=&sid=790D3C76&sni=www.speedtest.net&spx=%2F&type=grpc#|👤نام: {user.username}|⌛️روز های باقی مانده: {user.date}|'
                    content = line + '\n' + content

                filename = f'SUB/{protocol_name}-{user.username}'
                tasks.append((filename, content))

        with ThreadPoolExecutor(max_workers=10) as executor:
            for filename, content in tasks:
                executor.submit(write_to_file, filename, content)

def reorder_json_links(file_path):
    # Load the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Find the "Fredom" group
    for group in data['Protocol']:
        if group['Name'] == 'Fredom':
            # Reorder the "Links" list: move the first item to the last
            if group['Links']:
                group['Links'].append(group['Links'].pop(0))
    
    # Save the modified JSON back to the file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)



# Read JSON configuration file
json_file_path = 'Jsons/config.json'  # Adjust the path to your JSON file
with open(json_file_path, 'r') as f:
    config_data = json.load(f)

protocols = config_data['Protocol']

# Get users
User_url = 'https://raw.githubusercontent.com/sarvari1378/SingBOX/main/Users.txt'
users = get_users(User_url)

# Example usage
for protocol in protocols:
    protocol_name = protocol['Name']
    protocol_links = protocol['Links']
    
    if protocol.get('Split', False):
        responses = get_config(protocol_links)
        Create_SUBs(users, responses, protocol_name, protocol_links)
        print(f"{protocol_name} is Splited")
    else:
        responses = get_config(protocol_links)
        Create_SUBs(users, responses, protocol_name)
        print(f"{protocol_name} is not splited")


file_path = 'Jsons/config.json'  # Replace with the actual path to your JSON file
reorder_json_links(file_path)
