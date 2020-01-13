import socket
import select
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
else:
    print('Connected to remote host.')
# Receive functionality will not be blocking
client_socket.setblocking(False)

# Send username to server
uname = USERNAME.encode('utf-8')
uname_header = f'{len(uname):<{HEADER_LENGTH}}'.encode('utf-8')
client_socket.send(uname_header + uname)

# sys.stdout.write('\n[Me]: ')
# sys.stdout.flush()
print('\n[Me]: ', end='')

while True:
    # message = input(f'[{USERNAME}]: ')
    socket_list = [sys.stdin, client_socket]
    read_sockets, write_sockets, error_sockets = select.select(
        socket_list, [], [])

    for sock in read_sockets:
        if sock == client_socket:
            try:
                # Receive things
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print('\rconnection closed by the server')
                    sys.exit()

                # Get username
                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')
                # Get message
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                print(f'\r[{username}]: {message}')
                print(f'[Me]: ', end='')
                sys.stdout.flush()

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('reading error', str(e))
                    sys.exit()
                continue
        else:
            message = sys.stdin.readline()
            print('[Me]: ', end='')
            sys.stdout.flush()

            # Check if message is not empty
            if message:
                # Send message
                message = message.replace('\n', '')
                message = message.encode('utf-8')
                message_header = f'{len(message):<{HEADER_LENGTH}}'.encode(
                    'utf-8')
                client_socket.send(message_header + message)
