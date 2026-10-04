"""Run all experiments end-to-end (zero to hero)."""
import subprocess, sys, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
exps = ["exp01_dc_drive","exp02_sensors","exp03_comms","exp04_integration","exp05_hidden_patterns"]
# order matters: 05 needs 01/02/04 outputs
for e in exps:
    print(f"\n===== {e} =====")
    r = subprocess.run([sys.executable, f"experiments/{e}/run.py"], cwd=root)
    if r.returncode != 0:
        raise SystemExit(f"{e} failed")
print("\nALL EXPERIMENTS OK — see results/*.json + results/figures/")
