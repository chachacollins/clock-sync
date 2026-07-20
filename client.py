#!/usr/bin/env python
import socket
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 8080))

    offset = random.randint(-3600, 3600)
    t0 = datetime.now() + timedelta(seconds=offset)

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

    print(f"Initial client clock (T0):       {t0.strftime('%H:%M:%S')}")
    print(f"Server time (T1):                {server_dt.strftime('%H:%M:%S')}")
    print(f"Request time (T0):               {t0.strftime('%H:%M:%S')}")
    print(f"Response time (T2):              {t2.strftime('%H:%M:%S')}")
    print(f"Round-trip delay (RTT):          {rtt:.1f}s")
    print(f"Clock adjustment:                {adjustment:+.1f}s")
    print(f"Final synchronized clock:        {synchronized_time.strftime('%H:%M:%S')}")
    print(f"Synchronization error:           {sync_error:.1f}s")

    # plot_cristian(t0, server_dt, rtt, synchronized_time)

def plot_cristian(now, dt_object, rtt, synchronized_client_time):
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("Cristian's Clock Synchronization Algorithm",
                 fontsize=16, fontweight='bold')

    # ─── Plot 1: Timeline Diagram ─────────────────────────────────────────
    ax1 = axes[0]
    ax1.set_title("Message Timeline", fontsize=13, fontweight='bold', pad=15)

    CLIENT_Y = 1
    SERVER_Y = 3

    # Relative positions on timeline
    now_rel        = 0
    td             = (dt_object - now).total_seconds()
    dt_object_rel  = td
    rtt_rel        = rtt
    sync_rel       = rtt

    x_max = max(dt_object_rel, sync_rel) + 2

    # Draw client and server timelines
    ax1.hlines(CLIENT_Y, -0.5, x_max,
               colors='royalblue', linewidth=2.5, label='Client Timeline')
    ax1.hlines(SERVER_Y, -0.5, x_max,
               colors='tomato', linewidth=2.5, label='Server Timeline')

    # Request arrow: Client (now) → Server (dt_object)
    ax1.annotate(
        '', xy=(dt_object_rel, SERVER_Y), xytext=(now_rel, CLIENT_Y),
        arrowprops=dict(arrowstyle='->', color='green', lw=2)
    )
    ax1.text((now_rel + dt_object_rel) / 2 - 0.3, 2.2,
             'Request\n(→)', color='green', fontsize=9,
             ha='center', style='italic')

    # Response arrow: Server (dt_object) → Client (sync)
    ax1.annotate(
        '', xy=(sync_rel, CLIENT_Y), xytext=(dt_object_rel, SERVER_Y),
        arrowprops=dict(arrowstyle='->', color='purple', lw=2)
    )
    ax1.text((dt_object_rel + sync_rel) / 2 + 0.3, 2.2,
             'Response\n(←)', color='purple', fontsize=9,
             ha='center', style='italic')

    # Key event markers
    events = [
        (now_rel,       CLIENT_Y, f'T0 (now)\n{now.strftime("%H:%M:%S")}',                          'royalblue'),
        (dt_object_rel, SERVER_Y, f'T1 (dt_object)\n{dt_object.strftime("%H:%M:%S")}',              'tomato'),
        (rtt_rel,       CLIENT_Y, f'RTT={rtt}s',                                                    'orange'),
        (sync_rel,      CLIENT_Y, f'Sync\n{synchronized_client_time.strftime("%H:%M:%S")}',         'gold'),
    ]

    for x, y, label, color in events:
        ax1.plot(x, y, 'o', markersize=12, color=color,
                 zorder=5, markeredgecolor='black', markeredgewidth=1.2)
        ax1.text(x, y - 0.4, label, ha='center', fontsize=8,
                 color=color, fontweight='bold')

    # RTT brace
    ax1.annotate(
        '', xy=(sync_rel, CLIENT_Y - 0.6), xytext=(now_rel, CLIENT_Y - 0.6),
        arrowprops=dict(arrowstyle='<->', color='black', lw=1.5)
    )
    ax1.text((now_rel + sync_rel) / 2, CLIENT_Y - 0.82,
             f'td = {td}s  |  RTT = {rtt}s',
             ha='center', fontsize=9,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                       edgecolor='gray'))

    ax1.set_ylim(0, 4.5)
    ax1.set_xlim(-0.5, x_max)
    ax1.set_yticks([CLIENT_Y, SERVER_Y])
    ax1.set_yticklabels(['Client', 'Server'], fontsize=12)
    ax1.set_xlabel('Time (seconds relative to T0)', fontsize=10)
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(axis='x', linestyle='--', alpha=0.4)
    ax1.spines[['top', 'right']].set_visible(False)

    # ─── Plot 2: Clock Comparison Bar Chart ───────────────────────────────
    ax2 = axes[1]
    ax2.set_title("Clock Values Comparison", fontsize=13, fontweight='bold', pad=15)

    def to_seconds(dt):
        return dt.hour * 3600 + dt.minute * 60 + dt.second

    labels = [
        'Client\n(now / T0)',
        'Server\n(dt_object / T1)',
        'Synchronized\n(synchronized_client_time)'
    ]
    values = [
        to_seconds(now),
        to_seconds(dt_object),
        to_seconds(synchronized_client_time)
    ]
    colors = ['royalblue', 'tomato', 'gold']

    bars = ax2.bar(labels, values, color=colors,
                   edgecolor='black', linewidth=1.2, width=0.5)

    # Annotate bars with HH:MM:SS
    time_labels = [
        now.strftime("%H:%M:%S"),
        dt_object.strftime("%H:%M:%S"),
        synchronized_client_time.strftime("%H:%M:%S"),
    ]
    for bar, label in zip(bars, time_labels):
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.5,
                 label, ha='center', va='bottom',
                 fontsize=9, fontweight='bold')

    # td and rtt annotation box
    ax2.text(0.98, 0.05,
             f'td  (T1 - T0) = {td}s\nRTT = td // 2 = {rtt}s',
             transform=ax2.transAxes, fontsize=10,
             verticalalignment='bottom', horizontalalignment='right',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow',
                       edgecolor='gray', alpha=0.9))

    ax2.set_ylabel('Seconds since midnight', fontsize=10)
    ax2.set_ylim(min(values) - 5, max(values) + 5)
    ax2.grid(axis='y', linestyle='--', alpha=0.4)
    ax2.spines[['top', 'right']].set_visible(False)

    legend_patches = [
        mpatches.Patch(color='royalblue', label='now (Client T0)'),
        mpatches.Patch(color='tomato',    label='dt_object (Server T1)'),
        mpatches.Patch(color='gold',      label='synchronized_client_time'),
    ]
    ax2.legend(handles=legend_patches, fontsize=9, loc='upper left')

    plt.tight_layout()
    plt.savefig('cristian_clock.png', dpi=150, bbox_inches='tight')
    plt.show()
if __name__ == '__main__':
    main()

