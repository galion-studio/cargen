import sys,os; sys.path.insert(0,'/workspace/cargen/branding/grown/src')
import mark, subprocess
from brand import PAL as P
def svg(b): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">{b}</svg>'
open('t_full.svg','w').write(svg(mark.tile()+mark.glyph('dark')))
open('t_small.svg','w').write(svg(mark.tile()+mark.small_glyph()))
open('t_light.svg','w').write(svg(f'<rect width="256" height="256" fill="{P["bone"]}"/>'+mark.glyph('light')))
for n in ['t_full','t_small','t_light']:
  for s in [512,64,32,16]:
    subprocess.run(['resvg','-w',str(s),n+'.svg',f'{n}_{s}.png'])
