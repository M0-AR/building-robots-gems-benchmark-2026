"""EXP01 runner — emits results/exp01_dc_drive.json + figure."""
import json, sys
sys.path.insert(0, "src")
from gems_benchmark.dc_drive import DCMotorParams, PIParams, simulate_closed_loop, modulus_optimum_seed, grid_tune
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

p = DCMotorParams()
seed = modulus_optimum_seed(p)
base = simulate_closed_loop(p, PIParams(**{**seed.__dict__}))
tuned = grid_tune(p)
out = {"motor": p.__dict__, "seed_pi": seed.__dict__, "seed_result": base, "tuned": tuned["best"], "grid_n": len(tuned["grid"])}
with open("results/exp01_dc_drive.json", "w") as f:
    json.dump(out, f, indent=2)
# figure: overshoot vs IAE across grid
xs = [r["overshoot_pct"] for r in tuned["grid"]]
ys = [r["iae"] for r in tuned["grid"]]
plt.figure()
plt.scatter(xs, ys)
plt.xlabel("overshoot %")
plt.ylabel("IAE")
plt.title("DC drive PI grid: overshoot vs IAE (300 rpm)")
plt.savefig("results/figures/exp01_grid.png", dpi=150)
print(json.dumps(out["tuned"], indent=2))
