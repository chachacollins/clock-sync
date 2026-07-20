#!/usr/bin/env python
import socket
import random
from datetime import datetime, timedelta
import time

LOSS_RATES = [0, 5, 10, 20]
NUM_TRIALS = 100
MAX_RETRIES = 5
TIMEOUT = 1

def attempt_sync(loss_rate):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(TIMEOUT)
    client.connect(("localhost", 8080))

    offset = random.randint(-3600, 3600)
    t0 = datetime.now() + timedelta(seconds=offset)
    retransmissions = 0

    for attempt in range(MAX_RETRIES):
        if random.random() * 100 < loss_rate:
            retransmissions += 1
            try:
                client.sendall(b"request")
                client.recv(1024)
            except Exception:
                pass
            client.close()
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(TIMEOUT)
            client.connect(("localhost", 8080))
            continue

        try:
            client.sendall(b"request")
        except Exception:
            retransmissions += 1
            client.close()
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(TIMEOUT)
            client.connect(("localhost", 8080))
            continue

        if random.random() * 100 < loss_rate:
            retransmissions += 1
            try:
                client.recv(1024)
            except Exception:
                pass
            client.close()
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(TIMEOUT)
            client.connect(("localhost", 8080))
            continue

        try:
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
            return True, retransmissions, sync_error
        except socket.timeout:
            retransmissions += 1
            client.close()
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(TIMEOUT)
            client.connect(("localhost", 8080))
            continue

    client.close()
    return False, retransmissions, None

def main():
    results = {}

    for loss_rate in LOSS_RATES:
        successes = 0
        total_retransmissions = 0
        errors = []

        for trial in range(NUM_TRIALS):
            success, retrans, error = attempt_sync(loss_rate)
            if success:
                successes += 1
                errors.append(error)
            total_retransmissions += retrans

        avg_error = sum(errors) / len(errors) if errors else 0
        results[loss_rate] = {
            "successes": successes,
            "retransmissions": total_retransmissions,
            "avg_error": avg_error,
        }

        print(f"Loss rate: {loss_rate}%")
        print(f"  Successful synchronizations: {successes}/{NUM_TRIALS}")
        print(f"  Total retransmissions:       {total_retransmissions}")
        print(f"  Average sync error:          {avg_error:.2f}s")
        print()

    plot_results(results)

def plot_results(results):
    import matplotlib.pyplot as plt

    rates = list(results.keys())
    successes = [results[r]["successes"] for r in rates]
    retransmissions = [results[r]["retransmissions"] for r in rates]
    avg_errors = [results[r]["avg_error"] for r in rates]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Activity 2: Packet Loss Simulation", fontsize=14, fontweight="bold")

    axes[0].bar([f"{r}%" for r in rates], successes, color="royalblue", edgecolor="black")
    axes[0].set_title("Successful Synchronizations")
    axes[0].set_ylabel("Count")
    axes[0].set_ylim(0, NUM_TRIALS + 5)
    for i, v in enumerate(successes):
        axes[0].text(i, v + 1, str(v), ha="center", fontweight="bold")

    axes[1].bar([f"{r}%" for r in rates], retransmissions, color="tomato", edgecolor="black")
    axes[1].set_title("Total Retransmissions")
    axes[1].set_ylabel("Count")
    for i, v in enumerate(retransmissions):
        axes[1].text(i, v + 0.5, str(v), ha="center", fontweight="bold")

    axes[2].bar([f"{r}%" for r in rates], avg_errors, color="gold", edgecolor="black")
    axes[2].set_title("Average Synchronization Error")
    axes[2].set_ylabel("Seconds")
    for i, v in enumerate(avg_errors):
        axes[2].text(i, v + 0.1, f"{v:.2f}s", ha="center", fontweight="bold")

    for ax in axes:
        ax.set_xlabel("Packet Loss Rate")
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig("packet_loss_results.png", dpi=150, bbox_inches="tight")
    plt.show()

if __name__ == "__main__":
    main()
