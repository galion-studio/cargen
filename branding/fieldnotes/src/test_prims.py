from fn_lib import *
d=""; b=""
g,dd=car(20,20,1.0,copper=P["copper"],paper=P["paper"]); b+=g; d+=dd
g,dd=leaf(600,140,260,110,angle=-20,pid="l1"); b+=g; d+=dd
g,dd=moth_wing(900,140,1.3,copper=P["copper"],wash=P["vellum"]); b+=g; d+=dd
g,dd,_=tube(1180,30,0.5,copper=P["copper"],paper=P["paper"]); b+=g; d+=dd
t,_=T("cargen","garamond",90,40,330,P["ink"]); b+=t
t,_=T("Fig. 1  carapax plicata — P_m 101.0 kN","mono",14,400,320,P["sepia"]); b+=t
open("/tmp/fn_test.svg","w").write(svg(1300,360,b,"test",bg=P["paper"],extra_defs=d))
