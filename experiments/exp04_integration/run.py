"""EXP04 runner."""
import json, sys
sys.path.insert(0,"src")
from gems_benchmark.integration import diff_drive, diff_drive_odometry, arm_fk_2r, arm_ik_2r, control_loop_budget, dfm_score_3dprint, sustainability_score

# differential sweep
sweep=[{"vr":vr,"vl":vl,**diff_drive(vr,vl)} for vr,vl in [(0.3,0.3),(0.4,0.2),(0.3,-0.3),(0.5,0.5)]]
# odometry rollout 2 s
pose=(0.0,0.0,0.0)
for _ in range(40):
    pose=diff_drive_odometry(0.3,0.5,0.05,pose)
fk=arm_fk_2r(0.12,0.10,45,30)
ik=arm_ik_2r(0.12,0.10,fk["x"],fk["y"])
budget=control_loop_budget()
dfm=dfm_score_3dprint(50,1.2,0.2)
sust=sustainability_score(60,3,True)
out={"diff_sweep":sweep,"odom_2s":pose,"arm_fk":fk,"arm_ik_roundtrip":ik,"loop":budget,"dfm":dfm,"sustainability":sust}
with open("results/exp04_integration.json","w") as f: json.dump(out,f,indent=2)
print(json.dumps(out,indent=2))
