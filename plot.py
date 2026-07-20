import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_cristian(now, dt_object, td, rtt, synchronized_client_time):
    fig, axes = plt.subplots(1, 1, figsize=(16, 9))
    fig.suptitle("Cristian's Clock Synchronization Algorithm",
                 fontsize=16, fontweight='bold')

    ax1 = axes
    ax1.set_title("Message Timeline", fontsize=13, fontweight='bold', pad=15)

    CLIENT_Y = 1
    SERVER_Y = 3

    # Relative positions on timeline
    now_rel        = 0
    dt_object_rel  = td          
    rtt_rel        = rtt        
    sync_rel       = td + rtt  

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
             'Request\n(→)', color='green', fontsize=10,
             ha='center', style='italic')

    # Response arrow: Server (dt_object) → Client (sync)
    ax1.annotate(
        '', xy=(sync_rel, CLIENT_Y), xytext=(dt_object_rel, SERVER_Y),
        arrowprops=dict(arrowstyle='->', color='purple', lw=2)
    )
    ax1.text((dt_object_rel + sync_rel) / 2 + 0.3, 2.2,
             'Response\n(←)', color='purple', fontsize=10,
             ha='center', style='italic')

    # Key event markers
    events = [
        (now_rel,       CLIENT_Y, f'T0 (now)\n{now.strftime("%H:%M:%S")}',                          'black'),
        (dt_object_rel, SERVER_Y, f'T1 (dt_object)\n{dt_object.strftime("%H:%M:%S")}',              'black'),
        (rtt_rel,       CLIENT_Y, f'RTT={rtt}s',                                                    'black'),
        (sync_rel,      CLIENT_Y, f'Sync\n{synchronized_client_time.strftime("%H:%M:%S")}',         'black'),
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
             ha='center', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                       edgecolor='gray'))

    ax1.set_ylim(0, 4.5)
    ax1.set_xlim(-0.5, x_max)
    ax1.set_yticks([CLIENT_Y, SERVER_Y])
    ax1.set_yticklabels(['Client', 'Server'], fontsize=12)
    ax1.set_xlabel('Time (seconds relative to T0)', fontsize=10)
    ax1.legend(loc='upper right', fontsize=10)
    ax1.grid(axis='x', linestyle='--', alpha=0.4)
    ax1.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    plt.savefig('cristian_clock.png', dpi=150, bbox_inches='tight')
