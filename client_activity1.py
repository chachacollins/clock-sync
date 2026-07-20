#!/usr/bin/env python
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta

SYNC_INTERVALS = [1, 5, 10, 30]
SYNC_LABELS = ["1s", "5s", "10s", "30s"]
TOTAL_DURATION = 60
TIMEOUT = 2

def start_server():
    server = subprocess.Popen(
        [sys.executable, "server_activity3.py", "0.05"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(0.3)
    return server

def stop_server(server):
    server.terminate()
    server.wait()

def attempt_sync():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(TIMEOUT)
    client.connect(("localhost", 8080))

    t0 = datetime.now()
    try:
        client.sendall(b"request")
        data = client.recv(1024)
        t2 = datetime.now()

        resp_size = len(data)
        req_size = len(b"request")

        server_time = datetime.strptime(data.decode(), "%H:%M:%S").time()
        server_dt = datetime.combine(t0.date(), server_time)

        rtt = (t2 - t0).total_seconds()
        adjustment = (server_dt - t0).total_seconds() + rtt / 2
        synchronized_time = t0 + timedelta(seconds=adjustment)
        real_now = datetime.now()
        sync_error = abs((synchronized_time - real_now).total_seconds())

        client.close()
        return True, rtt, sync_error, req_size + resp_size
    except Exception:
        client.close()
        return False, None, None, 0

def run_frequency_test(interval):
    successes = 0
    failures = 0
    rtts = []
    errors = []
    total_bytes = 0
    sync_count = 0

    t_start = time.time()
    t_end = t_start + TOTAL_DURATION
    next_sync = t_start

    while time.time() < t_end:
        now = time.time()
        if now < next_sync:
            time.sleep(min(next_sync - now, 0.01))
            continue

        ok, rtt, error, bytes_used = attempt_sync()
        sync_count += 1

        if ok:
            successes += 1
            rtts.append(rtt)
            errors.append(error)
            total_bytes += bytes_used
        else:
            failures += 1

        next_sync = time.time() + interval

    actual_duration = time.time() - t_start
    avg_rtt = sum(rtts) / len(rtts) if rtts else 0
    avg_error = sum(errors) / len(errors) if errors else 0
    max_error = max(errors) if errors else 0
    min_error = min(errors) if errors else 0
    throughput = sync_count / actual_duration if actual_duration > 0 else 0
    bandwidth = total_bytes / actual_duration if actual_duration > 0 else 0

    return {
        "interval": interval,
        "successes": successes,
        "failures": failures,
        "sync_count": sync_count,
        "avg_rtt": avg_rtt,
        "avg_error": avg_error,
        "max_error": max_error,
        "min_error": min_error,
        "total_bytes": total_bytes,
        "avg_bytes": total_bytes / successes if successes else 0,
        "throughput": throughput,
        "bandwidth": bandwidth,
        "duration": actual_duration,
    }

def main():
    server = start_server()
    results = {}

    for interval, label in zip(SYNC_INTERVALS, SYNC_LABELS):
        print(f"Testing sync interval: {label} (duration: {TOTAL_DURATION}s)...")
        r = run_frequency_test(interval)
        results[label] = r

        print(f"  Syncs performed:     {r['sync_count']}")
        print(f"  Successful:          {r['successes']}/{r['sync_count']}")
        print(f"  Failures:            {r['failures']}")
        print(f"  Avg RTT:             {r['avg_rtt']*1000:.1f}ms")
        print(f"  Avg sync error:      {r['avg_error']*1000:.1f}ms")
        print(f"  Min/Max error:       {r['min_error']*1000:.1f}ms / {r['max_error']*1000:.1f}ms")
        print(f"  Total bytes:         {r['total_bytes']}")
        print(f"  Avg bytes/sync:      {r['avg_bytes']:.0f}")
        print(f"  Throughput:          {r['throughput']:.2f} syncs/s")
        print(f"  Bandwidth:           {r['bandwidth']:.1f} bytes/s")
        print()

    stop_server(server)
    print_table(results)
    plot_results(results)

def print_table(results):
    print("=" * 100)
    print(f"{'Metric':<25} {'1s':<18} {'5s':<18} {'10s':<18} {'30s':<18}")
    print("=" * 100)
    labels = list(results.keys())
    rows = [
        ("Sync Interval", lambda r: f"{r['interval']}s"),
        ("Total Syncs", lambda r: f"{r['sync_count']}"),
        ("Successful", lambda r: f"{r['successes']}/{r['sync_count']}"),
        ("Failures", lambda r: f"{r['failures']}"),
        ("Avg Error (ms)", lambda r: f"{r['avg_error']*1000:.1f}"),
        ("Max Error (ms)", lambda r: f"{r['max_error']*1000:.1f}"),
        ("Avg RTT (ms)", lambda r: f"{r['avg_rtt']*1000:.1f}"),
        ("Total Bytes", lambda r: f"{r['total_bytes']}"),
        ("Avg Bytes/Sync", lambda r: f"{r['avg_bytes']:.0f}"),
        ("Throughput (syncs/s)", lambda r: f"{r['throughput']:.2f}"),
        ("Bandwidth (bytes/s)", lambda r: f"{r['bandwidth']:.1f}"),
    ]
    for label, fn in rows:
        vals = [fn(results[n]) for n in labels]
        print(f"{label:<25} {vals[0]:<18} {vals[1]:<18} {vals[2]:<18} {vals[3]:<18}")
    print("=" * 100)
    print()

def plot_results(results):
    import matplotlib.pyplot as plt

    labels = list(results.keys())
    avg_errors = [results[l]["avg_error"] * 1000 for l in labels]
    max_errors = [results[l]["max_error"] * 1000 for l in labels]
    avg_rtts = [results[l]["avg_rtt"] * 1000 for l in labels]
    total_bytes = [results[l]["total_bytes"] for l in labels]
    throughputs = [results[l]["throughput"] for l in labels]
    bandwidths = [results[l]["bandwidth"] for l in labels]

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Activity 1: Synchronization Frequency Study", fontsize=14, fontweight="bold")
    colors = ["royalblue", "tomato", "gold", "seagreen"]

    axes[0][0].bar(labels, avg_errors, color=colors, edgecolor="black")
    axes[0][0].set_title("Average Synchronization Error")
    axes[0][0].set_ylabel("Error (ms)")
    for i, v in enumerate(avg_errors):
        axes[0][0].text(i, v + 0.2, f"{v:.1f}ms", ha="center", fontweight="bold")

    axes[0][1].bar(labels, max_errors, color=colors, edgecolor="black")
    axes[0][1].set_title("Maximum Synchronization Error")
    axes[0][1].set_ylabel("Error (ms)")
    for i, v in enumerate(max_errors):
        axes[0][1].text(i, v + 0.2, f"{v:.1f}ms", ha="center", fontweight="bold")

    axes[0][2].bar(labels, avg_rtts, color=colors, edgecolor="black")
    axes[0][2].set_title("Average Round-Trip Time")
    axes[0][2].set_ylabel("RTT (ms)")
    for i, v in enumerate(avg_rtts):
        axes[0][2].text(i, v + 0.2, f"{v:.1f}ms", ha="center", fontweight="bold")

    axes[1][0].bar(labels, total_bytes, color=colors, edgecolor="black")
    axes[1][0].set_title("Total Network Traffic")
    axes[1][0].set_ylabel("Bytes")
    for i, v in enumerate(total_bytes):
        axes[1][0].text(i, v + 20, str(v), ha="center", fontweight="bold")

    axes[1][1].bar(labels, throughputs, color=colors, edgecolor="black")
    axes[1][1].set_title("Synchronization Throughput")
    axes[1][1].set_ylabel("Syncs/sec")
    for i, v in enumerate(throughputs):
        axes[1][1].text(i, v + 0.02, f"{v:.2f}", ha="center", fontweight="bold")

    axes[1][2].bar(labels, bandwidths, color=colors, edgecolor="black")
    axes[1][2].set_title("Network Bandwidth Usage")
    axes[1][2].set_ylabel("Bytes/sec")
    for i, v in enumerate(bandwidths):
        axes[1][2].text(i, v + 0.5, f"{v:.1f}", ha="center", fontweight="bold")

    for row in axes:
        for ax in row:
            ax.grid(axis="y", linestyle="--", alpha=0.4)
            ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig("frequency_results.png", dpi=150, bbox_inches="tight")
    plt.show()

if __name__ == "__main__":
    main()
