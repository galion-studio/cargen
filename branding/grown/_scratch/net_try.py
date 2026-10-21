import sys; sys.path.insert(0,'src')
from brand import PAL as P
from growth import *
W,H=1280,320
attr,nodes=filament_attractors(W,H,n=2600,n_nodes=16,seed=5,bounds=(420,-20,1300,340))
roots=[(1290,40),(1290,280),(1100,330),(800,330),(1000,-10)]
Pt,par,r,k=colonise(attr,roots,step=5,kill=8,influence=60)
print(len(Pt))
body=network_svg(Pt,par,r,k,P["moss"],tip_col=P["foxfire"],node_col=P["foxfire"],w0=0.6)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="{P["loam"]}"/>{body}</svg>'
open('_scratch/net.svg','w').write(svg)
