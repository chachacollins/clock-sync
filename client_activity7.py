#!/usr/bin/env python
import socket
import random
import time as time_mod
import subprocess
import sys
from datetime import datetime, timedelta

SERVERS = {
    "server_a": {"port": 8081, "delay": 0.01},
    "server_b": {"port": 8082, "delay": 0.05},
    "server_c": {"port": 8083, "delay": 0.2},
}
NUM_TRIALS = 100
TIMEOUT = 2
RTT_FILTER_THRESHOLD = 0.5
NUM_AVERAGING_REQUESTS = 5
DRIFT_RATE = 0.02

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

def sync_with(port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(TIMEOUT)
    client.connect(("localhost", port))
    t0 = datetime.now()
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
        error = abs((synchronized_time - real_now).total_seconds())
        client.close()
        return True, rtt, adjustment, error, server_dt
    except Exception:
        client.close()
        return False, None, None, None, None

def strategy_original():
    port = SERVERS["server_a"]["port"]
    ok, rtt, adj, err, sdt = sync_with(port)
    if ok:
        return 1, rtt, adj, err
    return 0, 0, 0, float("inf")

def strategy_multi_best():
    best_err = float("inf")
    best_adj = 0
    best_rtt = 0
    msgs = 0
    for name, cfg in SERVERS.items():
        ok, rtt, adj, err, sdt = sync_with(cfg["port"])
        msgs += 1
        if ok and err < best_err:
            best_err = err
            best_adj = adj
            best_rtt = rtt
    if best_err < float("inf"):
        return msgs, best_rtt, best_adj, best_err
    return msgs, 0, 0, float("inf")

def strategy_averaging():
    adjustments = []
    rtts = []
    msgs = 0
    for _ in range(NUM_AVERAGING_REQUESTS):
        for name, cfg in SERVERS.items():
            ok, rtt, adj, err, sdt = sync_with(cfg["port"])
            msgs += 1
            if ok:
                adjustments.append(adj)
                rtts.append(rtt)
    if adjustments:
        avg_adj = sum(adjustments) / len(adjustments)
        avg_rtt = sum(rtts) / len(rtts)
        real_now = datetime.now()
        t0 = datetime.now()
        sync_time = t0 + timedelta(seconds=avg_adj)
        err = abs((sync_time - real_now).total_seconds())
        return msgs, avg_rtt, avg_adj, err
    return msgs, 0, 0, float("inf")

def strategy_rtt_filter():
    candidates = []
    msgs = 0
    for name, cfg in SERVERS.items():
        ok, rtt, adj, err, sdt = sync_with(cfg["port"])
        msgs += 1
        if ok and rtt < RTT_FILTER_THRESHOLD:
            candidates.append((rtt, adj, err))
    if candidates:
        best = min(candidates, key=lambda x: x[0])
        return msgs, best[0], best[1], best[2]
    return msgs, 0, 0, float("inf")

def strategy_drift_predict():
    port = SERVERS["server_a"]["port"]
    history = []
    msgs = 0
    for i in range(3):
        ok, rtt, adj, err, sdt = sync_with(port)
        msgs += 1
        if ok:
            history.append((time_mod.time(), adj, err))
        time_mod.sleep(0.1)
    if len(history) >= 2:
        t1, a1, e1 = history[-2]
        t2, a2, e2 = history[-1]
        dt = t2 - t1
        if dt > 0:
            drift_rate = (a2 - a1) / dt
        else:
            drift_rate = 0
        predicted = a2 + drift_rate * 0.1
        real_now = datetime.now()
        t0 = datetime.now()
        sync_time = t0 + timedelta(seconds=predicted)
        err = abs((sync_time - real_now).total_seconds())
        return msgs, 0, predicted, err
    if history:
        return msgs, 0, history[-1][1], history[-1][2]
    return msgs, 0, 0, float("inf")

def strategy_weighted_avg():
    weights = []
    adjustments = []
    rtts = []
    msgs = 0
    for name, cfg in SERVERS.items():
        ok, rtt, adj, err, sdt = sync_with(cfg["port"])
        msgs += 1
        if ok:
            w = 1.0 / max(rtt, 0.001)
            weights.append(w)
            adjustments.append(adj)
            rtts.append(rtt)
    if weights:
        total_w = sum(weights)
        weighted_adj = sum(w * a for w, a in zip(weights, adjustments)) / total_w
        avg_rtt = sum(rtts) / len(rtts)
        real_now = datetime.now()
        t0 = datetime.now()
        sync_time = t0 + timedelta(seconds=weighted_adj)
        err = abs((sync_time - real_now).total_seconds())
        return msgs, avg_rtt, weighted_adj, err
    return msgs, 0, 0, float("inf")

def main():
    procs = start_servers()
    strategies = {
        "Original Cristian": strategy_original,
        "Multi-Server Best": strategy_multi_best,
        "Multi-Server Avg": strategy_averaging,
        "RTT Filter": strategy_rtt_filter,
        "Drift Prediction": strategy_drift_predict,
        "Weighted Average": strategy_weighted_avg,
    }
    results = {}
    for name, fn in strategies.items():
        errors = []
        rtts = []
        msgs_list = []
        successes = 0
        for trial in range(NUM_TRIALS):
            msgs, rtt, adj, err = fn()
            msgs_list.append(msgs)
            if err < float("inf"):
                successes += 1
                errors.append(err)
                rtts.append(rtt)
        avg_err = sum(errors) / len(errors) if errors else float("inf")
        avg_rtt = sum(rtts) / len(rtts) if rtts else 0
        avg_msgs = sum(msgs_list) / len(msgs_list) if msgs_list else 0
        results[name] = {
            "successes": successes,
            "avg_error": avg_err,
            "avg_rtt": avg_rtt,
            "avg_msgs": avg_msgs,
        }
        print(f"Strategy: {name}")
        print(f"  Successes:     {successes}/{NUM_TRIALS}")
        print(f"  Avg Error:     {avg_err*1000:.1f}ms")
        print(f"  Avg RTT:       {avg_rtt*1000:.1f}ms")
        print(f"  Avg Messages:  {avg_msgs:.1f}")
        print()

    stop_servers(procs)
    print_comparison_table(results)
    plot_results(results)

def print_comparison_table(results):
    print("=" * 95)
    print(f"{'Strategy':<22} {'Success':<12} {'Avg Error':<14} {'Avg RTT':<14} {'Avg Msgs':<12} {'Fault Tol':<12}")
    print("=" * 95)
    for name, r in results.items():
        fault_tol = "High" if r["successes"] == NUM_TRIALS else ("Med" if r["successes"] > NUM_TRIALS * 0.5 else "Low")
        print(f"{name:<22} {r['successes']:<12} {r['avg_error']*1000:<14.1f} {r['avg_rtt']*1000:<14.1f} {r['avg_msgs']:<12.1f} {fault_tol:<12}")
    print("=" * 95)
    print()

def plot_results(results):
    import matplotlib.pyplot as plt

    names = list(results.keys())
    short = ["Original", "Multi-Best", "Multi-Avg", "RTT Filter", "Drift Pred", "Weighted"]
    errors = [results[n]["avg_error"] * 1000 for n in names]
    rtts = [results[n]["avg_rtt"] * 1000 for n in names]
    msgs = [results[n]["avg_msgs"] for n in names]
    successes = [results[n]["successes"] for n in names]

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("Activity 7: Enhanced Synchronization Strategies", fontsize=14, fontweight="bold")
    colors = plt.cm.Set2(range(len(names)))

    axes[0][0].barh(short, errors, color=colors, edgecolor="black")
    axes[0][0].set_title("Avg Synchronization Error")
    axes[0][0].set_xlabel("Error (ms)")
    for i, v in enumerate(errors):
        axes[0][0].text(v + 0.2, i, f"{v:.1f}", va="center", fontweight="bold")

    axes[0][1].barh(short, rtts, color=colors, edgecolor="black")
    axes[0][1].set_title("Avg Round-Trip Time")
    axes[0][1].set_xlabel("RTT (ms)")
    for i, v in enumerate(rtts):
        axes[0][1].text(v + 0.2, i, f"{v:.1f}", va="center", fontweight="bold")

    axes[1][0].barh(short, msgs, color=colors, edgecolor="black")
    axes[1][0].set_title("Avg Messages per Sync")
    axes[1][0].set_xlabel("Messages")
    for i, v in enumerate(msgs):
        axes[1][0].text(v + 0.1, i, f"{v:.1f}", va="center", fontweight="bold")

    axes[1][1].barh(short, successes, color=colors, edgecolor="black")
    axes[1][1].set_title("Successful Synchronizations")
    axes[1][1].set_xlabel("Count")
    axes[1][1].set_xlim(0, NUM_TRIALS + 5)
    for i, v in enumerate(successes):
        axes[1][1].text(v + 1, i, str(v), va="center", fontweight="bold")

    for row in axes:
        for ax in row:
            ax.grid(axis="x", linestyle="--", alpha=0.4)
            ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig("enhanced_strategy_results.png", dpi=150, bbox_inches="tight")
    plt.show()

if __name__ == "__main__":
    main()
