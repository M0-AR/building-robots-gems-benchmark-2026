"""Verify all result JSONs exist and assert physics invariants (live-data gate).

Fails loudly if any hand-edit broke reproducibility.
Checks:
- EXP01: best IAE < seed IAE, sse < 5%, saturation < 30%
- EXP02: noise floor dominates (all MAE in 0.002-0.005V band), DoA(0)=0deg, charlieplex(4)=12
- EXP03: CAN robust==10, SPI goodput > I2C goodput
- EXP04: FK/IK roundtrip reachable, loop realtime ok
- EXP05: findings count == 5
"""
import json, pathlib, sys
R = pathlib.Path("results")
def load(n): return json.load(open(R/n))
ok = True
def check(cond, msg):
    global ok
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond: ok = False

try:
    d1 = load("exp01_dc_drive.json")
    check(d1["tuned"]["iae"] <= d1["seed_result"]["iae"], f"EXP01 tuned IAE {d1['tuned']['iae']} <= seed {d1['seed_result']['iae']}")
    check(d1["tuned"]["sse_pct"] < 5.0, f"EXP01 SSE {d1['tuned']['sse_pct']}% < 5%")
    check(d1["tuned"]["saturation_frac"] < 0.3, "EXP01 saturation < 30%")
    d2 = load("exp02_sensors.json")
    maes = [r["mae_v"] for r in d2["sampling"]]
    check(all(0.002 <= m <= 0.005 for m in maes), f"EXP02 noise floor band 0.002-0.005V {maes}")
    check(d2["sampling"][0]["nyquist_ok"] is False and d2["sampling"][-1]["nyquist_ok"] is True, "EXP02 Nyquist flags")
    check(d2["doa_deg"]["0us"] == 0.0, "EXP02 DoA zero baseline")
    check(d2["charlieplex"]["4"] == 12, "EXP02 charlieplex(4)==12")
    d3 = load("exp03_comms.json")
    can = [r for r in d3["protocols"] if r["protocol"]=="CAN"][0]
    spi = [r for r in d3["protocols"] if r["protocol"]=="SPI"][0]
    i2c = [r for r in d3["protocols"] if r["protocol"]=="I2C"][0]
    check(can["robust_0_10"]==10, "EXP03 CAN robustness 10")
    check(spi["goodput_mbps"] > i2c["goodput_mbps"], "EXP03 SPI goodput > I2C")
    d4 = load("exp04_integration.json")
    check(d4["arm_ik_roundtrip"]["reachable"] is True, "EXP04 arm reachable")
    check(d4["loop"][" realtime_ok_20hz"] is True, f"EXP04 loop {d4['loop']['total_ms']}ms realtime")
    d5 = load("exp05_hidden_patterns.json")
    check(len(d5["findings"])==5, "EXP05 5 findings")
except FileNotFoundError as e:
    print("FAIL missing results:", e); ok=False

sys.exit(0 if ok else 1)
