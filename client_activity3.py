#!/usr/bin/env python
import socket
import random
import subprocess
import sys
import time
import os
from datetime import datetime, timedelta

DELAYS = [0.01, 0.1, 0.5]
DELAY_LABELS = ["10ms", "100ms", "500ms"]
NUM_TRIALS = 100
TIMEOUT = 2

def attempt_sync():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(TIMEOUT)
    client.connect(("localhost", 8080))

    offset = random.randint(-3600, 3600)
    t0 = datetime.now() + timedelta(seconds=offset)

    try:
        client.sendall(b"request")
        date_string = client.recv(1024).decode()
        t2 = datetime.now() + timedelta(seconds=offset)

        server_time = datetime.strptime(date_string, "%H:%M:%S").time()
        server_dt = datetime.combine(t0.date(), server_time)

        rtt = (t2 - t0).total_seconds()
        adjustment = (server_dt - t0).total_seconds() + rtt / 2
        synchronized_time = t0 + timedelta(seconds=adjustment)

        real_now = datetime.now()
        sync_error = abs((synchronized_time - real_now).total_seconds())

        client.close()
        return True, rtt, sync_error
    except Exception:
        client.close()
        return False, None, None

def start_server(delay):
    server = subprocess.Popen(
        [sys.executable, "server_activity3.py", str(delay)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(0.3)
    return server

def stop_server(server):
    server.terminate()
    server.wait()

def main():
    results = {}

    for delay, label in zip(DELAYS, DELAY_LABELS):
        server = start_server(delay)

        successes = 0
        rtts = []
        errors = []

        for trial in range(NUM_TRIALS):
            success, rtt, error = attempt_sync()
            if success:
                successes += 1
                rtts.append(rtt)
                errors.append(error)

        stop_server(server)

        avg_rtt = sum(rtts) / len(rtts) if rtts else 0
        avg_error = sum(errors) / len(errors) if errors else 0
        max_error = max(errors) if errors else 0
        min_error = min(errors) if errors else 0

        results[label] = {
            "delay_ms": delay * 1000,
            "successes": successes,
            "avg_rtt": avg_rtt,
            "avg_error": avg_error,
            "max_error": max_error,
            "min_error": min_error,
        }

        print(f"Server delay: {label}")
        print(f"  Successful synchronizations: {successes}/{NUM_TRIALS}")
        print(f"  Average RTT:                  {avg_rtt*1000:.1f}ms")
        print(f"  Average sync error:           {avg_error*1000:.1f}ms")
        print(f"  Min/Max sync error:           {min_error*1000:.1f}ms / {max_error*1000:.1f}ms")
        print()

    plot_results(results)

def plot_results(results):
    import matplotlib.pyplot as plt

    labels = list(results.keys())
    avg_errors = [results[l]["avg_error"] * 1000 for l in labels]
    avg_rtts = [results[l]["avg_rtt"] * 1000 for l in labels]
    max_errors = [results[l]["max_error"] * 1000 for l in labels]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Activity 3: Variable Server Processing Time", fontsize=14, fontweight="bold")

    axes[0].bar(labels, avg_errors, color="royalblue", edgecolor="black")
    axes[0].set_title("Average Synchronization Error")
    axes[0].set_ylabel("Error (ms)")
    for i, v in enumerate(avg_errors):
        axes[0].text(i, v + 0.5, f"{v:.1f}ms", ha="center", fontweight="bold")

    axes[1].bar(labels, avg_rtts, color="tomato", edgecolor="black")
    axes[1].set_title("Average Round-Trip Time")
    axes[1].set_ylabel("RTT (ms)")
    for i, v in enumerate(avg_rtts):
        axes[1].text(i, v + 0.5, f"{v:.1f}ms", ha="center", fontweight="bold")

    axes[2].bar(labels, max_errors, color="gold", edgecolor="black")
    axes[2].set_title("Maximum Synchronization Error")
    axes[2].set_ylabel("Error (ms)")
    for i, v in enumerate(max_errors):
        axes[2].text(i, v + 0.5, f"{v:.1f}ms", ha="center", fontweight="bold")

    for ax in axes:
        ax.set_xlabel("Server Processing Delay")
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig("server_delay_results.png", dpi=150, bbox_inches="tight")
    plt.show()

if __name__ == "__main__":
    main()
