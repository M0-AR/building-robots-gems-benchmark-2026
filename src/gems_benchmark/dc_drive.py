"""EXP01 — Diamond module: DC electrical drive model + closed-loop PI control.

Verifiable physics, no hardware required:
- DC machine equivalent circuit: V = R*i + L*di/dt + Ke*omega
- Mechanical: J*dw/dt + b*w = Kt*i - T_load
- H-bridge averaged model: V_applied = (2*D - 1) * Vbus
- Discrete PI with anti-windup, modulus-optimum seed + empirical grid refinement
- Metrics: overshoot, settling time, IAE, steady-state error, PWM saturation fraction

References (verified online 2026-10-04):
- GEMS Diamond module: H-bridge + PWM + reference/measurement control loop
- DelftX Week2-6 curriculum: equivalent circuit -> power converter -> open loop -> PI tune -> empirical deploy
- Gaiceanu "Embedded Control of DC Drive System for Education" (cascade PI, Z-transform, modulus/symmetric optimum)
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class DCMotorParams:
    R: float = 2.2       # Ohm (small educational motor, GEMS-class)
    L: float = 0.0018    # H
    Ke: float = 0.021    # V/(rad/s)
    Kt: float = 0.021    # Nm/A (SI: Kt == Ke)
    J: float = 7.5e-06   # kg*m^2 rotor + small gearbox reflected
    b: float = 1.8e-05   # Nm/(rad/s) viscous friction
    Vbus: float = 12.0   # V Emerald supply
    pwm_freq: float = 20000.0  # Hz


@dataclass
class PIParams:
    kp: float
    ki: float
    out_min: float = -12.0
    out_max: float = 12.0


def steady_state_current(voltage: float, omega: float, p: DCMotorParams) -> float:
    """I = (V - Ke*w)/R — direct from equivalent circuit (DelftX Week 2)."""
    return (voltage - p.Ke * omega) / p.R


def simulate_closed_loop(
    p: DCMotorParams,
    pi: PIParams,
    ref_rpm: float = 300.0,
    t_end: float = 1.0,
    dt: float = 0.0005,
    load_nm: float = 0.002,
) -> dict:
    """Simulate speed loop with discrete PI. Returns trace metrics (deterministic)."""
    ref = ref_rpm * 2.0 * math.pi / 60.0
    omega = 0.0
    i = 0.0
    integ = 0.0
    n = int(t_end / dt)
    iae = 0.0
    peak = 0.0
    saturated = 0
    trace_w = []
    for k in range(n):
        err = ref - omega
        integ += err * dt
        # anti-windup clamp
        integ = max(min(integ, pi.out_max / max(pi.ki, 1e-9)), pi.out_min / max(pi.ki, 1e-9))
        v_cmd = pi.kp * err + pi.ki * integ
        v_sat = max(min(v_cmd, pi.out_max), pi.out_min)
        if v_sat != v_cmd:
            saturated += 1
        # electrical + mechanical Euler integration (stable at dt=0.5ms)
        di = (v_sat - p.R * i - p.Ke * omega) / p.L * dt
        i += di
        dw = (p.Kt * i - p.b * omega - load_nm) / p.J * dt
        omega += dw
        iae += abs(err) * dt
        peak = max(peak, omega)
        if k % 4 == 0:
            trace_w.append(omega)
    # metrics
    overshoot = max(0.0, (peak - ref) / ref * 100.0) if ref > 0 else 0.0
    # settling: last time |err| > 2%
    settle_idx = n
    for k in range(n - 1, -1, -1):
        w = trace_w[min(k // 4, len(trace_w) - 1)]
        if abs(w - ref) / ref > 0.02:
            settle_idx = k
            break
    settling_time = settle_idx * dt
    sse = abs(trace_w[-1] - ref) / ref * 100.0
    return {
        "ref_rpm": ref_rpm,
        "kp": pi.kp,
        "ki": pi.ki,
        "overshoot_pct": round(overshoot, 3),
        "settling_time_s": round(settling_time, 4),
        "iae": round(iae, 5),
        "sse_pct": round(sse, 3),
        "saturation_frac": round(saturated / n, 4),
        "final_rpm": round(trace_w[-1] * 60 / (2 * math.pi), 2),
    }


def modulus_optimum_seed(p: DCMotorParams) -> PIParams:
    """Textbook modulus-optimum style seed for current/speed cascade simplified to single speed loop.

    Chosen to be stable for GEMS-class parameters; grid search refines empirically
    (mirrors DelftX Week 5 -> Week 6: model tune -> empirical stepwise tune).
    """
    kp = (p.R * p.J) / (p.Kt * 0.004)
    ki = kp * (p.R / p.L) * 0.12
    # scale to sane range for 12V / 300rpm regime
    kp = max(0.02, min(kp * 0.02, 0.6))
    ki = max(0.5, min(ki * 0.02, 8.0))
    return PIParams(kp=round(kp, 4), ki=round(ki, 4))


def grid_tune(p: DCMotorParams, ref_rpm: float = 300.0) -> dict:
    """Empirical stepwise tuning over small deterministic grid (DelftX Week 6 method)."""
    best = None
    rows = []
    for kp in [0.05, 0.1, 0.15, 0.2, 0.3]:
        for ki in [1.0, 2.0, 3.0, 5.0, 8.0]:
            m = simulate_closed_loop(p, PIParams(kp=kp, ki=ki), ref_rpm=ref_rpm)
            score = m["iae"] + 0.1 * m["overshoot_pct"] + 0.5 * m["settling_time_s"]
            rows.append({**m, "score": round(score, 5)})
            if best is None or score < best["score"]:
                best = {**m, "score": round(score, 5)}
    return {"best": best, "grid": rows}
