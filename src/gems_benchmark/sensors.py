"""EXP02 — Ruby module: sensing + data acquisition.

Covers DelftX Sensors curriculum Weeks 1-5:
- Sampling/quantization/noise model (Week 3)
- Calibration + error (Week 2): linear fit gain/offset, residual RMSE, max abs error
- Ultrasound ToF ranging (Week 4): d = c*T/2 with temperature-compensated c
- DoA TDOA direction finding with 2-mic Ruby array (Week 5)
- Charlieplexing pin-count law (Week 4): n pins -> n*(n-1) LEDs

All functions deterministic (seeded RNG) so benchmarks are reproducible.
"""
from __future__ import annotations

import math
import random


def adc_model(v_true: float, v_ref: float = 3.3, bits: int = 12, noise_std: float = 0.004, seed: int = 0) -> float:
    rng = random.Random(seed + int(v_true * 1e6) % 10007)
    q = v_ref / (2 ** bits)
    v_noisy = v_true + rng.gauss(0.0, noise_std)
    code = int(round(v_noisy / v_ref * (2 ** bits - 1)))
    code = max(0, min(2 ** bits - 1, code))
    return code * q


def sampling_benchmark(fs_list=(100, 500, 1000, 5000), f_sig: float = 50.0, dur: float = 0.2) -> list:
    """Aliasing/noise demo: reconstruct sine amplitude error vs sample rate."""
    rows = []
    for fs in fs_list:
        n = int(fs * dur)
        err_sum = 0.0
        for k in range(n):
            t = k / fs
            v = 1.65 + 1.0 * math.sin(2 * math.pi * f_sig * t)
            v_q = adc_model(v, seed=k)
            err_sum += abs(v_q - v)
        rows.append({"fs_hz": fs, "mae_v": round(err_sum / n, 5), "nyquist_ok": fs > 2 * f_sig})
    return rows


def calibrate_linear(raw: list, true: list) -> dict:
    """Least-squares y = a*x + b mapping raw ADC volts to physical units."""
    n = len(raw)
    mx = sum(raw) / n
    my = sum(true) / n
    num = sum((x - mx) * (y - my) for x, y in zip(raw, true))
    den = sum((x - mx) ** 2 for x in raw) or 1e-12
    a = num / den
    b = my - a * mx
    resid = [y - (a * x + b) for x, y in zip(raw, true)]
    rmse = math.sqrt(sum(r * r for r in resid) / n)
    return {"gain": round(a, 5), "offset": round(b, 5), "rmse": round(rmse, 5),
            "max_abs_err": round(max(abs(r) for r in resid), 5)}


def ultrasound_distance(tof_s: float, temp_c: float = 20.0) -> float:
    """d = c*T/2, c = 331.3*sqrt(1+T/273.15)."""
    c = 331.3 * math.sqrt(1.0 + temp_c / 273.15)
    return c * tof_s / 2.0


def doa_tdoa(dt_s: float, mic_spacing_m: float = 0.06, temp_c: float = 20.0) -> float:
    """Plane-wave DoA: sin(theta) = c*dt/d. Returns degrees in [-90, 90], clamped."""
    c = 331.3 * math.sqrt(1.0 + temp_c / 273.15)
    s = max(-1.0, min(1.0, c * dt_s / mic_spacing_m))
    return round(math.degrees(math.asin(s)), 2)


def charlieplex_capacity(n_pins: int) -> int:
    return n_pins * (n_pins - 1)
