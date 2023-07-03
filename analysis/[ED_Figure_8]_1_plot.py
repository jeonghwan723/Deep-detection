# JHK
# Python script for generating ED Figure 8

import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.basemap import Basemap
import os

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Set output path & name
#==========================================================
o_path = hdir+'/fig/'
o_name = 'ED_Figure8'

#==========================================================
# Load total precipitation (PRCP) (MSWEP, 1980-2020)
#==========================================================
i_path = hdir+'/data/'
i_name = 'MSWEP_prcp_total_1979_2021.nc'
f = Dataset(i_path+i_name,'r')
mswep = f['prcp'][365:-365,0]
f.close()

#==========================================================
# compute climatology (1980-2020)
#==========================================================
mswep_mean = np.mean(mswep, axis=0)

#==========================================================
# Load high frequency (HF) PRCP (MSWEP,1980-2020)
#==========================================================
i_path = hdir+'/dataset/prcp/filter/'
i_name = 'MSWEP_prcp_lat_1979_2021_f01.nc'
f = Dataset(i_path+i_name,'r')
mswep = f['prcp'][365:-365,0]
f.close()

#==========================================================
# compute variability (i.e., standard deviation)
#==========================================================
mswep_var = np.std(mswep, axis=0)

#==========================================================
# Load climatology of CESM2 LE (1980-2020) [80-member,73,144]
#==========================================================
i_path = hdir+'/data/'
i_name = 'CESM2_LE_mean_1980_2020.nc'
f = Dataset(i_path+i_name,'r')
cesm_mean = f['p'][:,0] * 86400 * 1000
f.close()

#==========================================================
# Load variability of CESM2 LE (1980-2020) [80-member,73,144]
#==========================================================
i_path = hdir+'/data/'
i_name = 'CESM2_LE_var_1981_2020.nc'
f = Dataset(i_path+i_name,'r')
cesm_var = f['p'][:,0]
f.close()

#==========================================================
# ensemble mean [1,73,144]
#==========================================================
cesm_mean = np.mean(cesm_mean, axis=0)
cesm_var = np.mean(cesm_var, axis=0)

#==========================================================
# merging
#==========================================================
dat = np.zeros((4,73,144))
dat[0] = mswep_mean
dat[1] = mswep_var
dat[2] = cesm_mean
dat[3] = cesm_var

#==========================================================
# expansion [4,73,144] -> [4,73,153]
#==========================================================
dat = np.append(dat, dat[:,:,:9], axis=2)

#==========================================================
# plot
#==========================================================
mpl.use('Agg')
plt.rcParams["figure.figsize"] = [6.4, 3.2]

tit_list = [
            'a',
            'c',
            'b',
            'd'
            ]

text_list = [
    'PRCP averages (MSWEP)',
    'HF PRCP variability (MSWEP)',
    'PRCP averages (CESM2 LE)',
    'HF PRCP variability (CESM2 LE)',
]

cmap = plt.cm.get_cmap('gist_earth_r')

x, y = np.meshgrid(np.arange(0,382.5,2.5), np.arange(-91.25,91.25,2.5))

for i in range(4):

    plt.subplot(2,2,i+1)

    if i == 0 or i == 2:
        clevs = np.arange(0,10.001,0.5)
    else:
        clevs = np.arange(0,1.601,0.1)

    cax = plt.contourf(x, y, dat[i], clevs, cmap=cmap, extend='max')

    map = Basemap(projection='cyl', llcrnrlat=-55,urcrnrlat=60, resolution='c',
                        llcrnrlon=0, urcrnrlon=360, fix_aspect=True)
    map.drawparallels(np.arange( -90., 90.,30.),labels=[1,0,0,0],fontsize=7,
                    color='grey', linewidth=0.4)
    map.drawmeridians(np.arange(0.,380.,60.),labels=[0,0,0,1],fontsize=7,
                    color='grey', linewidth=0.4)
    map.drawcoastlines(linewidth=0.3)

    plt.title(tit_list[i], x=-0.05, y=1, ha='left', fontsize=8, weight='bold')
    plt.text(180, 63, text_list[i], fontsize=8, ha='center')

    if i == 2:
        cax = plt.axes([0.08, 0.14, 0.42, 0.02])
        cbar = plt.colorbar(cax=cax, orientation='horizontal')
        cbar.ax.tick_params(labelsize=7,direction='in',length=5,width=0.4,color='black',zorder=6)
        plt.text(0.5,-3.8,r'Precpitation (mm day$^{-1}$)', fontsize=7, ha='center')

    elif i == 3:
        cax = plt.axes([0.555, 0.14, 0.42, 0.02])
        cbar = plt.colorbar(cax=cax, orientation='horizontal')
        cbar.ax.tick_params(labelsize=7,direction='in',length=5,width=0.4,color='black',zorder=6)
        plt.text(0.5,-3.8,r'Standard deviation', fontsize=7, ha='center')

plt.tight_layout(h_pad=1,w_pad=0.5)
plt.subplots_adjust(bottom=0.15, top=0.93, left=0.08, right=0.97)
plt.savefig(o_path+o_name+'.jpg', format='jpeg', dpi=300)
plt.close()


