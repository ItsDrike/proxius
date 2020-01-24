import socket
# A way to manage many connection
# Brings OS level IO (on Windows it could be different than Linux)
# Makes code run the same weather you use Windows/Mac/Linux
import select
import os
import configparser
from time import gmtime, strftime
import sys


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


def init_msg(ip, port, version):
    clear()
    print(r'''

       ___                     _
      / _ \  ____ ___  __ __  (_) __ __  ___
     / ___/ / __// _ \ \ \ / / / / // / (_-<
    /_/    /_/   \___//_\_\ /_/  \_,_/ /___/

    ''')

    print('Proxius Server running | Made by koumakpet')
    print('for more info, visit the github page: github.com/koumakpet/proxius')
    print(f'IP: {ip}:{port} | {version}\n')


def log(msg):
    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print(f'[{time}]: {msg}')


def get_header(message):
    return f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')


def receive_message(client_socket):
    try:
        # Receive header
        message_header = client_socket.recv(HEADER_LENGTH)

        # If no data was received, client closed the connection
        if not len(message_header):
            return False

        # Get message length from the received header
        message_length = int(message_header.decode('utf-8').strip())

        return {'header': message_header, 'data': client_socket.recv(message_length)}
    # Can happen if client breaks their script
    except Exception:
        return False


# GET BASIC PARAMS FROM CONFIG
config_file = 'config.conf'
info_file = 'info.cfg'

HEADER_LENGTH = int(get_config(config_file, 'Main', 'HEADER_LENGTH'))
IP = get_config(config_file, 'Main', 'IP')
PORT = int(get_config(config_file, 'Main', 'PORT'))

VERSION = get_config(info_file, 'Main', 'VERSION')


# Show starting message
init_msg(IP, PORT, VERSION)

# SETUP SERVER_SOCKET
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Allow to reconnect (fix Address in use after restart)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Set IP (and port)
server_socket.bind((IP, PORT))

server_socket.listen()


sockets_list = [server_socket]  # List of known sockets
clients = {}  # Key: client's socket, Value: user dataclients = {}


while True:
    try:
        read_sockets, write_sockets, exception_sockets = select.select(
            sockets_list, [], sockets_list)
    except KeyboardInterrupt:
        print('\n\nServer stopped.. (KeyboardInterrupt)')
        sys.exit()

    for notified_socket in read_sockets:
        # Someone just connected
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            # Handle user disconnect
            if user is False:
                log(
                    f'New connection failed from {client_address[0]}:{client_address[1]}')

            # Add user's socket to socket_list
            sockets_list.append(client_socket)

            # Add client's info to clients dict
            clients[client_socket] = user

            username = user['data'].decode('utf-8')
            log(
                f'Accepted new connection from {client_address[0]}:{client_address[1]} username:{username}')
        # Someone sent a message/left
        else:
            message = receive_message(notified_socket)

            # Connection closed
            if message is False:
                username = clients[notified_socket]['data'].decode('utf-8')
                log(f'Closed connection from {username}')
                # Remove disconnected socket from sockets_list
                sockets_list.remove(notified_socket)
                # Remove disconnected socket from clients (dict)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            username = user['data'].decode('utf-8')
            msg = message['data'].decode('utf-8')
            log(f'Received message from {username}: {msg}')

            # Share the message with everyone
            for client_socket in clients:
                # Don't send back to sender
                if client_socket != notified_socket:
                    # Send info about sender and the message he sent to other clients
                    sender_information = user['header'] + user['data']
                    message_to_send = message['header'] + message['data']
                    client_socket.send(sender_information + message_to_send)

    for notified_socket in exception_sockets:
        username = clients[notified_socket]['data'].decode('utf-8')
        log(f'Exception logged from {username}')
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
