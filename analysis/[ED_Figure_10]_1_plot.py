# JHK
# Python script for generating ED Figure 10

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Set output path & name
#==========================================================
o_path = hdir+'/fig/'
o_name = 'ED_Figure10'

#====================================================================
# load binned high frequency (HF) precipiction (PRCP) 
# and 7x7 occlusion sensitivity (OS)
# (from '[Figure3]_1_binning.py')
#====================================================================
# Deep detection [3,2,20]
i_path = hdir+'/data/figure3/'
i_name = 'bin_prcp_occ_dd.nc'
f = Dataset(i_path+i_name,'r')
bins_dd = f['p'][:,0]
f.close()

# Ridge regression [3,2,20]
i_path = hdir+'/data/figure3/'
i_name = 'bin_prcp_occ_reg.nc'
f = Dataset(i_path+i_name,'r')
bins_reg = f['p'][:,0]
f.close()

#====================================================================
# Load PDF ratio of HF PRCP [3,4,10] [3-regions, 4-decades, 10-bins]
# 1st dim: EP ITCZ region, Mid-latitude storm track region, Subtropics region
# 2nd dim: 1980s, 1990s, 2000s, 2010s
# 3rd dim: ten-bins of HF PRCP
# (from '[Figure3]_2_PDF_ratio.py')
#====================================================================
i_path = hdir+'/data/main/figure3/'
i_name = 'pdf_prcp.nc'
f = Dataset(i_path+i_name,'r')
pdf = f['p'][:,0]
f.close()

#====================================================================
# plot
#====================================================================
plt.rcParams["figure.figsize"] = [6.4, 4.8]

x = np.arange(2.5,97.501,5)

line1 = plt.plot(x, bins_dd[2,1]*100, 'tab:green')
plt.setp(line1,linewidth=2.0, marker='o', markersize=4.0, zorder=6)

line2 = plt.plot(x, bins_reg[2,1]*100, 'black')
plt.setp(line2,linewidth=2.0, marker='v', markersize=4.0, zorder=5)

plt.xticks([10,20,30,40,50,60,70,80,90])
plt.tick_params(labelsize=9,direction='out',length=1.5,width=0.4)

plt.xlim([2.5,97.5])
plt.ylim([-5.8,8.4])

plt.title('Subtropics', fontsize=12, x=0.5, y=1, ha='center')

plt.ylabel(r'Occlusion sensitivity (°C 10$^{-2}$)', fontsize=10)
plt.xlabel('HF PRCP (percentile)', fontsize=10)

plt.axhline(0, linewidth=1, color='black', linestyle='--')
plt.axvline(50, linewidth=1, color='black', linestyle='--')

plt.legend([line1[0], line2[0]], ['DD', 'Reg.'], loc='upper right', prop={'size':10}, ncol=1, frameon=False)

plt.subplots_adjust(bottom=0.15, top=0.9, left=0.15, right=0.9)
plt.savefig(o_path+o_name+'.jpg', format='jpeg', dpi=300)
plt.close()






