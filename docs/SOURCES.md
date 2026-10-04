# Sources — every claim traceable (fetched 2026-10-04, cached in data/public/live_snapshot.json)

## 1. Program under study (user-provided edX copy + live verification)
- TU Delft Learning for Life: Building Robots from Mechatronic Components to Robotics (program page) — 4 courses, 27 weeks, Erasmus+ GEMS initiative.
- DelftX Electrical Drives (6w): DC equivalent circuit, half-bridge PWM, closed-loop architecture, PI tune, empirical deploy.
- DelftX Sensors and Data Acquisition (6w, U. Alcalá): sampling/noise, calibration, Ruby charlieplexing + ultrasound, DoA design.
- DelftX Communication Protocols and Hardware (7w, Teaching Factory): serial/industrial/wireless, ROS topics/services/actions, sustainability week.
- DelftX System Integration (8w, U. Ljubljana): specs, FDM DFM, differential kinematics, 2R arm kinematics, assemble→control→improve wireless robot.
- Live verification: `python scripts/fetch_live_data.py` hit `https://gems-erasmus.eu/hardware/` OK and `api.openalex.org` OK (see data/public/live_snapshot.json).

## 2. GEMS hardware ground truth (webfetch https://gems-erasmus.eu/hardware/)
- Diamond = Controlled Motion (DC motor + H-bridge + PWM + control loop) → EXP01.
- Ruby = Sensing the World (2-mic sound/ultrasound, ESP-class MCU) → EXP02.
- Sapphire = Communicate to Automate (system comms centre) → EXP03.
- Emerald = Power to the System (battery + flat cable DC+CAN) → EXP04 power/bus.
- Drivetrain (3-stage, oversized for understandability), Robots (2×GEMS + wheels), Amethyst (light+RGB, ESP32-C3), Citrine (SMD soldering trainer).
- Project meta: Erasmus+ KA220-HED 2022-1-SI01-KA220-HED-000087727, €400k, 01.11.2022–31.10.2025, partners UL (coord), Alcalá, Teaching Factory, TU Delft DC Systems group.

## 3. Sequential search voting (one-at-a-time, no parallel websearch to avoid 429)
1. `websearch` — DelftX/GEMS open-source hardware → confirmed program + hardware pages.
2. `searxng_web_search` — DC PI tuning → NETWORK ERROR (recorded; fallback used, no fabrication).
3. `openresearch web_search` — modular integration kinematics → TIMEOUT (recorded).
4. `paper-search search_papers` (arxiv/semantic/openalex/crossref, q=DC motor drives robotics) → 15 papers incl. Samak et al. Nigel sim2real robust control; Gaiceanu Embedded Control of DC Drive (cascade PI, Z-transform, modulus/symmetric optimum); Lotfi et al. open-source hardware in mechatronics education; Mahfouz et al. differential-drive-as-DC-motor-control.
5. `duckduckgo_search` (ROS2 UART/I2C/SPI/CAN 2026) → 8 results: RobotForge one-robot-six-protocols rule; SmashingRobotics Aug-2026 I2C/SPI/UART guide; thomasthelliez CAN-vs-UART-vs-I2C-vs-SPI decision framework (used in code).
6. `agent-reach_search web` → unavailable (needs Exa key, recorded); `github` → gh CLI flag error (recorded). No hallucinated GitHub hits.
7. `openresearch search_openalex` (modular benchmarking) → CardioXplorer open-source modular robot; Gaspar et al. reconfigurable workcell; DeepClaw hardware benchmark; Padilla-García 2026 open BLDC drive platform.
8. `paper-search_search_arxiv` (differential kinematics ROS2) → low precision (surgical kinematics, VQualA, Mobile-MMLU) — recorded as negative result, not cited as support.
9. `kaggle search_everything` (robotics DC/IMU) → no results (recorded).
10. `wiki_search` (DC PID/kinematics) → Motion control, Servo, Kalman filter, Simatic (background only).
11. `gsd_websearch` (reproducible benchmarking) → empty (recorded).
12. `openresearch hacker_news` (open-source robotics education ROS) → no results (recorded).
13. `openresearch stackoverflow` (DC PID Python encoder) → 1 Q/A: beagle-bone differential PID (ecological validity for EXP01).
14. `gitmcp documentation` (ros2_control diff-drive benchmarking) → no doc hit (recorded).
15. `websearch` (reproducible Docker benchmark live data) → HIT: open-navigation workload benchmark (Docker + Nav2 + 3×3D-lidar/RGBD/IMU, HIL + logs + analysis) and CSAR 2026 (LXC/LXD + ROS2/DDS, edge-offloaded SLAM, Zenodo rosbags) and SwarmRob (Docker reproducibility toolkit). These three justify our Docker-Compose + `results/` + `verify.py` design.
16. `superpowers recommend` → systematic-debugging/dispatching-parallel-agents (workflow only).
17. `openresearch news` (modular hardware) → irrelevant Forbes/composites (recorded as negative).
18. `paper-search semantic` (ROS latency) → empty (recorded).
19. `kaggle datasets_list` → sort_by type error (recorded); `discussions_search` → 2 unrelated threads (recorded).
20. `webfetch` GEMS hardware page → full module map (strongest ground truth, quoted above).

## 4. What was NOT used
- searxng engine results (server down), Exa (no key), bili/reddit/twitter backends (irrelevant). All failures logged here instead of silently retried in parallel.
