#!/usr/bin/env python
import socket
import random
import time
from datetime import datetime, timedelta
import subprocess
import sys

DRIFT_PERIODS = [0, 30, 60, 120, 300]
DRIFT_RATE = 0.05
NUM_TRIALS = 50
TIMEOUT = 2

def start_server():
    server = subprocess.Popen(
        [sys.executable, "cristian.py"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(0.3)
    return server

def stop_server(server):
    server.terminate()
    server.wait()

def attempt_sync(initial_offset):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(TIMEOUT)
    client.connect(("localhost", 8080))

    t0 = datetime.now() + timedelta(seconds=initial_offset)
    try:
        client.sendall(b"request")
        date_string = client.recv(1024).decode()
        t2 = datetime.now() + timedelta(seconds=initial_offset)

        server_time = datetime.strptime(date_string, "%H:%M:%S").time()
        server_dt = datetime.combine(t0.date(), server_time)

        rtt = (t2 - t0).total_seconds()
        adjustment = (server_dt - t0).total_seconds() + rtt / 2
        synchronized_time = t0 + timedelta(seconds=adjustment)
        real_now = datetime.now()
        sync_error = abs((synchronized_time - real_now).total_seconds())

        client.close()
        return True, rtt, adjustment, sync_error
    except Exception:
        client.close()
        return False, None, None, None

def main():
    server = start_server()
    results = {}

    for drift_period in DRIFT_PERIODS:
        drift_accumulated = []
        corrections = []
        errors = []
        successes = 0

        for trial in range(NUM_TRIALS):
            base_offset = random.randint(-3600, 3600)

            if drift_period > 0:
                actual_drift = DRIFT_RATE * drift_period
                current_offset = base_offset + actual_drift
            else:
                actual_drift = 0
                current_offset = base_offset

            ok, rtt, adjustment, error = attempt_sync(current_offset)
            if ok:
                successes += 1
                drift_accumulated.append(actual_drift)
                corrections.append(adjustment)
                errors.append(error)

        avg_drift = sum(drift_accumulated) / len(drift_accumulated) if drift_accumulated else 0
        avg_correction = sum(corrections) / len(corrections) if corrections else 0
        avg_error = sum(errors) / len(errors) if errors else 0

        results[drift_period] = {
            "avg_drift": avg_drift,
            "avg_correction": avg_correction,
            "avg_error": avg_error,
            "successes": successes,
        }

        print(f"Drift period: {drift_period}s")
        print(f"  Successful syncs:  {successes}/{NUM_TRIALS}")
        print(f"  Avg drift:         {avg_drift:.2f}s")
        print(f"  Avg correction:    {avg_correction:.2f}s")
        print(f"  Avg sync error:    {avg_error:.2f}s")
        print()

    stop_server(server)
    plot_results(results)

def plot_results(results):
    import matplotlib.pyplot as plt

    labels = [f"{k}s" for k in results.keys()]
    avg_drifts = [results[k]["avg_drift"] for k in results]
    avg_corrections = [results[k]["avg_correction"] for k in results]
    avg_errors = [results[k]["avg_error"] for k in results]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Activity 4: Clock Drift Over Time", fontsize=14, fontweight="bold")

    axes[0].bar(labels, avg_drifts, color="tomato", edgecolor="black")
    axes[0].set_title("Average Drift Accumulated")
    axes[0].set_ylabel("Drift (s)")
    for i, v in enumerate(avg_drifts):
        axes[0].text(i, v + 0.1, f"{v:.2f}s", ha="center", fontweight="bold")

    axes[1].bar(labels, [abs(c) for c in avg_corrections], color="royalblue", edgecolor="black")
    axes[1].set_title("Average Correction Applied")
    axes[1].set_ylabel("Correction (s)")
    for i, v in enumerate(avg_corrections):
        axes[1].text(i, abs(v) + 0.1, f"{v:+.2f}s", ha="center", fontweight="bold")

    axes[2].bar(labels, avg_errors, color="gold", edgecolor="black")
    axes[2].set_title("Average Synchronization Error")
    axes[2].set_ylabel("Error (s)")
    for i, v in enumerate(avg_errors):
        axes[2].text(i, v + 0.05, f"{v:.2f}s", ha="center", fontweight="bold")

    for ax in axes:
        ax.set_xlabel("Drift Period Before Sync")
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig("drift_results.png", dpi=150, bbox_inches="tight")
    plt.show()

if __name__ == "__main__":
    main()
