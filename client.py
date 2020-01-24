import socket
import select
import sys
import errno
import os
import configparser


def get_config(config_file, category, value):
    # SETUP CONFIGPARSER
    DIR = os.path.dirname(os.path.realpath(__file__))
    conf_file = os.path.join(DIR, config_file)
    config = configparser.ConfigParser()
    config.read(conf_file)
    return config.get(category, value)


def clear():
    if sys.platform == "linux" or sys.platform == "linux2":
        os.system('clear')
    elif sys.platform == "darwin":
        os.system('clear')
    elif sys.platform == "win32":
        os.system('cls')


def init_msg(version):
    clear()
    print(r'''

       ___                     _
      / _ \  ____ ___  __ __  (_) __ __  ___
     / ___/ / __// _ \ \ \ / / / / // / (_-<
    /_/    /_/   \___//_\_\ /_/  \_,_/ /___/

    ''')
    print('Proxius Client running | koumakpet')
    print('for more info, visit the github page: github.com/koumakpet/proxius')
    print(f'{version}\n')


def get_header(message):
    return f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')


def recv_message(client_socket):
    # Receive things
    username_header = client_socket.recv(HEADER_LENGTH)
    # Handle server connection error
    if not len(username_header):
        print('\rconnection closed by the server')
        sys.exit()
    # Get username
    username_length = int(
        username_header.decode('utf-8').strip())
    username = client_socket.recv(
        username_length).decode('utf-8')
    # Get message
    message_header = client_socket.recv(HEADER_LENGTH)
    message_length = int(
        message_header.decode('utf-8').strip())
    message = client_socket.recv(
        message_length).decode('utf-8')
    return username, message


def send_message(message, client_socket):
    # Check if message is not empty
    if message:
        # Send message
        message = message.replace('\n', '')
        message = message.encode('utf-8')
        message_header = get_header(message)
        client_socket.send(message_header + message)


# GET BASIC PARAMS FROM CONFIG
config_file = 'config.conf'
info_file = 'info.cfg'

HEADER_LENGTH = int(get_config(config_file, 'Main', 'HEADER_LENGTH'))
VERSION = get_config(info_file, 'Main', 'VERSION')

# Show starting message
init_msg(VERSION)

# CHECK IF CORRECT NUMBER OF PARAMETERS WAS ENTERED
if len(sys.argv) != 5:
    print('Usage: python client.py <Host IP> <PORT> <Password> <Username>')
    sys.exit()

# GET PARAMS FROM ARGV
HOST_IP = sys.argv[1]
PORT = int(sys.argv[2])
PASSWORD = sys.argv[3]
USERNAME = sys.argv[4]


# Setup socket and connect to server
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
uname_header = get_header(uname)
client_socket.send(uname_header + uname)


def main():
    print('\n[Me]: ', end='')

    while True:
        socket_list = [sys.stdin, client_socket]
        try:
            read_sockets, write_sockets, error_sockets = select.select(
                socket_list, [], [])
        except KeyboardInterrupt:
            print('\n\nConnection Interrupted')
            sys.exit()

        for notified_socket in read_sockets:
            if notified_socket == client_socket:
                try:
                    username, message = recv_message(client_socket)

                    print(f'\r[{username}]: {message}')
                    print(f'[Me]: ', end='')
                    sys.stdout.flush()

                except IOError as e:
                    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                        print('reading error', str(e))
                        sys.exit()
                    continue
            else:
                # Get input
                message = sys.stdin.readline()
                print('[Me]: ', end='')
                sys.stdout.flush()

                send_message(message, client_socket)


main()
