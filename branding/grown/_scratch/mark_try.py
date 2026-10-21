import sys; sys.path.insert(0,'src')
from brand import *
B = body()
def r_of(x,y):
    t = (x-30)/196   # 0 rear .. 1 front
    return 30 - 19*t**1.4
pts = poisson(B, r_of, seed=11)
xy = lloyd(pts, B, r_of)
cells = voronoi(xy, B)
P=PAL; parts=[]
for (x,y),c in zip(xy,cells):
    t=(x-30)/196
    col = P["foxfire"] if t>0.9 else mix(P["moss"],P["lichen"],min(1,t**2*1.1))
    parts.append(f'<path d="{to_d(rounded(c,3.2,1.6))}" fill="{col}"/>')
for w in wheels(): parts.append(f'<path d="{to_d(w)}" fill="{P["lichen"]}"/>')
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256"><rect x="8" y="8" width="240" height="240" rx="56" fill="{P["loam"]}"/><g transform="translate(0 -3)">{"".join(parts)}</g></svg>'
open('_scratch/m1.svg','w').write(svg); print(len(xy))
