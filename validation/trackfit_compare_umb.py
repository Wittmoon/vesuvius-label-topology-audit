import json,sys,numpy as np
ours=json.load(open(sys.argv[1]))["control_points"]; ref=json.load(open(sys.argv[2]))["control_points"]
rz=np.array([p["z"] for p in ref]); rx=np.array([p["x"] for p in ref]); ry=np.array([p["y"] for p in ref])
o=np.argsort(rz); rz,rx,ry=rz[o],rx[o],ry[o]
errs=[]
for p in ours:
    x=np.interp(p["z"],rz,rx); y=np.interp(p["z"],rz,ry)
    e=np.hypot(p["x"]-x,p["y"]-y); errs.append(e)
    print(f"z{p['z']:.0f} ours({p['x']:.0f},{p['y']:.0f}) ref({x:.0f},{y:.0f}) err {e:.0f}px")
print("median err",round(float(np.median(errs)),1),"max",round(float(np.max(errs)),1))
