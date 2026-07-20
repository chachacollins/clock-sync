#!/usr/bin/env python
import socket
import random
import time as time_mod
import subprocess
import sys
import os
import struct
from datetime import datetime, timedelta

NUM_TRIALS = 100
TIMEOUT = 2
CONFIGS = {
    "fast_10ms":  {"port": 8081, "delay": 0.01},
    "medium_100ms": {"port": 8082, "delay": 0.1},
    "slow_500ms": {"port": 8083, "delay": 0.5},
}

def get_net_bytes():
    try:
        with open("/proc/net/dev") as f:
            lines = f.readlines()
        total = 0
        for line in lines[2:]:
            parts = line.split()
            if len(parts) >= 10:
                total += int(parts[1]) + int(parts[9])
        return total
    except Exception:
        return 0

def get_cpu_percent():
    try:
        with open("/proc/stat") as f:
            line = f.readline()
        parts = line.split()
        idle = int(parts[4])
        total = sum(int(p) for p in parts[1:])
        return idle, total
    except Exception:
        return 0, 1

def start_server(port, delay):
    p = subprocess.Popen(
        [sys.executable, "server_activity5.py", str(port), str(delay)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return p

def stop_server(p):
    p.terminate()
    p.wait()

def attempt_sync(port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(TIMEOUT)
    client.connect(("localhost", port))

    t0 = datetime.now()
    msg_size = len(b"request")
    try:
        client.sendall(b"request")
        data = client.recv(1024)
        t2 = datetime.now()

        server_time = datetime.strptime(data.decode(), "%H:%M:%S").time()
        server_dt = datetime.combine(t0.date(), server_time)

        rtt = (t2 - t0).total_seconds()
        adjustment = (server_dt - t0).total_seconds() + rtt / 2
        synchronized_time = t0 + timedelta(seconds=adjustment)
        real_now = datetime.now()
        sync_error = abs((synchronized_time - real_now).total_seconds())

        resp_size = len(data)
        client.close()
        return True, rtt, sync_error, msg_size + resp_size
    except Exception:
        client.close()
        return False, None, None, 0

def main():
    results = {}

    for name, cfg in CONFIGS.items():
        server = start_server(cfg["port"], cfg["delay"])
        time_mod.sleep(0.5)

        errors = []
        rtts = []
        successes = 0
        total_bytes = 0
        sync_times = []

        idle1, total1 = get_cpu_percent()
        net1 = get_net_bytes()
        t_start = time_mod.time()

        for trial in range(NUM_TRIALS):
            ok, rtt, error, bytes_used = attempt_sync(cfg["port"])
            if ok:
                successes += 1
                rtts.append(rtt)
                errors.append(error)
                total_bytes += bytes_used
                sync_times.append(rtt)

        t_end = time_mod.time()
        net2 = get_net_bytes()
        idle2, total2 = get_cpu_percent()

        stop_server(server)

        total_time = t_end - t_start
        avg_rtt = sum(rtts) / len(rtts) if rtts else 0
        avg_error = sum(errors) / len(errors) if errors else 0
        max_error = max(errors) if errors else 0
        min_error = min(errors) if errors else 0
        throughput = successes / total_time if total_time > 0 else 0

        cpu_total = total2 - total1
        cpu_idle = idle2 - idle1
        cpu_used = ((cpu_total - cpu_idle) / cpu_total * 100) if cpu_total > 0 else 0

        net_used = net2 - net1

        results[name] = {
            "delay_ms": cfg["delay"] * 1000,
            "successes": successes,
            "avg_rtt_ms": avg_rtt * 1000,
            "avg_error_ms": avg_error * 1000,
            "max_error_ms": max_error * 1000,
            "min_error_ms": min_error * 1000,
            "total_bytes": total_bytes,
            "avg_bytes": total_bytes / successes if successes else 0,
            "cpu_percent": cpu_used,
            "net_bytes": net_used,
            "throughput": throughput,
            "total_time": total_time,
        }

        print(f"Config: {name} (server delay={cfg['delay']*1000:.0f}ms)")
        print(f"  Successful syncs:  {successes}/{NUM_TRIALS}")
        print(f"  Average RTT:       {avg_rtt*1000:.1f}ms")
        print(f"  Average error:     {avg_error*1000:.1f}ms")
        print(f"  Min/Max error:     {min_error*1000:.1f}ms / {max_error*1000:.1f}ms")
        print(f"  Total bytes:       {total_bytes}")
        print(f"  Avg bytes/sync:    {total_bytes // max(successes, 1)}")
        print(f"  CPU usage:         {cpu_used:.2f}%")
        print(f"  Network traffic:   {net_used} bytes")
        print(f"  Throughput:        {throughput:.1f} syncs/sec")
        print(f"  Total time:        {total_time:.2f}s")
        print()

    print_table(results)
    plot_results(results)

def print_table(results):
    print("=" * 90)
    print(f"{'Metric':<30} {'fast_10ms':<20} {'medium_100ms':<20} {'slow_500ms':<20}")
    print("=" * 90)
    names = list(results.keys())
    rows = [
        ("Server Delay (ms)", lambda r: f"{r['delay_ms']:.0f}"),
        ("Successful Syncs", lambda r: f"{r['successes']}/{NUM_TRIALS}"),
        ("Avg RTT (ms)", lambda r: f"{r['avg_rtt_ms']:.1f}"),
        ("Avg Error (ms)", lambda r: f"{r['avg_error_ms']:.1f}"),
        ("Max Error (ms)", lambda r: f"{r['max_error_ms']:.1f}"),
        ("Total Bytes", lambda r: f"{r['total_bytes']}"),
        ("Avg Bytes/Sync", lambda r: f"{r['avg_bytes']:.0f}"),
        ("CPU Usage (%)", lambda r: f"{r['cpu_percent']:.2f}"),
        ("Network Traffic (B)", lambda r: f"{r['net_bytes']}"),
        ("Throughput (syncs/s)", lambda r: f"{r['throughput']:.1f}"),
        ("Total Time (s)", lambda r: f"{r['total_time']:.2f}"),
    ]
    for label, fn in rows:
        vals = [fn(results[n]) for n in names]
        print(f"{label:<30} {vals[0]:<20} {vals[1]:<20} {vals[2]:<20}")
    print("=" * 90)
    print()

def plot_results(results):
    import matplotlib.pyplot as plt

    labels = list(results.keys())
    display = ["Fast (10ms)", "Medium (100ms)", "Slow (500ms)"]

    avg_errors = [results[l]["avg_error_ms"] for l in labels]
    avg_rtts = [results[l]["avg_rtt_ms"] for l in labels]
    total_bytes = [results[l]["total_bytes"] for l in labels]
    cpu_percents = [results[l]["cpu_percent"] for l in labels]
    throughputs = [results[l]["throughput"] for l in labels]

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Activity 6: Performance Analysis", fontsize=14, fontweight="bold")
    colors = ["royalblue", "tomato", "gold"]

    axes[0][0].bar(display, avg_errors, color=colors, edgecolor="black")
    axes[0][0].set_title("Avg Synchronization Error")
    axes[0][0].set_ylabel("Error (ms)")
    for i, v in enumerate(avg_errors):
        axes[0][0].text(i, v + 0.2, f"{v:.1f}", ha="center", fontweight="bold")

    axes[0][1].bar(display, avg_rtts, color=colors, edgecolor="black")
    axes[0][1].set_title("Avg Round-Trip Time")
    axes[0][1].set_ylabel("RTT (ms)")
    for i, v in enumerate(avg_rtts):
        axes[0][1].text(i, v + 0.5, f"{v:.1f}", ha="center", fontweight="bold")

    axes[0][2].bar(display, total_bytes, color=colors, edgecolor="black")
    axes[0][2].set_title("Total Network Traffic")
    axes[0][2].set_ylabel("Bytes")
    for i, v in enumerate(total_bytes):
        axes[0][2].text(i, v + 50, str(v), ha="center", fontweight="bold")

    axes[1][0].bar(display, cpu_percents, color=colors, edgecolor="black")
    axes[1][0].set_title("CPU Utilization")
    axes[1][0].set_ylabel("CPU (%)")
    for i, v in enumerate(cpu_percents):
        axes[1][0].text(i, v + 0.01, f"{v:.2f}%", ha="center", fontweight="bold")

    axes[1][1].bar(display, throughputs, color=colors, edgecolor="black")
    axes[1][1].set_title("Synchronization Throughput")
    axes[1][1].set_ylabel("Syncs/sec")
    for i, v in enumerate(throughputs):
        axes[1][1].text(i, v + 0.2, f"{v:.1f}", ha="center", fontweight="bold")

    table_data = [
        [f"{results[l]['successes']}/{NUM_TRIALS}" for l in labels],
        [f"{results[l]['avg_error_ms']:.1f}ms" for l in labels],
        [f"{results[l]['avg_bytes']:.0f}B" for l in labels],
    ]
    table_labels = ["Success Rate", "Avg Error", "Avg Bytes"]
    axes[1][2].axis("off")
    table = axes[1][2].table(
        cellText=table_data,
        rowLabels=table_labels,
        colLabels=["Fast", "Medium", "Slow"],
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)
    axes[1][2].set_title("Summary Table", fontweight="bold", pad=20)

    for row in axes.flat[:5]:
        row.grid(axis="y", linestyle="--", alpha=0.4)
        row.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig("performance_results.png", dpi=150, bbox_inches="tight")
    plt.show()

if __name__ == "__main__":
    main()
