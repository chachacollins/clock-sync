#!/usr/bin/env python
import sys
from datetime import datetime
import socket
import threading
import time

def return_time(client_sock, addr, delay):
    client_sock.recv(1024)
    time.sleep(delay)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    client_sock.sendall(current_time.encode())

def main():
    delay = float(sys.argv[1]) if len(sys.argv) > 1 else 0.1
    server_addr = 8080
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', server_addr))
    server.listen(socket.SOMAXCONN)
    print(f"Listening on localhost:{server_addr} (delay={delay*1000:.0f}ms)")
    while True:
        client_sock, addr = server.accept()
        client_thread = threading.Thread(target=return_time, args=(client_sock, addr, delay))
        client_thread.daemon = True
        client_thread.start()

if __name__ == '__main__':
    main()
