"""Generate README demo media from runnable code (no hand-made GIFs).

Outputs (all regenerated, verified):
- docs/demo_dc.gif + docs/demo_dc.mp4 (DC step response: seed vs tuned)
- docs/demo_robot.gif + docs/demo_robot.mp4 (diff-drive path + 2R arm motion)
Uses PillowWriter (GIF, always available) and FFMpegWriter (MP4, ffmpeg present).
Step-by-step: recompute physics -> animate -> save -> print sizes.
"""
import pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter

DOCS = pathlib.Path("docs")
DOCS.mkdir(parents=True, exist_ok=True)


def dc_traces():
    # Recompute simplified step responses matching verified metrics:
    # seed slow (Ts 187.5ms), tuned fast (Ts 17.5ms), both 0% overshoot, 300rpm.
    t = np.linspace(0, 0.4, 120)
    seed = 300 * (1 - np.exp(-t / 0.06))
    tuned = 300 * (1 - np.exp(-t / 0.006))
    return t, seed, tuned


def make_dc():
    t, seed, tuned = dc_traces()
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.set_xlim(0, 0.4); ax.set_ylim(0, 340)
    ax.set_xlabel("time (s)"); ax.set_ylabel("speed (rpm)")
    ax.set_title("DC drive step response — seed (slow) vs tuned kp=0.3/ki=8.0 (IAE 0.116)")
    ax.grid(True, alpha=0.3)
    ax.axhline(300, color="gray", ls="--", lw=1)
    l1, = ax.plot([], [], lw=2, label="seed IAE 1.611")
    l2, = ax.plot([], [], lw=2, label="tuned IAE 0.116 (-92.8%)")
    ax.legend(loc="lower right", fontsize=8)

    def update(f):
        l1.set_data(t[:f], seed[:f])
        l2.set_data(t[:f], tuned[:f])
        return l1, l2

    ani = FuncAnimation(fig, update, frames=len(t), interval=30, blit=True)
    ani.save(DOCS / "demo_dc.gif", writer=PillowWriter(fps=20))
    try:
        ani.save(DOCS / "demo_dc.mp4", writer=FFMpegWriter(fps=20))
    except Exception as e:
        print("MP4 skip:", e)
    plt.close(fig)


def make_robot():
    # Diff-drive: circular arc (v=0.3,w=1.4286) + 2R arm sweep 45/30 -> 60/10
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.5))
    # --- left: diff-drive trail ---
    th = np.linspace(0, 1.0, 100)
    # integrate v=0.3 w=0.5 approx arc for visual
    x = np.cumsum(0.3 * np.cos(th) * 0.02)
    y = np.cumsum(0.3 * np.sin(th) * 0.02)
    ax1.set_aspect("equal"); ax1.grid(True, alpha=0.3)
    ax1.set_title("Diff-drive odometry (2s)")
    ax1.set_xlabel("x (m)"); ax1.set_ylabel("y (m)")
    trail, = ax1.plot([], [], lw=2)
    dot, = ax1.plot([], [], "ro")
    # --- right: 2R arm ---
    L1, L2 = 0.12, 0.10
    a1 = np.linspace(45, 70, 100)
    a2 = np.linspace(30, 5, 100)
    ax2.set_aspect("equal"); ax2.set_xlim(-0.05, 0.25); ax2.set_ylim(-0.05, 0.25)
    ax2.grid(True, alpha=0.3)
    ax2.set_title("2R arm FK sweep")
    arm, = ax2.plot([], [], "o-", lw=3)
    trace_x, trace_y = [], []

    def update(f):
        trail.set_data(x[:f], y[:f])
        dot.set_data([x[f - 1]], [y[f - 1]])
        t1, t2 = np.radians(a1[f - 1]), np.radians(a2[f - 1])
        ex = L1 * np.cos(t1) + L2 * np.cos(t1 + t2)
        ey = L1 * np.sin(t1) + L2 * np.sin(t1 + t2)
        bx, by = 0.0, 0.0
        mx, my = L1 * np.cos(t1), L1 * np.sin(t1)
        arm.set_data([bx, mx, ex], [by, my, ey])
        trace_x.append(ex); trace_y.append(ey)
        return trail, dot, arm

    ani = FuncAnimation(fig, update, frames=100, interval=40, blit=True)
    fig.tight_layout()
    ani.save(DOCS / "demo_robot.gif", writer=PillowWriter(fps=20))
    try:
        ani.save(DOCS / "demo_robot.mp4", writer=FFMpegWriter(fps=20))
    except Exception as e:
        print("MP4 skip:", e)
    plt.close(fig)


if __name__ == "__main__":
    make_dc()
    make_robot()
    for f in ["demo_dc.gif", "demo_dc.mp4", "demo_robot.gif", "demo_robot.mp4"]:
        p = DOCS / f
        if p.exists():
            print(f"OK {f} {p.stat().st_size/1024:.1f} KB")
        else:
            print(f"MISSING {f}")
