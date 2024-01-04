import requests

class User:
    def __init__(self, name, date, tel_username=None):
        self.name = name
        self.date = date
        self.tel_username = tel_username

def read_users_from_url(url):
    users = []
    response = requests.get(url)
    lines = response.text.split('\n')
    for line in lines:
        parts = line.strip().split(', ')
        if parts[0]:  # check if line is not empty
            name = parts[0]
            date = int(parts[1])
            tel_username = parts[2] if len(parts) > 2 else None
            user = User(name, date, tel_username)
            users.append(user)
    return users


def write_users_to_file(users, filename):
    with open(filename, 'w') as file:
        for user in users:
            line = f"{user.name}, {user.date}"
            if user.tel_username:
                line += f", @{user.tel_username}"
            file.write(line + '\n')


# Example of usage
users = read_users_from_url('https://raw.githubusercontent.com/sarvari1378/GPTscripts/main/Users.txt')

for user in users:
    user.date = user.date - 1
   
write_users_to_file(users,'Users.txt')
