# From Components to Robots: A Reproducible Benchmark of the GEMS Modular Mechatronics Curriculum — With Hidden Cross-Module Patterns

**Authors:** Independent Reproduction Study (code + data: this repo) · **Date:** 2026-10-04 · **Status:** preprint draft, all results recomputed live

## Abstract
The Erasmus+ GEMS program (*Graceful Equalising of Mechatronics Students*,
KA220-HED 2022-1-SI01-KA220-HED-000087727) pairs affordable open-source hardware
(Diamond/Ruby/Sapphire/Emerald) with four DelftX MOOCs to teach full-stack robot
building. We reproduce the entire pipeline — DC drive closed-loop control,
sensor data acquisition, communication/ROS selection, and system integration —
as deterministic, hardware-free benchmarks in a Docker replication package.
Verified results (10/10 unit tests, 12/12 verification checks, live-fetch of
GEMS + OpenAlex OK): (1) empirical PI grid beats modulus-optimum seed by 92.8%
IAE with zero overshoot; (2) 50× sampling-rate increase buys only 1.01× MAE
improvement — noise floor dominates; (3) CAN wins motor-bus despite 163× lower
goodput than WiFi; (4) wireless comm is 47% of the 17 ms control loop;
(5) exact arm FK/IK roundtrip vs drifting open-loop odometry quantifies why
sensing+comms must close the loop. We contribute the first end-to-end
reproducible artifact for the GEMS curriculum and five pre-registered,
quantified hidden patterns with direct design levers.

**Keywords:** mechatronics education, GEMS, DC drives, sensor acquisition,
communication protocols, ROS 2, system integration, reproducible benchmarking, Docker.

## 1. Introduction
Mechatronics education suffers from unequal hardware access (GEMS motivation:
lab-only tutorials exclude learners with divergent needs). GEMS answers with
personal modular hardware + MOOCs + sharing/recycling platform. Prior work
validates pieces — cascade PI for DC education (Gaiceanu), differential-drive
as DC control (Mahfouz), open-source platforms in robotics education (Lotfi et
al.), hardware benchmarks (DeepClaw), reproducible robotics infra (SwarmRob,
CSAR 2026, open-navigation workload benchmark) — but no study spans all four
GEMS courses with runnable verification. We close that gap.

**Contributions:** (C1) faithful curriculum→code mapping; (C2) 5 deterministic
experiments + strict verifier + Docker compose; (C3) 5 quantified hidden
patterns; (C4) full negative-results search log (20 sequential queries).

## 2. Background: program and hardware (ground truth)
Verified via live `webfetch https://gems-erasmus.eu/hardware/`:
Diamond (H-bridge/PWM motion), Ruby (2-mic sound/ultrasound sensing), Sapphire
(comms centre), Emerald (battery + DC+CAN flat cable), plus Drivetrain
(oversized 3-stage), wheeled Robots (2×GEMS), Amethyst (ESP32-C3 light/RGB),
Citrine (SMD trainer). Courses: Electrical Drives (equivalent circuit →
converter → open loop → PI → empirical deploy); Sensors (architecture →
calibration → sampling/noise → Ruby charlieplex/ultrasound → DoA design);
Comms (serial → wireless → hardware → ROS topics/services/actions → real-time/
fault-tolerance → sustainability); Integration (specs → FDM DFM → diff-drive →
2R arm → assemble/control/improve wireless robot).

## 3. Methods
See `docs/METHODS.md` for equations. Summary: DC V=R·i+L·di/dt+Ke·ω,
J·dω/dt+b·ω=Kt·i−Tload, Vapp=(2D−1)Vbus; discrete PI + anti-windup, dt=0.5 ms,
300 rpm, 2 mNm; 5×5 grid. ADC 12-bit/3.3 V/σ4 mV seeded; fs sweep on 50 Hz tone;
LS calibration; ultrasound/DoA physics; charlieplex n(n−1). Protocol goodput =
clock×efficiency (2026 comparison-anchored); ROS latencies topic 0.6/service
1.8/action 2.6 ms. Diff-drive + 2R FK/IK closed forms; 17 ms loop budget; DFM
and circular scores. EXP05 pre-registered H1–H4, emergent H5, fixed seeds/grids.

## 4. Results (all verified 2026-10-04)

### 4.1 EXP01 DC drive — `results/exp01_dc_drive.json`, `figures/exp01_grid.png`
Seed (kp=0.02, ki=0.5762): IAE 1.61142, Ts 187.5 ms. Grid best (kp=0.3, ki=8.0):
**IAE 0.11606, overshoot 0.0%, Ts 17.5 ms, SSE 0.0%, saturation 0.0%** (n=25).
Mean-by-ki: overshoot 0.0/0.192/1.271/3.725/7.752%; IAE
0.9187/0.4701/0.339/0.251/0.2243. Improvement **92.8%**.

### 4.2 EXP02 Sensors — `results/exp02_sensors.json`, `figures/exp02_sampling.png`
fs 100/500/1000/5000 Hz → MAE 0.00326/0.00268/0.00358/0.00322 V; Nyquist flags
F/T/T/T. Calibration gain 1.02041, offset −0.02041, RMSE 0.0. Ultrasound
3 ms→0.5148 m, 6 ms→1.0296 m. DoA 0/87/174 µs → 0.0/29.85/84.46°.
Charlieplex 3/4/5/8 → 6/12/20/56.

### 4.3 EXP03 Comms — `results/exp03_comms.json`, `figures/exp03_goodput.png`
Goodput Mbps: WiFi 90.0, SPI 46.0, RS-485 8.2, I2C 2.55, BLE 1.3, CAN 0.55,
UART 0.092. Robustness CAN 10/10. Picks: motor-bus CAN, encoder SPI, debug UART,
PC-link WiFi, graph ROS 2 topics.

### 4.4 EXP04 Integration — `results/exp04_integration.json`
Diff sweep: (0.3,0.3)→v0.3/w0.0; (0.4,0.2)→v0.3/w1.4286/ICC0.21;
(0.3,−0.3)→spin w4.2857; (0.5,0.5)→v0.5. Odometry 2 s → (0.50832, 0.26947,
1.0 rad). Arm FK (L1=0.12, L2=0.10, 45°/30°) → (0.11073, 0.18145); IK recovers
(45.0°, 30.0°) reachable. Loop 17.0 ms / 58.8 Hz OK. DFM 7.0, circular 6.4.

### 4.5 EXP05 Hidden patterns — `results/exp05_hidden_patterns.json`
H1 tradeoff + boundary optimum; H2 noise-floor surprise (×1.01, non-monotonic);
H3 throughput inversion (163×); H4 comm bottleneck (47%); H5 thesis-in-one-number
(exact IK vs drifting odometry). Exact wordings in JSON findings[].

## 5. Discussion: design levers
(1) Always follow model tune with empirical grid — and extend past the boundary
with saturation/thermal guards. (2) Spend sensing budget on analog front-end +
calibration, not fs beyond ~500 Hz for quasi-static signals. (3) Choose buses by
robustness/topology, not Mbps. (4) Localize control on ESP32; use ROS 2 topics
for streams, actions for goals. (5) Teach integration via the odometry-vs-IK
contrast — it motivates closing the loop in one lab session. Sustainability:
60% reuse + 3 shares + packaging-free → 6.4/10; the GEMS sharing platform is
the highest-leverage green lever.

## 6. Threats to validity
Simulation-only (no HIL yet — interfaces ready); small-motor params;
order-of-magnitude comm/ROS numbers (transparent formulas, not datasheets);
deterministic seeds understate real EMI variance; single 2R arm geometry.
Mitigations: strict verifier, live-fetch gate, negative-results log, fixed
grids, Docker pinning (`python:3.11-slim`, pinned requirements).

## 7. Related work
Gaiceanu cascade-PI education; Mahfouz diff-drive-as-DC-control; Lotfi
open-source hardware education; DeepClaw/RPX/OpenNav benchmarks; SwarmRob/CSAR
reproducibility; RobotForge/SmashingRobotics/thomasthelliez protocol guides;
StackOverflow differential-PID practice; OpenAlex modular/teleop systems.
Full per-query log in `docs/SOURCES.md`.

## 8. Replication package
`docker compose up --build` or `make test run verify`. Artifacts:
`src/gems_benchmark/*`, `experiments/*/run.py`, `scripts/*`,
`tests/test_benchmark.py` (10 tests), `data/public/live_snapshot.json`,
`results/*.json + figures/*.png`. License for code: MIT (suggested); data:
CC-BY (GEMS CC ethos). Next: HIL on real Diamond/Ruby/Sapphire/Emerald +
Zenodo rosbags + preregistered ki>8 extension.

## References (abridged; full URLs in SOURCES.md)
GEMS hardware/program pages; DelftX 4-course syllabi; Gaiceanu ch. Embedded
Control of DC Drive; Samak et al. Nigel; Lotfi et al. ASEE; Mahfouz et al.
IJISA; Gaspar et al. RCIM; DeepClaw arXiv:2005.02588; Padilla-García Processes
2026; CSAR arXiv:2606.30293; open-navigation workload benchmark; SwarmRob;
RobotForge/SmashingRobotics/thomasthelliez 2026 protocol comparisons.
