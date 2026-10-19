import zarr, numpy as np, json, csv, time, math, sys
from concurrent.futures import ThreadPoolExecutor
B="https://vesuvius-challenge-open-data.s3.amazonaws.com/"
A2="PHerc0139/segments/%s/surface-volumes/2.399um-0.22m-78keV-volume-20260102150214.zarr"
P1="PHerc1667/segments/%s/surface-volumes/2.399um-0.22m-78keV-volume-20251217075048.zarr"
PP="PHercParis4/segments/%s/surface-volumes/2.4um-0.22m-78keV-volume-20260411134726.zarr"
al=[("pherc0139-w016",A2%"20250108000004-w029_2025010827"),("pherc0139-w017",A2%"20250108000005-w030_2025010818"),
("pherc0139-w028",A2%"20260115000000-w044_2026011522"),("pherc0139-w029",A2%"20260126000000-w045_2026012619"),
("pherc0139-w035",A2%"20260317000000-w035_2026031718"),("pherc0139-w039",A2%"20260302000000-w039_2026030210"),
("pherc0139-w040",A2%"20250831000000-w040_2025083102"),("pherc0139-w041",A2%"20260108000000-w041_2026010816"),
("pherc0139-w043",A2%"20260112000000-w043_2026011217"),
("pherc0814-46527","PHerc0814/segments/20260226000000-46527_2um_try2/surface-volumes/2.399um-0.22m-78keV-volume-20260309142202.zarr")]
for s,i in [("w013","20240304141531-w013_20240304141531_flatboi"),("w018","20240304144031-w018_20240304144031_flatboi"),
("w023","20240304161941-w023_20240304161941_flatboi"),("w028","20251208130119-w028_20251208130119156_flatboi"),
("w029","20251212185248-w029_20251212185248662_flatboi"),("w031","20251223230000-w031_2025122323_flatboi")]:
    al.append(("pherc1667-"+s,P1%i))
for s,i in [("w00","20231016151002"),("w01","20230702185753"),("w02","20231031143852"),("w03","20231106155351"),
("w05","20231012184424"),("w06","20231210121321"),("w07","20231007101619"),("w09","20230929220926")]:
    al.append(("phercparis4-"+s,PP%i))
N9="PHerc0139/segments/%s/surface-volumes/9.362um-1.2m-113keV-volume-20250728140407.zarr"
LOC="/Volumes/Studio-SSD/Claude/projects/other/vesuvius-villa-tools/scratch/ink/data/%s/sv9/0"
nat=[("native-w035",LOC%"w035"),("native-w039",LOC%"w039"),
("native-w040",B+(N9%"20250831000000-w040_2025083102")+"/0"),("native-w041",B+(N9%"20260108000000-w041_2026010816")+"/0"),
("native-w044",B+(N9%"20260115000000-w044_2026011522")+"/0")]
def run(name,path,source):
    t0=time.time()
    a=zarr.open_array(path,mode='r',zarr_format=2)
    Z,Y,X=a.shape; ch=a.chunks[1]
    if source=="aligned":
        z0=math.ceil((Z-84)/2); zs=slice(z0,z0+84); nl=21
    else:
        zs=slice(0,Z); nl=Z
    ys=np.arange(int(Y*.25)//ch,int(Y*.75)//ch+1); xs=np.arange(int(X*.25)//ch,int(X*.75)//ch+1)
    sel=lambda v:v[np.unique(np.linspace(0,len(v)-1,min(len(v),10)).round().astype(int))]
    cells=[(y,x) for y in sel(ys) for x in sel(xs)]
    def rd(c):
        if time.time()-t0>600: return None
        y,x=c; b=a[zs,y*ch:(y+1)*ch,x*ch:(x+1)*ch].astype(np.float32)
        if source=="aligned": b=b.reshape(nl,4,*b.shape[1:]).mean(1)
        m=(b>0).any(0); 
        return (b[:,m].sum(1),int(m.sum()))
    with ThreadPoolExecutor(16) as ex: rs=[r for r in ex.map(rd,cells) if r]
    n=sum(r[1] for r in rs)
    if n==0: raise RuntimeError("no signal columns")
    prof=sum(r[0] for r in rs)/n
    return prof,n,len(rs),len(cells),time.time()-t0
out=[];full={};skip=[]
for source,lst in (("aligned",al),("native9",nat)):
    for name,p in lst:
        path=p if p.startswith(("/","http")) else B+p+("/2" if source=="aligned" else "")
        try:
            prof,n,k,kc,dt=run(name,path,source)
        except Exception as e:
            skip.append((name,repr(e)[:150])); print("SKIP",name,repr(e)[:150],flush=True); continue
        nl=len(prof);c=nl//2;pk=int(prof.argmax());cen=float((prof*np.arange(nl)).sum()/prof.sum())
        out.append(dict(segment=name,source=source,n_layers=nl,centre=c,peak_layer=pk,centroid=round(cen,2),peak_minus_centre=pk-c))
        full[name]=dict(source=source,profile=[round(float(v),3) for v in prof],columns=n,chunks_read=f"{k}/{kc}")
        print(name,source,nl,c,pk,round(cen,2),pk-c,f"cols={n} chunks={k}/{kc} {dt:.0f}s",flush=True)
        w=csv.DictWriter(open("profiles.csv","w"),fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
        json.dump(dict(profiles=full,skipped=skip),open("profiles_full.json","w"))
print("SKIPPED",skip)
