# JHK
# Python script for generating ED Figure 9

import matplotlib
matplotlib.use('Agg')
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import os

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Set output path & name
#==========================================================
o_path = hdir+'/fig/'
o_name = 'ED_Figure9'

#==========================================================
# Load data (STD ratio)
# (from '[ED_Figure_9]_1_std_ratio.py')
#==========================================================
i_path = hdir+'/data/CPCU/'
i_name = 'CPCU_std_ratio.nc'
f = Dataset(i_path+i_name,'r')
dat1 = f['p1'][:,0,0,0] # STD ratio [2016-2020] / [1980-1984]
dat3 = f['p2'][:,0,0,0] # STD ratio [2001-2020] / [1960-2020]
f.close()

#==========================================================
# Load data (ratio between delta std and delta Clim.)
# (from '[ED_Figure_9]_2_STD_Clim_ratio.py')
#==========================================================
i_path = hdir+'/data/CPCU/'
i_name = 'CPCU_dstd_dclim_ratio.nc'
f = Dataset(i_path+i_name,'r')
dat2 = f['p1'][:,0,0,0]
dat4 = f['p2'][:,0,0,0]
f.close()

#==========================================================
# plot
#==========================================================
plt.rcParams["figure.figsize"] = [6.4, 4.2]

#==========================================================
# panel (a) - STD ratio (2016-2020 / 1980-1984)
#==========================================================

plt.subplot(2,2,1)
x = np.arange(2)
plt.bar(x, dat1[:], 0.8, color='gray', edgecolor='black', linewidth=0.8, zorder=6)

plt.xticks(x, ['U.S West', 'U.S East'])
#plt.yticks(np.arange(0.9,1.5,0.1))
plt.tick_params(labelsize=7,direction='out',length=1.5,width=0.4,color='black')
plt.ylabel(r'STD ratio', fontsize=8)

plt.xlim([-0.6,1.6])
plt.ylim([0.85, 1.25])

plt.axhline(1, linewidth=0.5, color='black', linestyle='--', zorder=8)

plt.title('(a) STD ratio', x=0, y=0.96, ha='left', fontsize=9)
plt.text(-0.5,1.217,r'[2016-2020] $/$ [1980-1984]', fontsize=7)

#==========================================================
# panel (b) - ratio between STD change and mean change (2016-2020 / 1980-1984)
#==========================================================

plt.subplot(2,2,2)
x = np.arange(2)
plt.bar(x, dat2[:], 0.8, color='gray', edgecolor='black', linewidth=0.8, zorder=6)
#plt.bar(x+0.2, dat2[1,:], 0.4, color='tab:blue', edgecolor='black', linewidth=0.8, zorder=6)

plt.xticks(x, ['U.S West', 'U.S East'])
#plt.yticks(np.arange(0.9,1.5,0.1))
plt.tick_params(labelsize=7,direction='out',length=1.5,width=0.4,color='black')
plt.ylabel('|ΔSTD| / |ΔClim.|', fontsize=8)

plt.xlim([-0.6,1.7])
plt.ylim([0, 2.2])

plt.axhline(1, linewidth=0.5, color='black', linestyle='--', zorder=7)

plt.title('(c) |ΔSTD| / |ΔClim.|', x=0, y=0.96, ha='left', fontsize=9)
plt.text(-0.5,2.0,r'[2016-2020] $-$ [1980-1984]', fontsize=7)

#==========================================================
# panel (c) - STD ratio (2001-2020 minus 1960-1979)
#==========================================================

plt.subplot(2,2,3)
x = np.arange(2)
plt.bar(x, dat3[:], 0.8, color='gray', edgecolor='black', linewidth=0.8, zorder=6)

plt.xticks(x, ['U.S West', 'U.S East'])
plt.tick_params(labelsize=7,direction='out',length=1.5,width=0.4,color='black')
plt.ylabel(r'STD ratio', fontsize=8)

plt.xlim([-0.6,1.6])
plt.ylim([0.85, 1.25])

plt.axhline(1, linewidth=0.5, color='black', linestyle='--', zorder=8)

plt.title('(b) STD ratio', x=0, y=0.96, ha='left', fontsize=9)
plt.text(-0.5,1.217,r'[2001-2020] $/$ [1960-1979]', fontsize=7)

#==========================================================
# panel (d) - ratio between STD change and mean change (2001-2020 minus 1960-1979)
#==========================================================

plt.subplot(2,2,4)
x = np.arange(2)
plt.bar(x, dat4[:], 0.8, color='gray', edgecolor='black', linewidth=0.8, zorder=6)

plt.xticks(x, ['U.S West', 'U.S East'])
plt.tick_params(labelsize=7,direction='out',length=1.5,width=0.4,color='black')
plt.ylabel('|ΔSTD| / |ΔClim.|', fontsize=8)

plt.xlim([-0.6,1.6])
plt.ylim([0.0, 1.3])

plt.axhline(1, linewidth=0.5, color='black', linestyle='--', zorder=7)

plt.title('(d) |ΔSTD| / |ΔClim.|', x=0, y=0.96, ha='left', fontsize=9)
plt.text(-0.5,1.2,r'[2001-2020] $-$ [1960-1979]', fontsize=7)

plt.tight_layout(h_pad=1,w_pad=2)
plt.subplots_adjust(bottom=0.1, top=0.92, left=0.1, right=0.95)
plt.savefig(o_path+o_name+'.png', dpi=300)
