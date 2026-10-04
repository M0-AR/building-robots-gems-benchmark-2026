"""EXP02 runner."""
import json, sys
sys.path.insert(0, "src")
from gems_benchmark.sensors import sampling_benchmark, calibrate_linear, ultrasound_distance, doa_tdoa, charlieplex_capacity
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

samp = sampling_benchmark()
# synthetic calibration: true 0..10 cm vs raw with gain 0.98 + offset
raw = [i*0.33 for i in range(11)]
true = [r*1.0 for r in [0,1,2,3,4,5,6,7,8,9,10]]
cal = calibrate_linear([v*0.98+0.02 for v in [0,1,2,3,4,5,6,7,8,9,10]], true)
us = {"tof_3ms_m": round(ultrasound_distance(0.003), 4), "tof_6ms_m": round(ultrasound_distance(0.006), 4)}
doa = {"0us": doa_tdoa(0.0), "87us": doa_tdoa(87e-6), "174us": doa_tdoa(174e-6)}
charlie = {n: charlieplex_capacity(n) for n in [3,4,5,8]}
out = {"sampling": samp, "calibration": cal, "ultrasound_m": us, "doa_deg": doa, "charlieplex": charlie}
with open("results/exp02_sensors.json","w") as f: json.dump(out,f,indent=2)
plt.figure()
plt.plot([r["fs_hz"] for r in samp],[r["mae_v"] for r in samp],marker="o")
plt.xscale("log"); plt.xlabel("fs Hz"); plt.ylabel("MAE V"); plt.title("Sampling rate vs acquisition error (50 Hz tone)")
plt.savefig("results/figures/exp02_sampling.png",dpi=150)
print(json.dumps(out,indent=2))
