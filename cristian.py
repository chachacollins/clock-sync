from datetime import datetime
import socket
import threading
import time

def return_time(client_sock, addr):
    #time to delay execution
    time.sleep(4)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    client_sock.sendall(current_time.encode())

def main():
    server_addr = 8080
    server      = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', server_addr))
    server.listen(socket.SOMAXCONN)
    print(f"Listening on localhost:{server_addr}")
    while True:
        client_sock, addr = server.accept()
        print(f"\nConnection from {addr}")
        client_thread = threading.Thread(target=return_time, args=(client_sock, addr))
        client_thread.daemon = True
        client_thread.start()

if __name__ == '__main__':
    main()
