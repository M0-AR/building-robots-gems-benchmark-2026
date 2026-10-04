# 🤖 Building Robots (GEMS): Reproducible Mechatronics Benchmark 2026

> Open-source robotics integration — from DC drives to wireless robots — with runnable benchmarks, demos, and a publishable study. No hardware required.

[![License MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](pyproject.toml)
[![Docker ready](https://img.shields.io/badge/Docker-ready-blue.svg)](docker-compose.yml)
[![Tests 10 passing](https://img.shields.io/badge/tests-10_passing-brightgreen.svg)](tests/test_benchmark.py)
[![Verify 12 checks](https://img.shields.io/badge/verify-12_checks-brightgreen.svg)](scripts/verify.py)

📖 **Live visual summary:** open [`docs/preview.html`](docs/preview.html) in your browser (works offline).
🖼️ Preview screenshot: [`docs/preview_shot.png`](docs/preview_shot.png) · Full page: [`docs/preview_full.png`](docs/preview_full.png)

---

## 0. Executive summary — read this in 60 seconds and you understand the whole repo

**What this is:** a complete, runnable reproduction of the 4-course *Building Robots: from Mechatronic Components to Robotics* program (Electrical Drives · Sensors & Data Acquisition · Communication Protocols + ROS · System Integration) built around modular educational hardware (Diamond = motion, Ruby = sensing, Sapphire = comms, Emerald = power + integration).

**Why it matters in 5 numbers (all recomputed by code, verified 2026-10-04):**

1. DC motor tuning improves **92.8%** — error integral 1.611 → **0.116**, zero overshoot, settles in **17.5 ms**.
2. Sensor sampling hits a wall — 100 Hz error 0.00326 V vs 5000 Hz 0.00322 V (**×1.01 for ×50 cost**). Noise, not speed, rules.
3. The **slowest bus wins** the motor network — CAN at 0.55 Mbps beats WiFi at 90 Mbps on reliability (10/10) and wiring.
4. The control loop runs at **58.8 Hz (17 ms)** — and **47% is just wireless communication**, not math.
5. The arm math is **exact** (45.0°/30.0° recovered) while open-loop driving **drifts** — proving sensors + comms must close the loop around motors.

**What you can do in 3 commands:**

```bash
docker compose up --build
# or:
pip install -r requirements.txt && python scripts/run_all.py && python scripts/verify.py
```

**Who this serves:** students without lab access, teachers needing auto-graded labs, hobbyists sizing real builds, ROS 2 developers choosing topics vs services vs actions, and researchers needing a replication package for a publication.

---

## 🎬 Demos — watch it before you read it

> Best practice: one demo above the fold, under 5 MB, generated from code — never hand-recorded.

| Demo | GIF (loops everywhere) | Video (smooth) | What you see |
|---|---|---|---|
| DC step to 300 rpm | ![DC demo](docs/demo_dc.gif) | <video src="docs/demo_dc.mp4" controls width="100%"></video> [demo_dc.mp4](docs/demo_dc.mp4) | Slow beginner tuning vs tuned kp=0.3/ki=8.0 converging fast with no overshoot |
| Robot motion | ![Robot demo](docs/demo_robot.gif) | <video src="docs/demo_robot.mp4" controls width="100%"></video> [demo_robot.mp4](docs/demo_robot.mp4) | Left: differential-drive trail · Right: 2-joint arm sweep with exact kinematics |

Regenerate anytime (deterministic):

```bash
python scripts/make_demo.py
ls -lh docs/demo*   # 4 files, GIFs <500 KB each
```

Terminal quick-tour (copy-paste, 60 seconds):

```bash
python scripts/fetch_live_data.py   # live source check, cached, never blocks
python scripts/run_all.py           # 5 experiments → results/*.json + figures
python scripts/verify.py            # 12 strict PASS lines, exit 0
pytest -q                           # 10 passed
python scripts/screenshot.py        # re-shoots docs/preview_shot.png
```

---

## 🌱 Beginner guide — read this and you are a professional

> You will know more than most interview candidates. Let's work this out in a step-by-step way to be sure we have the right answer.

### Step 1 — What is a robot, really?
Mechanics + electronics + software agreeing **58 times per second**. Miss the deadline and the robot wobbles. This repo proves 58.8 Hz end-to-end. Every later section is just defending that number.

**Takeaway:** robotics = meeting a timer, not just writing code.

### Step 2 — Motion: making a motor obey (Diamond)
A DC motor is a resistor + coil + spinning magnet:

- Voltage pushes current: `V = R·i + L·di/dt + Ke·ω`
- Current pushes twist: `J·dω/dt + b·ω = Kt·i − load`
- A chip (H-bridge) chops 12 V into pulses 20,000×/s (PWM). Wider pulses = more push.

A **PI controller** watches speed error and adjusts voltage: `P` reacts now, `I` remembers the past. Too little I = sluggish (IAE 1.611). Just right (kp=0.3, ki=8.0) = IAE **0.116**, settles in **0.0175 s**, no overshoot, no saturation.

**Try it:** open `src/gems_benchmark/dc_drive.py`, change `kp`, rerun `experiments/exp01_dc_drive/run.py`, watch `results/figures/exp01_grid.png` move.

### Step 3 — Sensing: trusting measurements (Ruby)
Sensors always lie a little. Our 12-bit sensor lies by ~0.003 V (noise + steps).

- **Sampling faster does not fix lying.** 100 Hz → 0.00326 V, 5000 Hz → 0.00322 V. Best is 500 Hz. The floor is physics.
- **Calibrate:** fit `true = gain·raw + offset` (here gain 1.02041, offset −0.02041, error 0.0 on clean data).
- **Ultrasound:** shout, time the echo. 6 ms echo = **1.0296 m** (`d = c·T/2`).
- **Direction:** two ears 6 cm apart. 87 µs delay = sound from **29.85°**.
- **Wiring trick:** 4 pins control 12 LEDs (`n·(n−1)` — charlieplexing).

**Try it:** run `experiments/exp02_sensors/run.py`, check `results/figures/exp02_sampling.png` flatten.

### Step 4 — Talking: wires and radio (Sapphire)
One robot speaks 6 languages. Rule of thumb proven in code:

| Job | Pick | Why (measured) |
|---|---|---|
| Motor bus (daisy-chain, noisy factory) | **CAN** 0.55 Mbps | Arbitration + error check + 500 m + robustness 10/10 |
| Joint encoder (short, fast) | **SPI** 46.0 Mbps | Full-duplex speed, 1.39 µs/frame |
| Debug / GPS (simple) | **UART** 0.092 Mbps | 2 wires, no setup pain |
| PC link (bulk data) | **WiFi** 90.0 Mbps | 0.71 µs/frame, accepts jitter |
| Software graph (ROS 2) | **topics** 0.6 ms | Streams; services 1.8 ms for settings; actions 2.6 ms for goals |

**Takeaway:** fastest ≠ fittest. Reliability × topology wins.

### Step 5 — Assembly: putting it together (Emerald)
Battery + cables + 3D-printed frame + two wheels + arm + web buttons.

- Drive straight: both wheels 0.3 m/s → forward 0.3, spin 0.0.
- Spin in place: left +0.3, right −0.3 → spin **4.29 rad/s**.
- 2 s blind drive ends at **(0.508, 0.269, 1.0 rad)** — drift is why you need sensors.
- Arm forward `(45°,30°)` → tip **(0.11073, 0.18145)**; inverse returns **exact (45.0°,30.0°)**.
- Loop: sense 4 + think 3 + **talk 8** + move 2 = **17 ms**. Talk is the bottleneck — move brains onto the robot.
- Plastic check DFM **7.0/10**, reuse score **6.4/10** (60% reused + shared 3× + no packaging).

### Step 6 — Prove it like a professional
Professionals do not claim — they show a green check:

```bash
pytest -q && python scripts/run_all.py && python scripts/verify.py
# must see: 10 passed · ALL EXPERIMENTS OK · 12× PASS
```

If any number is hand-edited, verification fails. That is the whole culture of this repo.

---

## ✨ Features — everything in one table

| Area | What you get | File to open first |
|---|---|---|
| DC drive lab | Equivalent-circuit model, PWM average, discrete PI + anti-windup, modulus seed + 25-point grid, overshoot/settle/IAE/saturation metrics | `src/gems_benchmark/dc_drive.py` |
| Sensor lab | ADC + noise model, sampling sweep, linear calibration, ultrasound ToF, 2-mic DoA, charlieplex law | `src/gems_benchmark/sensors.py` |
| Comms lab | 7-protocol goodput/robustness table, ROS topic/service/action chooser, motor/encoder/debug/PC decision rules | `src/gems_benchmark/comms.py` |
| Integration lab | Diff-drive + odometry, 2R FK/IK, loop budget, FDM DFM score, circular-economy score | `src/gems_benchmark/integration.py` |
| Hidden patterns | 5 quantified cross-module findings with effect sizes | `results/exp05_hidden_patterns.json` |
| Demos | 2 GIFs + 2 MP4s from physics, no screen recorder | `scripts/make_demo.py` |
| Visual summary | Beautiful offline `preview.html` + Playwright screenshots | `docs/preview.html` |
| Verification | 10 unit tests + 12 strict checks + live-source gate | `scripts/verify.py` |
| Docker | One-command repro (`gems-benchmark` + `gems-verify` services) | `docker-compose.yml` |
| Publication | Full IMRaD draft + methods + sources + reproducibility notes | `docs/PAPER.md` |

![Benchmark figures](results/figures/exp01_grid.png)
![Sampling figure](results/figures/exp02_sampling.png)
![Protocol figure](results/figures/exp03_goodput.png)

---

## 🧑‍💻 User stories — who uses this and how

### 1. Engineering student (no hardware, self-paced, 4–6 h/week)
**Goal:** finish all 4 courses with intuition + numbers.
**Path:** Beginner guide → run EXP01→EXP04 in order → tweak one knob per lab (ki, fs, protocol, wheel base) → write 1 paragraph per hidden pattern. You will finish able to: size a drive, calibrate a sensor, pick a bus, budget a loop, and defend integration trade-offs in an interview.

### 2. Teacher / teaching assistant
**Goal:** 5 auto-graded labs.
**Path:** assign each `experiments/exp0*/run.py` as a lab; grade with `scripts/verify.py` (12 checks = rubric) + `pytest -q`. No lab hardware needed for the simulation track; swap in real Diamond/Ruby drivers later behind the same function names.

### 3. Hobbyist building a small rover or arm
**Goal:** stop guessing parts.
**Path:** use EXP01 to pick PI gains for your motor (start kp=0.15–0.3, ki=2–8); EXP02 to set sampling ~500 Hz and calibrate; EXP03 to wire motors CAN + encoders SPI + debug UART; EXP04 to check your wheel base math and 3D-print clearances before printing.

### 4. ROS 2 / embedded developer
**Goal:** choose the right primitive and bus.
**Path:** `protocol_table()` + `ros_choice_table()` give latencies and topologies. Rule encoded: streams→topics, settings→services, long goals→actions. Loop budget shows when to move control from web UI to on-board ESP32.

### 5. Researcher / PhD student
**Goal:** publishable extension.
**Path:** `docs/PAPER.md` is a complete draft. Extend H1 past ki=8 with thermal/saturation guards, replace simulated drivers with hardware-in-the-loop, log rosbags, and you have a journal empirical study. All seeds, grids, and checks are fixed to prevent p-hacking.

### 6. Hiring manager / interviewer
**Goal:** 5-minute seniority probe.
**Path:** ask “Why did 50× sampling buy 1% accuracy?” (noise floor), “Why does the slowest bus win?” (robustness), “Where is the 17 ms spent?” (comm). Answers are in EXP05 with exact numbers.

---

## 📊 Full results — every number, no adjectives

### EXP01 — DC drive (`results/exp01_dc_drive.json`)
Motor: R 2.2 Ω · L 1.8 mH · Ke=Kt 0.021 · J 7.5e-06 · b 1.8e-05 · 12 V · 20 kHz.
Seed (kp 0.02, ki 0.5762): IAE **1.61142**, Ts 0.1875 s. Best (kp **0.3**, ki **8.0**): IAE **0.11606**, overshoot **0.0%**, Ts **0.0175 s**, SSE 0.0%, saturation 0.0%, final **300.0 rpm**. Grid n=25. Mean-by-ki overshoot: 0.0 / 0.192 / 1.271 / 3.725 / 7.752%; IAE: 0.9187 / 0.4701 / 0.339 / 0.251 / 0.2243.

### EXP02 — Sensors (`results/exp02_sensors.json`)
Sampling (50 Hz tone): 100 Hz 0.00326 V (Nyquist ✗) · 500 Hz **0.00268** ✓ · 1000 Hz 0.00358 ✓ · 5000 Hz 0.00322 ✓. Calibration gain **1.02041**, offset **−0.02041**, RMSE 0.0. Ultrasound 3 ms **0.5148 m**, 6 ms **1.0296 m**. DoA 0/87/174 µs → **0.0 / 29.85 / 84.46°**. Charlieplex 3/4/5/8 pins → 6/12/20/56 LEDs.

### EXP03 — Comms (`results/exp03_comms.json`)
Goodput: WiFi **90.0** · SPI **46.0** · RS-485 8.2 · I2C 2.55 · BLE 1.3 · CAN **0.55** · UART 0.092 Mbps. Frame (8 B): WiFi 0.711 µs … CAN 116.36 µs … UART 695.65 µs. Robustness CAN **10/10**. ROS: topic **0.6** / service **1.8** / action **2.6 ms**. Picks: motor-bus CAN, encoder SPI, debug UART, PC WiFi, graph topics.

### EXP04 — Integration (`results/exp04_integration.json`)
Diff: (0.3,0.3)→v0.3/w0.0; (0.4,0.2)→v0.3/w1.4286/ICC0.21; (0.3,−0.3)→spin 4.2857; (0.5,0.5)→v0.5. Odom 2 s: **(0.50832, 0.26947, 1.0)**. Arm FK (0.12, 0.10, 45°, 30°) → **(0.11073, 0.18145)**; IK → **(45.0°, 30.0°, reachable)**. Loop **17.0 ms / 58.8 Hz** ✓. DFM **7.0**, circular **6.4**.

### EXP05 — Hidden patterns (`results/exp05_hidden_patterns.json`)
H1 tradeoff + boundary optimum (optimum at edge → probe ki>8 next). H2 noise-floor surprise (×1.01, non-monotonic). H3 throughput inversion (163×). H4 comm bottleneck (47%). H5 thesis-in-one-number (exact IK vs drifting odometry). Exact wordings in JSON `findings[]`.

---

## 🗂️ Repository map

```
├── README.md                    # you are here
├── LICENSE                      # MIT
├── Dockerfile + docker-compose.yml
├── requirements.txt + pyproject.toml + Makefile
├── src/gems_benchmark/          # dc_drive · sensors · comms · integration
├── experiments/exp01_dc_drive … exp05_hidden_patterns/run.py
├── scripts/run_all.py · verify.py · fetch_live_data.py · make_demo.py · screenshot.py
├── tests/test_benchmark.py      # 10 physics invariants
├── docs/preview.html            # visual summary (open in browser)
├── docs/demo_dc.gif/.mp4 · demo_robot.gif/.mp4
├── docs/preview_shot.png · preview_full.png
├── docs/PAPER.md · METHODS.md · SOURCES.md · REPRODUCIBILITY.md
├── data/public/live_snapshot.json
└── results/*.json + results/figures/*.png   # regenerated + verified
```

---

## ⚙️ Install & run — zero to hero, step-by-step

**Option A — Docker (recommended, one command):**

```bash
docker compose up --build
docker compose run gems-verify
```

**Option B — Native (3 steps):**

```bash
pip install -r requirements.txt
python scripts/fetch_live_data.py   # checks live sources, caches, never blocks offline
python scripts/run_all.py           # 5 experiments → results + figures
python scripts/verify.py            # must print 12× PASS, exit 0
pytest -q                           # must print 10 passed
python scripts/make_demo.py         # regenerate GIFs/MP4s
python scripts/screenshot.py        # regenerate preview screenshots (needs playwright)
```

**Makefile shortcuts:** `make setup fetch run verify test docker-up docker-verify`.

---

## ✅ Verification — how you know nothing was hand-tuned

| Gate | Command | Required |
|---|---|---|
| Unit physics | `pytest -q` | 10 passed |
| End-to-end | `python scripts/run_all.py` | ALL EXPERIMENTS OK |
| Strict invariants | `python scripts/verify.py` | 12× PASS (IAE improved, SSE<5%, noise band, DoA 0°, charlieplex 12, CAN 10, SPI>I2C, arm reachable, loop realtime, 5 findings) |
| Live sources | `python scripts/fetch_live_data.py` | GEMS + OpenAlex OK (cached in `data/public/live_snapshot.json`) |
| Demos | `python scripts/make_demo.py` | 4 files, GIFs <500 KB |
| Preview | `python scripts/screenshot.py` | 2 PNGs, open `docs/preview.html` to confirm |

Rule enforced in this repo: **no result file is edited by hand — if a number changes without code changing, verification fails.**

---

## ❓ FAQ / Troubleshooting

**Do I need hardware?** No. Everything runs simulated with real physics. Hardware drivers can replace functions later.

**Which Python?** 3.10+ (tested 3.12). Docker uses 3.11-slim.

**GIF too big?** Ours are 363 + 442 KB (well under the 5 MB mobile limit) via PillowWriter 20 fps. MP4s ~25 KB via ffmpeg.

**Video does not play on GitHub?** GitHub README supports GIF inline; MP4 is linked + embedded in `preview.html` with `<video controls>`. Keep both.

**`verify.py` fails?** Read the FAIL line — it names the exact invariant (e.g., noise band, IAE). Do not edit JSON; fix code or parameters, rerun `run_all.py`.

**How do I cite?** See `docs/PAPER.md` references + `docs/SOURCES.md` for the full source log. Code: MIT (see LICENSE).

**How do I share publicly?**

```bash
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
# then enable GitHub Pages for docs/ or just share preview.html
```

---

## 📄 License & contributing

MIT © 2026 GEMS Benchmark Contributors — see [LICENSE](LICENSE). Issues and pull requests welcome: fork → branch → `pytest -q && python scripts/verify.py` → PR. For the full manuscript, methods, and source log see [`docs/PAPER.md`](docs/PAPER.md), [`docs/METHODS.md`](docs/METHODS.md), [`docs/SOURCES.md`](docs/SOURCES.md), [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).
