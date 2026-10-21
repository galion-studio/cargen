import sys; sys.path.insert(0,'src')
from glyphs import text_path, FONTS
rows=[]; y=80
for n in ["outfit","sora","manrope","figtree","plex","instrument","hanken","geologica"]:
  for w in (500,600):
    d,wd,_,_=text_path("cargen",n,w,72,x=40,y=y)
    rows.append(f'<path d="{d}" fill="#1E2620"/><text x="420" y="{y}" font-size="16" font-family="sans-serif">{n} {w}</text>'); y+=80
open('_scratch/fonts.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="{y}"><rect width="100%" height="100%" fill="#F3F0E7"/>{"".join(rows)}</svg>')
