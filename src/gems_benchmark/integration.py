"""EXP04 — Emerald module: system integration.

DelftX System Integration Weeks 0-7:
- Differential-drive kinematics (Week 3): v=(vr+vl)/2, w=(vr-vl)/L; ICC, odometry
- 2R planar arm FK/IK (Week 4)
- Wireless web-control loop budget (Weeks 5-6)
- FDM 3D-print DFM score (Week 2)
- Sustainability / circular-economy score (Comms Week 7 + GEMS sharing platform)

All closed-form, deterministic, unit-tested.
"""
from __future__ import annotations

import math


def diff_drive(vr: float, vl: float, wheel_base_m: float = 0.14) -> dict:
    v = (vr + vl) / 2.0
    w = (vr - vl) / wheel_base_m
    r_icc = v / w if abs(w) > 1e-9 else float("inf")
    return {"v_ms": round(v, 4), "w_rads": round(w, 4), "icc_radius_m": round(r_icc, 4) if r_icc != float("inf") else "inf"}


def diff_drive_odometry(v: float, w: float, dt: float, pose=(0.0, 0.0, 0.0)):
    x, y, th = pose
    x += v * math.cos(th) * dt
    y += v * math.sin(th) * dt
    th += w * dt
    return (round(x, 5), round(y, 5), round(th, 5))


def arm_fk_2r(l1: float, l2: float, th1_deg: float, th2_deg: float) -> dict:
    t1, t2 = math.radians(th1_deg), math.radians(th2_deg)
    x = l1 * math.cos(t1) + l2 * math.cos(t1 + t2)
    y = l1 * math.sin(t1) + l2 * math.sin(t1 + t2)
    return {"x": round(x, 5), "y": round(y, 5)}


def arm_ik_2r(l1: float, l2: float, x: float, y: float) -> dict:
    d2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    d2 = max(-1.0, min(1.0, d2))
    th2 = math.acos(d2)
    th1 = math.atan2(y, x) - math.atan2(l2 * math.sin(th2), l1 + l2 * math.cos(th2))
    reachable = (x * x + y * y) <= (l1 + l2) ** 2 + 1e-9
    return {"th1_deg": round(math.degrees(th1), 2), "th2_deg": round(math.degrees(th2), 2),
            "reachable": reachable}


def control_loop_budget(sensor_ms=4.0, control_ms=3.0, comm_ms=8.0, actuate_ms=2.0) -> dict:
    total = sensor_ms + control_ms + comm_ms + actuate_ms
    return {"total_ms": round(total, 2), "hz": round(1000 / total, 1),
            " realtime_ok_20hz": total <= 50.0}


def dfm_score_3dprint(overhang_deg: float, wall_mm: float, tol_mm: float) -> dict:
    s = 10.0
    if overhang_deg > 45: s -= 3.0
    if wall_mm < 0.8: s -= 3.0
    if tol_mm < 0.1: s -= 2.0
    return {"dfm_0_10": round(max(0.0, s), 1)}


def sustainability_score(reused_pct: float, shared_uses: int, packaging_free: bool) -> dict:
    s = reused_pct * 0.06 + min(shared_uses, 5) * 0.6 + (1.0 if packaging_free else 0.0)
    return {"circular_0_10": round(min(10.0, s), 1)}
