# Methods — zero to hero, everything recomputed

## EXP01 Diamond / DC drive (`src/gems_benchmark/dc_drive.py`)
V = R·i + L·di/dt + Ke·ω; J·dω/dt + b·ω = Kt·i − Tload; Vapp = (2D−1)·Vbus.
Params: R=2.2Ω, L=1.8mH, Ke=Kt=0.021, J=7.5e-6, b=1.8e-5, Vbus=12V, 20kHz PWM.
Discrete PI + anti-windup, dt=0.5ms, 300rpm, 2mNm load. Modulus-optimum seed
(kp=0.02, ki=0.5762) then deterministic 5×5 grid kp∈{0.05..0.3}×ki∈{1..8}
(DelftX W5→W6: model tune → empirical stepwise tune). Score = IAE + 0.1·OS + 0.5·Ts.

## EXP02 Ruby / Sensors (`sensors.py`)
12-bit ADC (3.3Vref, σ=4mV, seeded RNG). Sampling benchmark: 50Hz tone, fs∈{100,500,1000,5000}.
Calibration: least-squares y=ax+b. Ultrasound d=cT/2, c=331.3√(1+T/273.15).
DoA plane-wave sinθ=c·Δt/d, d=60mm. Charlieplex n(n−1).

## EXP03 Sapphire / Comms (`comms.py`)
Goodput = clock×payload_eff; frame time for 8B. Table values from 2026 comparisons
(RobotForge/SmashingRobotics/thomasthelliez), encoded as transparent formulas.
ROS primitives: topic 0.6ms / service 1.8ms / action 2.6ms (order-of-magnitude model).
Decision rules: motor-bus→CAN, encoder→SPI, debug/GPS→UART, PC-link→WiFi, graph→ROS2 topics.

## EXP04 Emerald / Integration (`integration.py`)
Diff-drive v=(vr+vl)/2, ω=(vr−vl)/L (L=0.14m); Euler odometry. 2R arm FK closed-form;
IK acos-clamped + reachable flag. Loop budget 4+3+8+2=17ms → 58.8Hz (>20Hz OK).
FDM DFM 10−penalties; circular score 0.06·reused% +0.6·min(shares,5)+packaging.

## EXP05 Hidden patterns (`experiments/exp05_hidden_patterns/run.py`)
Pre-registered H1–H4 + emergent H5. Recomputes grid (no p-hacking, fixed seeds),
reports effect sizes with exact verified numbers. See results/exp05_hidden_patterns.json.

## Live-data gate (`scripts/fetch_live_data.py`, `scripts/verify.py`)
Fetch is best-effort cached; verify is strict and offline. `make test run verify`
must all pass. Docker reproduces same via `docker compose up --build`.
