import sys
sys.path.insert(0, "src")
from gems_benchmark.dc_drive import DCMotorParams, PIParams, simulate_closed_loop, steady_state_current
from gems_benchmark.sensors import ultrasound_distance, doa_tdoa, charlieplex_capacity, calibrate_linear
from gems_benchmark.comms import protocol_table, recommend_link
from gems_benchmark.integration import diff_drive, arm_fk_2r, arm_ik_2r, control_loop_budget

def test_dc_steady_state():
    p = DCMotorParams()
    assert abs(steady_state_current(12.0, 0.0, p) - 12.0/2.2) < 1e-9

def test_closed_loop_tracks():
    m = simulate_closed_loop(DCMotorParams(), PIParams(kp=0.15, ki=2.0))
    assert m["sse_pct"] < 5.0
    assert m["saturation_frac"] < 0.5

def test_ultrasound():
    d = ultrasound_distance(0.006, 20.0)
    assert 1.0 < d < 1.1

def test_doa():
    assert doa_tdoa(0.0) == 0.0
    assert abs(doa_tdoa(87e-6) - 28.7) < 2.0

def test_charlieplex():
    assert charlieplex_capacity(4) == 12

def test_calibration():
    c = calibrate_linear([0,1,2],[0,2,4])
    assert abs(c["gain"]-2.0) < 1e-6 and c["rmse"] < 1e-6

def test_comms_ranking():
    tab = protocol_table()
    spi = [r for r in tab if r["protocol"]=="SPI"][0]
    i2c = [r for r in tab if r["protocol"]=="I2C"][0]
    assert spi["goodput_mbps"] > i2c["goodput_mbps"]
    assert recommend_link("motor-bus")["pick"] == "CAN"

def test_diff_drive():
    d = diff_drive(0.3,0.3)
    assert d["v_ms"] == 0.3 and d["w_rads"] == 0.0

def test_arm_roundtrip():
    fk = arm_fk_2r(0.12,0.10,45,30)
    ik = arm_ik_2r(0.12,0.10,fk["x"],fk["y"])
    assert ik["reachable"] is True

def test_loop_budget():
    assert control_loop_budget()[" realtime_ok_20hz"] is True
