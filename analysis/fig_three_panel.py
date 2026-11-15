import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE="#2b6cb0"; ORANGE="#dd6b20"; GREY="#4a5568"; LIGHT="#a0aec0"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":15})
fig, ax = plt.subplots(1,3, figsize=(17,7.2), dpi=150)
fig.subplots_adjust(left=0.05,right=0.985,top=0.74,bottom=0.22,wspace=0.28)

def clean(a):
    for s in ("top","right"): a.spines[s].set_visible(False)
    a.spines["left"].set_color(LIGHT); a.spines["bottom"].set_color(LIGHT)
    a.tick_params(colors=GREY, length=0)

# A: FRP median with IQR
a=ax[0]; clean(a)
med=[9.0,5.6]; lo=[5.7,3.9]; hi=[16.5,8.5]
a.bar([0,1],med,color=[BLUE,ORANGE],width=0.55)
a.errorbar([0,1],med,yerr=[[m-l for m,l in zip(med,lo)],[h-m for m,h in zip(med,hi)]],
           fmt="none",ecolor=GREY,capsize=6,lw=1.6)
for x,m in zip([0,1],med):
    a.text(x+0.33,m,f"{m:.1f}",va="center",ha="left",fontsize=17,fontweight="bold",color=GREY)
a.set_xticks([0,1]); a.set_xticklabels(["Matched\nby Aqua","VIIRS-only"],color=GREY)
a.set_ylim(0,19); a.set_xlim(-0.6,1.9); a.set_ylabel("Fire power, median (MW)",color=GREY)
a.set_title("A. VIIRS-only fires are weaker",loc="left",fontsize=16,fontweight="bold",color="#1a202c")
a.text(0.5,18.4,"line = middle half of fires",ha="center",fontsize=11,color=GREY)

# B: lone pixel share
b=ax[1]; clean(b)
v=[25,54]
b.bar([0,1],v,color=[BLUE,ORANGE],width=0.55)
for x,m in zip([0,1],v):
    b.text(x,m+2,f"{m}%",ha="center",fontsize=17,fontweight="bold",color=GREY)
b.set_xticks([0,1]); b.set_xticklabels(["Matched\nby Aqua","VIIRS-only"],color=GREY)
b.set_ylim(0,70); b.set_ylabel("Share that are a lone pixel (%)",color=GREY)
b.set_title("B. VIIRS-only fires are more isolated",loc="left",fontsize=16,fontweight="bold",color="#1a202c")

# C: quiet to busy
c=ax[2]; clean(c)
q=[64,60,54,44]
c.bar(range(4),q,color="#718096",width=0.6)
for i,m in enumerate(q):
    c.text(i,m+2,f"{m}%",ha="center",fontsize=16,fontweight="bold",color=GREY)
c.set_xticks(range(4)); c.set_xticklabels(["Quietest\nmonths","","","Busiest\nmonths"],color=GREY)
c.set_ylim(0,80); c.set_ylabel("VIIRS lone-pixel share (%)",color=GREY)
c.set_title("C. Quiet months: more lone pixels",loc="left",fontsize=16,fontweight="bold",color="#1a202c")

fig.text(0.05,0.93,"Why VIIRS counts more hotspots than MODIS",fontsize=24,fontweight="bold",color="#1a202c")
fig.text(0.05,0.865,"VIIRS sees small, weak, isolated fires that Aqua's pixel often does not flag, and these are commoner in quiet months.",
         fontsize=15,color=GREY)
fig.text(0.05,0.805,"This is a pattern, not proof of why. VIIRS-only does not mean MODIS failed.",fontsize=13,color=GREY,style="italic")
fig.text(0.05,0.085,"A, B: daytime, Aqua vs Suomi NPP, Sabah, 2012-2022, within 15 minutes, passes where Aqua saw a fire (1,643 matched, 4,216 VIIRS-only).",fontsize=10.5,color=GREY)
fig.text(0.05,0.055,"C: all daytime VIIRS pixels in 2012-2022 (n = 24,823); months ranked by VIIRS count and split into 4 equal groups. Grey = all VIIRS pixels.",fontsize=10.5,color=GREY)
fig.text(0.05,0.022,"Source: NASA FIRMS (MODIS Aqua, VIIRS S-NPP). Hotspots are not burned area.",fontsize=10.5,color=GREY)
fig.savefig("slide6_three_panel.png")
