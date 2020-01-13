import socket
# A way to manage many connection
# Brings OS level IO (on Windows it could be different than Linux)
# Makes code run the same weather you use Windows/Mac/Linux
import select
import os
import configparser
from time import gmtime, strftime

os.system('clear')
print(r'''

   ___                     _
  / _ \  ____ ___  __ __  (_) __ __  ___
 / ___/ / __// _ \ \ \ / / / / // / (_-<
/_/    /_/   \___//_\_\ /_/  \_,_/ /___/

''')


# SETUP CONFIGPARSER
DIR = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(DIR, 'config.conf')
info_file = os.path.join(DIR, 'info.cfg')

config = configparser.ConfigParser()
config.read(config_file)

# GET BASIC PARAMS FROM CONFIG
HEADER_LENGTH = int(config.get('Main', 'HEADER_LENGTH'))
IP = config.get('Main', 'IP')
PORT = int(config.get('Main', 'PORT'))

config.read(info_file)
VERSION = config.get('Main', 'VERSION')

print('Proxius Server running | Made by koumakpet')
print('for more info, visit the github page: github.com/koumakpet/proxius')
print(f'IP: {IP}:{PORT} | {VERSION}\n')

# SETUP SERVER_SOCKET
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Allow to reconnect (fix Address in use after restart)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()


sockets_list = [server_socket]  # List of known sockets
clients = {}  # Key: client's socket, Value: user dataclients = {}


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
    except:
        return False


def log(msg):
    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print(f'[{time}]: {msg}')


while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        # Someone just connected
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            # Handle user disconnect
            if user is False:
                continue

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
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
