import socket
import sys
import errno
import os
import configparser

# SETUP CONFIGPARSER
DIR = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(DIR, 'config.conf')
info_file = os.path.join(DIR, 'info.cfg')

config = configparser.ConfigParser()
config.read(config_file)

# GET BASIC PARAMS FROM CONFIG
HEADER_LENGTH = int(config.get('Main', 'HEADER_LENGTH'))

config.read(info_file)
VERSION = config.get('Main', 'VERSION')

os.system('clear')

print('Proxius Client running | koumakpet')
print('for more info, visit the github page: github.com/koumakpet/proxius')
print(f'{VERSION}\n')

if len(sys.argv) != 5:
    print('Usage: python client.py <Host IP> <PORT> <Password> <Username>')
    sys.exit()

HOST_IP = sys.argv[1]
PORT = int(sys.argv[2])
PASSWORD = sys.argv[3]
USERNAME = sys.argv[4]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((HOST_IP, PORT))
except ConnectionRefusedError:
    print('Connection refused (Check IP and Port)')
    sys.exit()
# Receive functionality will not be blocking
client_socket.setblocking(False)

# Send username to server
uname = USERNAME.encode('utf-8')
uname_header = f'{len(uname):<{HEADER_LENGTH}}'.encode('utf-8')
client_socket.send(uname_header + uname)

while True:
    message = input(f'[{USERNAME}]: ')

    # Check if message is not empty
    if message:
        # Send message
        message = message.encode('utf-8')
        message_header = f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')
        client_socket.send(message_header + message)

    try:
        while True:
            # Receive things
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print('connection closed by the server')
                sys.exit()

            # Get username
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            # Get message
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            print(f'[{username}]: {message}')

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('reading error', str(e))
            sys.exit()
        continue

    # except Exception as e:
    #     print('General error', str(e))
    #     sys.exit()
