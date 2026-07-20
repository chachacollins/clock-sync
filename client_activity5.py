#!/usr/bin/env python
import socket
import random
import time as time_mod
import subprocess
import sys
from datetime import datetime, timedelta

SERVERS = {
    "fast": {"port": 8081, "delay": 0.01},
    "slow": {"port": 8082, "delay": 0.15},
}
NUM_TRIALS = 100
TIMEOUT = 2

def start_servers():
    procs = []
    for name, cfg in SERVERS.items():
        p = subprocess.Popen(
            [sys.executable, "server_activity5.py", str(cfg["port"]), str(cfg["delay"])],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        procs.append(p)
    time_mod.sleep(0.5)
    return procs

def stop_servers(procs):
    for p in procs:
        p.terminate()
        p.wait()

def sync_with_server(port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(TIMEOUT)
    client.connect(("localhost", port))

    t0 = datetime.now()
    try:
        client.sendall(b"request")
        date_string = client.recv(1024).decode()
        t2 = datetime.now()

        server_time = datetime.strptime(date_string, "%H:%M:%S").time()
        server_dt = datetime.combine(t0.date(), server_time)

        rtt = (t2 - t0).total_seconds()
        adjustment = (server_dt - t0).total_seconds() + rtt / 2
        synchronized_time = t0 + timedelta(seconds=adjustment)
        real_now = datetime.now()
        sync_error = abs((synchronized_time - real_now).total_seconds())

        client.close()
        return True, rtt, server_dt, sync_error
    except Exception:
        client.close()
        return False, None, None, None

def main():
    procs = start_servers()
    results = {}

    strategies = ["nearest", "least_loaded", "average"]
    for strategy in strategies:
        errors = []
        rtts = []
        successes = 0

        for trial in range(NUM_TRIALS):
            if strategy == "nearest":
                best_port = None
                best_rtt = float("inf")
                for name, cfg in SERVERS.items():
                    ok, rtt, sdt, err = sync_with_server(cfg["port"])
                    if ok and rtt < best_rtt:
                        best_rtt = rtt
                        best_port = cfg["port"]
                        best_err = err
                if best_port is not None:
                    successes += 1
                    rtts.append(best_rtt)
                    errors.append(best_err)

            elif strategy == "least_loaded":
                best_port = None
                best_sdt = None
                best_rtt = None
                best_err = None
                for name, cfg in SERVERS.items():
                    ok, rtt, sdt, err = sync_with_server(cfg["port"])
                    if ok:
                        if best_sdt is None or sdt > best_sdt:
                            best_sdt = sdt
                            best_port = cfg["port"]
                            best_rtt = rtt
                            best_err = err
                if best_port is not None:
                    successes += 1
                    rtts.append(best_rtt)
                    errors.append(best_err)

            elif strategy == "average":
                syncs = []
                for name, cfg in SERVERS.items():
                    ok, rtt, sdt, err = sync_with_server(cfg["port"])
                    if ok:
                        syncs.append((rtt, err))
                if syncs:
                    successes += 1
                    rtts.append(sum(r for r, e in syncs) / len(syncs))
                    errors.append(sum(e for r, e in syncs) / len(syncs))

        avg_rtt = sum(rtts) / len(rtts) if rtts else 0
        avg_error = sum(errors) / len(errors) if errors else 0
        results[strategy] = {
            "successes": successes,
            "avg_rtt": avg_rtt,
            "avg_error": avg_error,
        }

        print(f"Strategy: {strategy}")
        print(f"  Successful syncs: {successes}/{NUM_TRIALS}")
        print(f"  Average RTT:      {avg_rtt*1000:.1f}ms")
        print(f"  Average error:    {avg_error*1000:.1f}ms")
        print()

    stop_servers(procs)
    plot_results(results)

def plot_results(results):
    import matplotlib.pyplot as plt

    labels = list(results.keys())
    display = ["Nearest\n(lowest RTT)", "Least Loaded\n(lowest delay)", "Average\n(both servers)"]
    successes = [results[l]["successes"] for l in labels]
    avg_rtts = [results[l]["avg_rtt"] * 1000 for l in labels]
    avg_errors = [results[l]["avg_error"] * 1000 for l in labels]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Activity 5: Multiple Time Servers", fontsize=14, fontweight="bold")

    axes[0].bar(display, successes, color=["royalblue", "tomato", "gold"], edgecolor="black")
    axes[0].set_title("Successful Synchronizations")
    axes[0].set_ylabel("Count")
    axes[0].set_ylim(0, NUM_TRIALS + 5)
    for i, v in enumerate(successes):
        axes[0].text(i, v + 1, str(v), ha="center", fontweight="bold")

    axes[1].bar(display, avg_rtts, color=["royalblue", "tomato", "gold"], edgecolor="black")
    axes[1].set_title("Average Round-Trip Time")
    axes[1].set_ylabel("RTT (ms)")
    for i, v in enumerate(avg_rtts):
        axes[1].text(i, v + 0.5, f"{v:.1f}ms", ha="center", fontweight="bold")

    axes[2].bar(display, avg_errors, color=["royalblue", "tomato", "gold"], edgecolor="black")
    axes[2].set_title("Average Synchronization Error")
    axes[2].set_ylabel("Error (ms)")
    for i, v in enumerate(avg_errors):
        axes[2].text(i, v + 0.5, f"{v:.1f}ms", ha="center", fontweight="bold")

    for ax in axes:
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig("multi_server_results.png", dpi=150, bbox_inches="tight")
    plt.show()

if __name__ == "__main__":
    main()
