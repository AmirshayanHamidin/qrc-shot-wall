import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=json.load(open('b9_marginest.json'))['rows']
PIL=[250,1000,4000,16000]
def col(est,key,f): return [r[est][key] for r in R if f(r)]
fig,ax=plt.subplots(1,3,figsize=(15,4.6))

# A: naive bias vs D0 (small D0 -> big optimistic bias)
for Sp,mk,cc in [(250,'o','tab:red'),(1000,'s','tab:orange'),(4000,'^','tab:green')]:
    f=lambda r,Sp=Sp:r['S_pilot']==Sp
    D=col('naive','bias',f); D0=[r['D0'] for r in R if f(r)]
    ax[0].scatter(D0,[100*b for b in D],marker=mk,color=cc,label=f'pilot {Sp} shots',alpha=0.8)
ax[0].axhline(0,color='k',lw=0.8); ax[0].set_xscale('log')
ax[0].set_xlabel('exact separation $D_0=\\|\\mu_1-\\mu_0\\|$ (log)')
ax[0].set_ylabel('naive estimator bias (%)')
ax[0].set_title('A. Naive plug-in is OPTIMISTICALLY biased,\nworst for hard (small-$D_0$) tasks')
ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)

# B: bias vs S_pilot, naive vs corrected (mean over 15 configs)
def mean(est,key,Sp): 
    f=lambda r:r['S_pilot']==Sp; return 100*np.mean(col(est,key,f))
ax[1].plot(PIL,[mean('naive','bias',s) for s in PIL],'s--',color='tab:red',label='naive plug-in')
ax[1].plot(PIL,[mean('corr_pilot','bias',s) for s in PIL],'o-',color='tab:blue',label='bias-corrected (pilot-only)')
ax[1].axhline(0,color='k',lw=0.8); ax[1].set_xscale('log')
ax[1].set_xlabel('pilot budget $S_{pilot}$ (shots/timestep, log)')
ax[1].set_ylabel('mean estimator bias (%)')
ax[1].set_title('B. A cheap closed-form correction\nremoves the bias at every budget')
ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)

# C: corrected RMSE and implied shot-budget error (2x) vs S_pilot
rmse=[mean('corr_pilot','rmse',s) for s in PIL]
ax[2].plot(PIL,rmse,'o-',color='tab:blue',label='RMSE of $\\hat D$ (corrected)')
ax[2].plot(PIL,[2*x for x in rmse],'^--',color='tab:purple',label='implied shot-budget error ($\\approx2\\times$)')
ax[2].axhline(5,color='gray',ls=':',lw=1); ax[2].set_xscale('log')
ax[2].set_xlabel('pilot budget $S_{pilot}$ (shots/timestep, log)')
ax[2].set_ylabel('relative error (%)')
ax[2].set_title('C. Practical cost: $\\gtrsim$1k pilot shots\ngives $<$6% budget error (avg task)')
ax[2].legend(fontsize=8); ax[2].grid(alpha=0.3)

plt.tight_layout(); plt.savefig('/tmp/b9/qrc_marginest.png',dpi=130)
print('saved')
