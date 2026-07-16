import socket
from datetime import datetime, timedelta

def main():
    """
    Client for Cristian's algorithm when the client clock is AHEAD of server time.
    This client will DELAY its own clock to synchronize with the server.
    
    Use this when you know your system clock is running ahead of the true time.
    Use the original client.py when your system clock is behind the true time.
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 8080))
    
    # Record time before sending request
    time_sent = datetime.now()
    print(f"TIME_SENT = {time_sent.time()}")
    
    # Receive time from server
    server_time_str = client.recv(1024).decode()
    print(f"SERVER_TIME_RECEIVED = {server_time_str}")
    
    # Parse the server time (seconds precision only)
    server_time = datetime.strptime(server_time_str, "%H:%M:%S")
    # Combine with today's date to get a full datetime object
    server_time = datetime.combine(time_sent.date(), server_time.time())
    
    # Record time when response was received
    time_received = datetime.now()
    print(f"TIME_RECEIVED = {time_received.time()}")
    
    # Calculate round trip time
    rtt = (time_received - time_sent).total_seconds()
    print(f"ROUND_TRIP_TIME = {rtt:.3f} seconds")
    
    # SERVER_DELAY is the known processing delay in the server
    # From cristian.py: time.sleep(4) before sending the time
    SERVER_DELAY = 4.0
    
    # Calculate network delay (one-way)
    # RTT = 2 * network_delay + SERVER_DELAY
    # Therefore: network_delay = (RTT - SERVER_DELAY) / 2
    network_delay = max(0, (rtt - SERVER_DELAY) / 2)  # Ensure non-negative
    
    # The correct time to set our clock to is:
    # server_time (when server sent response) + network_delay (time for response to reach us)
    correct_time = server_time + timedelta(seconds=network_delay)
    
    # Calculate how much our clock is off
    time_offset = (time_received - correct_time).total_seconds()
    print(f"TIME_OFFSET = {time_offset:.3f} seconds (positive means our clock is ahead)")
    
    # The time we should set our clock to
    target_time = time_received - timedelta(seconds=time_offset)
    print(f"CURRENT_TIME = {time_received.time()}")
    print(f"TIME_TO_SET_CLOCK_TO = {target_time.time()}")

if __name__ == "__main__":
    main()
