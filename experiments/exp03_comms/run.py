"""EXP03 runner."""
import json, sys
sys.path.insert(0,"src")
from gems_benchmark.comms import protocol_table, recommend_link, ros_choice_table
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

tab = protocol_table()
ros = ros_choice_table()
recs = {k: recommend_link(k) for k in ["motor-bus","joint-encoder","debug-gps","pc-link","ros-graph"]}
out = {"protocols": tab, "ros": ros, "recommendations": recs}
with open("results/exp03_comms.json","w") as f: json.dump(out,f,indent=2)
names=[r["protocol"] for r in tab]; vals=[r["goodput_mbps"] for r in tab]
plt.figure(figsize=(8,3.5)); plt.bar(names,vals); plt.xticks(rotation=25,ha="right")
plt.ylabel("goodput Mbps (log-ish)"); plt.title("Protocol goodput comparison (8B frame model)")
plt.tight_layout(); plt.savefig("results/figures/exp03_goodput.png",dpi=150)
print(json.dumps(out,indent=2))
