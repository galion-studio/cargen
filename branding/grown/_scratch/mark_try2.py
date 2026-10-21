import sys; sys.path.insert(0,'src')
import brand
from brand import *
brand.BODY_D=("M 24 166 L 24 149 C 24 139 31 133 42 131 L 76 125 C 96 106 117 98 142 98 "
 "C 165 98 183 106 199 120 L 219 124 C 228 126 232 133 232 142 L 232 166 Z")
brand.WHEELS=[(70,166),(188,166)]; brand.ARCH_R=25
B = body()
def r_of(x,y):
    t = (x-24)/208
    return 23 - 15*t**1.6
pts = poisson(B, r_of, seed=int(sys.argv[1]) if len(sys.argv)>1 else 11, tries=20000)
xy = lloyd(pts, B, r_of, 4)
cells = voronoi(xy, B)
P=PAL; parts=[]
for (x,y),c in zip(xy,cells):
    t=(x-24)/208
    col = P["foxfire"] if t>0.88 else mix(P["moss"],P["lichen"],min(1,max(0,(t-0.25)/0.65))**1.5)
    parts.append(f'<path d="{to_d(rounded(c,2.6,1.4))}" fill="{col}"/>')
for w in wheels(18.5):
    ring = w.difference(w.buffer(-7))
    parts.append(f'<path d="{to_d(ring)}" fill="{P["lichen"]}" fill-rule="evenodd"/>')
miny=B.bounds[1]; maxy=166+18.5; dy=128-(miny+maxy)/2
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256"><rect x="8" y="8" width="240" height="240" rx="56" fill="{P["loam"]}"/><g transform="translate(0 {dy:.1f})">{"".join(parts)}</g></svg>'
open('_scratch/m2.svg','w').write(svg); print(len(xy))
