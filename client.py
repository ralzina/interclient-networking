#!/usr/bin/env python3

import sys
import socket
import select

HOST = "localhost"
PORT = 8000

def usage(exit_status):
    print(f"""Usage: {sys.argv[0]} HOST PORT
Options:
    -h          Print this help message

Defaults:
    HOST        localhost
    PORT        8000""")
    sys.exit(exit_status)

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

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT}")
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

    try:
        while True:
            read_sockets, _, _ = select.select([sys.stdin,sock],[],[])

            for s in read_sockets:
                if s == sock:
                    data = sock.recv(4096)
                    if not data:
                        print("\nServer closed the connection.")
                        sys.exit(0)
                    print(data.decode(),end='')
                else:
                    msg = sys.stdin.readline()
                    if not msg:
                        print("\Goodbye!")
                        sock.close()
                        sys.exit(0)
                    sock.sendall(msg.encode())
    except KeyboardInterrupt:
        print("\nInterrupted. Closing connection.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
