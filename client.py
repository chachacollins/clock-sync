#!/usr/bin/env python
import socket
from datetime import datetime, timedelta

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 42069))
    now = datetime.now() 
    print(f"TO = {now.time()}")
    date_string = client.recv(1024).decode()
    parsed_time = datetime.strptime(date_string, "%H:%M:%S").time()
    print(f"T1 = {parsed_time}")
    dt_object = datetime.combine(now.date(), parsed_time)
    td = int((abs(dt_object - now)).total_seconds())
    print(f"T1 - T0 = {td}")
    rtt = td // 2
    print(f"RTT = {rtt}")
    synchronized_client_time = dt_object + timedelta(seconds=rtt)
    print(f"Synchronized time {synchronized_client_time.time()}")

if __name__ == '__main__':
    main()

