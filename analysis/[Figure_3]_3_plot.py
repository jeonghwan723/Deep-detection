# JHK
# Python script for generating Figure 3.

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Set output path & name
#==========================================================
o_path = hdir+'/fig/'
o_name = 'Figure3'

#====================================================================
# load binned high frequency (HF) precipiction (PRCP) 
# and 7x7 occlusion sensitivity (OS)
# (from '[Figure3]_1_binning.py')
#====================================================================
# binned data of deep detection model [3,20] [3-regions, 20-bins]
i_path = hdir+'/data/figure3/'
i_name = 'bin_prcp_occ_dd.nc'
f = Dataset(i_path+i_name,'r')
bins_dd = f['p'][:,0,1] * 100
f.close()

# binned data of ridge regression model [3,20]
i_name = 'bin_prcp_occ_reg.nc'
f = Dataset(i_path+i_name,'r')
bins_reg = f['p'][:,0,1] * 100
f.close()

#====================================================================
# Load PDF ratio of HF PRCP [3,4,10] [3-regions, 4-decades, 10-bins]
# 1st dim: EP ITCZ region, Mid-latitude storm track region, Subtropics region
# 2nd dim: 1980s, 1990s, 2000s, 2010s
# 3rd dim: ten-bins of HF PRCP
# (from '[Figure3]_2_PDF_ratio.py')
#====================================================================
i_name = 'pdf_prcp.nc'
f = Dataset(i_path+i_name,'r')
pdf = f['p'][:,0]
f.close()

#====================================================================
# plot
#====================================================================
mpl.use('Agg')
plt.rcParams["figure.figsize"] = [6.2, 5.0]
plt.rcParams["pdf.fonttype"] = 42

#====================================================================
# Panel (a) and (b)
#====================================================================
for i in range(2):

    plt.subplot(2,2,i+1)

    x = np.arange(2.5,97.501,5)

    line1 = plt.plot(x, bins_dd[i], 'tab:green')
    plt.setp(line1,linewidth=1.0, marker='o', markersize=2.0, zorder=6)

    line2 = plt.plot(x, bins_reg[i], 'black')
    plt.setp(line2,linewidth=1.0, marker='v', linestyle='-', markersize=2.0, zorder=5)

    plt.xticks([10,20,30,40,50,60,70,80,90])
    plt.tick_params(labelsize=6,direction='out',length=1.5,width=0.4)

    plt.xlim([2.5,97.5])
    plt.ylim([-2,8])

    if i == 0:
        plt.title('a', fontsize=8, x=-0.11, y=0.97, ha='left', weight='bold')
        plt.text(50, 8.7, 'EP ITCZ', fontsize=8, ha='center')
    elif i == 1:
        plt.title('b', fontsize=8, x=-0.11, y=0.97, ha='left', weight='bold')
        plt.text(50, 8.7, 'Mid-latitude', fontsize=8, ha='center')
    
    if i == 0:
        plt.ylabel(r'Occlusion sensitivity (°C 10$^{-2}$)', fontsize=7)
    plt.xlabel('HF PRCP (percentile)', fontsize=7)

    plt.axhline(0, linewidth=0.5, color='black', linestyle='--')
    plt.axvline(50, linewidth=0.5, color='black', linestyle='--')

    if i == 0:
        plt.legend(bbox_to_anchor=[0.9, 1], labels=['DD', 'Reg.'], loc='upper right', prop={'size':6}, ncol=1, frameon=False)
    else:
        plt.legend([line1[0], line2[0]], ['DD', 'Reg.'], loc='upper right', prop={'size':6}, ncol=1, frameon=False)

#====================================================================
# panel (c), (d)
#====================================================================
for i in range(2):

    plt.subplot(2,2,i+3)
    x = np.arange(5,95.001,10)

    col_list = ['lightsalmon', 'orangered', 'tab:red', 'darkred']

    colors = plt.cm.RdYlBu_r(np.linspace(0,1,20))
    col_loc = [0, 4, 15, 19]

    for j in range(4):
        line1 = plt.plot(x, pdf[i,j], color=colors[col_loc[j]])
        plt.setp(line1,linewidth=1.2, marker='o', markersize=0, zorder=5)

    plt.xticks([10,20,30,40,50,60,70,80,90])
    plt.tick_params(labelsize=6,direction='out',length=1.5,width=0.4)

    plt.xlim([5,95])
    plt.ylim([0.85,1.17])

    if i == 0:
        plt.title('c', fontsize=8, x=-0.11, y=0.97, ha='left', weight='bold')
    elif i == 1:
        plt.title('d', fontsize=8, x=-0.11, y=0.97, ha='left', weight='bold')

    if i == 0:
        plt.ylabel('PDF ratio (each decade / all)', fontsize=7)
    plt.xlabel('HF PRCP (percentile)', fontsize=7)

    plt.legend(['1980s', '1990s', '2000s', '2010s'], loc='upper right', prop={'size':6}, ncol=2, frameon=False)

    plt.axhline(1, linewidth=0.5, color='black', linestyle='--')
    plt.axvline(50, linewidth=0.5, color='black', linestyle='--')

plt.tight_layout(h_pad=1,w_pad=2)
plt.subplots_adjust(bottom=0.1, top=0.90, left=0.11, right=0.95)
plt.savefig(o_path+o_name+'.png', dpi=300)
plt.close()






