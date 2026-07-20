#!/usr/bin/env python
from datetime import datetime
import socket
import threading
import time
import sys

def return_time(client_sock, addr, delay):
    client_sock.recv(1024)
    time.sleep(delay)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    client_sock.sendall(current_time.encode())

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    delay = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', port))
    server.listen(socket.SOMAXCONN)
    print(f"Server listening on localhost:{port} (delay={delay*1000:.0f}ms)")
    while True:
        client_sock, addr = server.accept()
        t = threading.Thread(target=return_time, args=(client_sock, addr, delay))
        t.daemon = True
        t.start()

if __name__ == '__main__':
    main()
