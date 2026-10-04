"""EXP03 — Sapphire module: communication protocols + hardware + ROS.

Models DelftX Comms Weeks 1-7:
- Serial: UART/RS-232/RS-485, I2C, SPI, CAN (baud, topology, arbitration, CRC)
- Wireless: WiFi/BLE (range, throughput, industrial robustness penalty)
- ROS1 vs ROS2-DDS concepts: topics/services/actions overhead model
- PCB/industrial best-practice scoring (termination, shielding, grounding)

Numbers are literature-anchored order-of-magnitude benchmarks (RobotForge,
SmashingRobotics Aug-2026, thomasthelliez CAN-vs-UART-vs-I2C-vs-SPI comparison),
implemented as transparent formulas — not vendor datasheets. Every row is
recomputed live by the experiment script.
"""
from __future__ import annotations


PROTOCOLS = {
    # max_clock_mhz, wires, multi_master, distance_m, overhead BYTE per frame approx, robust industry score 0-10
    "UART":      {"clock_mhz": 0.115, "wires": 2, "topology": "point-to-point", "distance_m": 15,  "payload_eff": 0.80, "robust": 4},
    "RS-485":    {"clock_mhz": 10.0,  "wires": 2, "topology": "multi-drop/32",  "distance_m": 1200,"payload_eff": 0.82, "robust": 8},
    "I2C":       {"clock_mhz": 3.4,   "wires": 2, "topology": "bus/127",        "distance_m": 2,   "payload_eff": 0.75, "robust": 4},
    "SPI":       {"clock_mhz": 50.0,  "wires": 4, "topology": "star/select",    "distance_m": 0.5, "payload_eff": 0.92, "robust": 3},
    "CAN":       {"clock_mhz": 1.0,   "wires": 2, "topology": "multi-master/110","distance_m": 500,"payload_eff": 0.55, "robust": 10},
    "WiFi-ESP32":{"clock_mhz": 150.0, "wires": 0, "topology": "star/AP",        "distance_m": 50,  "payload_eff": 0.60, "robust": 5},
    "BLE-ESP32": {"clock_mhz": 2.0,   "wires": 0, "topology": "star/mesh",      "distance_m": 30,  "payload_eff": 0.65, "robust": 5},
}

ROS_OVERHEAD = {
    "topic":   {"latency_ms": 0.6, "note": "async pub/sub, best for streaming sensor/odom"},
    "service": {"latency_ms": 1.8, "note": "sync request/response, best for config/IK query"},
    "action":  {"latency_ms": 2.6, "note": "goal/feedback/result, best for navigation/arm motion"},
}


def protocol_table(payload_bytes: int = 8) -> list:
    rows = []
    for name, p in PROTOCOLS.items():
        raw_mbps = p["clock_mhz"]
        goodput = raw_mbps * p["payload_eff"]
        # time to move one payload frame (µs), idealised
        t_us = payload_bytes * 8 / max(goodput, 1e-6)
        rows.append({
            "protocol": name,
            "raw_mbps": raw_mbps,
            "goodput_mbps": round(goodput, 3),
            "frame_us_8B": round(t_us, 3),
            "topology": p["topology"],
            "distance_m": p["distance_m"],
            "robust_0_10": p["robust"],
        })
    return sorted(rows, key=lambda r: r["goodput_mbps"], reverse=True)


def recommend_link(requirements: str = "motor-bus") -> dict:
    """Decision framework (thomasthelliez 2026 rule distilled to code)."""
    rules = {
        "motor-bus": ("CAN", "daisy-chain motor controllers, arbitration+CRC, noise-immune twisted pair"),
        "joint-encoder": ("SPI", "per-joint absolute encoder, full-duplex speed, short star wiring"),
        "debug-gps": ("UART", "console/GPS point-to-point simplicity"),
        "pc-link": ("WiFi-ESP32", "Jetson/PC high goodput, accept jitter"),
        "ros-graph": ("ROS2-DDS topic", "streaming odom/scan; service for params; action for goals"),
    }
    pick, why = rules.get(requirements, ("CAN", "default industrial backbone"))
    return {"for": requirements, "pick": pick, "why": why}


def ros_choice_table() -> list:
    return [{"primitive": k, **v} for k, v in ROS_OVERHEAD.items()]
