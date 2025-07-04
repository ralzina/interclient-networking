#!/usr/bin/env python3

import socket
import select
import sys

HOST = "0.0.0.0"
PORT = 8000
reserved = ["username","rename","help","listall"]

def usage(exit_status):
    print(f"""Usage: {sys.argv[0]} [HOST PORT]
Options:
    -h          Show help message

Defaults:
    HOST        0.0.0.0
    PORT        8000""")
    sys.exit(exit_int)

def setup_server():
    # Create socket
    #   socket.AF_INET: for IPv4
    #   socket.SOCK_STREAM: for TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set socket option
    #   SOL_SOCKET: socket-level options
    #   SO_REUSEADDR: reuse the port after closing the server
    #   Avoids the "Address already in use" error when restarting server
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket
    server_socket.bind((HOST,PORT))

    # Listen on socket
    server_socket.listen()

    print(f"Server running on port {PORT}")

    return server_socket

def set_user(message,clients,notified_socket,new):
    username = message.split(":",1)[1]

    if username in clients.values():
        notified_socket.send(f"Username [{username}] already in use\n".encode())
        return

    if username in reserved:
        notified_socket.send(f"Username [{username}] is a reserved command\n".encode())
        return

    old_user = ""
    if not new:
        old_user = clients[notified_socket]

    clients[notified_socket] = username

    if new:
        notified_socket.send(f"Registered as [{username}]\n".encode())

        print(f"User registered: [{username}]")

    else:
        notified_socket.send(f"Renamed effectively from [{old_user}] to [{username}]\n".encode())
        print(f"User {old_user} renamed to {username}")

def send_message(user, msg, clients):
    for key,value in clients.items():
        if value == user:
            key.send((msg+"\n").encode())
            

def main():
    global HOST, PORT

    if len(sys.argv) == 3:
        HOST = sys.argv[1].strip()
        try:
            PORT = int(sys.argv[2].strip())
        except ValueError:
            print("PORT must be an integer")
            usage(1)
    elif len(sys.argv) == 2 and sys.argv[1] == "-h":
        usage(0)
    elif len(sys.argv) != 1:
        usage(1)

    server_socket = setup_server()

    sockets_list = [server_socket]

    message = ""

    clients = {}
    
    try:
        while True:
            # Use select to check  when there's data to read from any of our sockets without bl ocking
            read_sockets, _, _ = select.select(sockets_list, [], [])

            for notified_socket in read_sockets:
                if notified_socket == server_socket:
                    client_socket, client_address = server_socket.accept()
                    sockets_list.append(client_socket)
                    print(f"Accepted connection from {client_address}")
                    client_socket.send(f"Welcome to the server, type help: to know commands\n".encode())
                else:
                    try:
                        message = notified_socket.recv(1024).decode().strip()
                        if not message:
                            raise ConnectionResetError
                        
                        if message.startswith("help:"):
                            notified_socket.send("Type username:YOURNAME to register\nType rename:NEWNAME to update username\nType destination_user:message to send a message to destination_user\nType listall: to list all users\nType help: for help\n".encode())
                        elif message.startswith("listall:"):
                            notified_socket.send((", ".join(clients.values()) + "\n").encode())
                        elif notified_socket not in clients:
                            if message.startswith("username:"):
                                set_user(message,clients,notified_socket,True)
                            else:
                                notified_socket.send("Please register first with username:YOURNAME\n".encode())
                        elif message.startswith("rename:"):
                            set_user(message,clients,notified_socket,False)
                        elif message.split(":",1)[0] in clients.values():
                            user, msg = message.split(":",1)
                            send_message(user,msg,clients)
                            print(f"[{clients[notified_socket]}] -> [{user}] : {msg}")
                        else:
                            notified_socket.send("Unkown command\n".encode())
                    except:
                        if notified_socket in clients:
                            print(f"User [{clients[notified_socket]}] disconnected")
                            del clients[notified_socket]
                        else:
                            print("Unregistered client disconnected")
                        sockets_list.remove(notified_socket)
                        notified_socket.close()
                        continue
    except KeyboardInterrupt:
        print("\nInterrupted. Closing server.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
