# JHK
# Python script for generating ED Figure 7

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
import os

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Set output path & name
#==========================================================
o_path = hdir+'/fig/'
o_name = 'ED_Figure7'

#==========================================================
# Load linear trend of 7x7 occlusion sensitivity for ERA5 PRCP
#==========================================================
i_path = hdir+'/data/os7/'
i_name = 'DD_ERA5_prcp_lat_1979_2021_trend.nc'
f = Dataset(i_path+i_name, 'r')
era5 = f['p'][0,0]
f.close()

#==========================================================
# Load linear trend of 7x7 occlusion sensitivity for MSWEP PRCP
#==========================================================
i_name = 'DD_MSWEP_prcp_lat_1979_2021_trend.nc'
f = Dataset(i_path+i_name, 'r')
mswep = f['p'][0,0]
f.close()

#==========================================================
# Load linear trend of 7x7 occlusion sensitivity for IMERG HF PRCP
#==========================================================
i_name = 'DD_IMERG_org_prcp_lat_2000_2021_f01_trend.nc'
f = Dataset(i_path+i_name, 'r')
imerg = f['p'][0,0]
f.close()

#==========================================================
# Load linear trend of 7x7 occlusion sensitivity for IMERG HF PRCP
#==========================================================
i_name = 'DD_GPCP_v3.2_prcp_lat_2000_2020_f01_trend.nc'
f = Dataset(i_path+i_name, 'r')
gpcp = f['p'][0,0]
f.close()

#==========================================================
# merging
#==========================================================
occ = np.zeros((3,55,160))
occ[0] = (era5 + mswep) / 2
occ[1] = imerg
occ[2] = gpcp

occ = np.ma.masked_equal(occ, -9.99e+08)
occ = np.ma.masked_equal(occ, 0)

#==========================================================
# plot
#==========================================================
plt.rcParams["figure.figsize"] = [3.6, 4.8]

cmap = plt.cm.get_cmap('RdBu_r')
x, y = np.meshgrid(np.arange(0,400,2.5), np.arange(-61.25,76.25,2.5))

clevs = np.arange(-0.01,0.0101,0.001)

tit_list = [
            'a', 'b', 'c',
            ]

text_list = [
    'Unfiltered PRCP (1980-2020, ERA5+MSWEP)',
    'HF PRCP (2001-2020, IMERG)',
    'HF PRCP (2001-2020, GPCP)'
]

for i in range(3):

    plt.subplot(3,1,i+1)

    if i == 0:
        clevs = np.arange(-0.014,0.01401,0.002)
    elif i == 1:
        clevs = np.arange(-0.014,0.01401,0.002)
    elif i == 2:
        clevs = np.arange(-0.006,0.00601,0.001)

    cax = plt.contourf(x, y, occ[i], clevs, cmap=cmap, extend='both')

    map = Basemap(projection='cyl', llcrnrlat=-55,urcrnrlat=60, resolution='c',
                        llcrnrlon=20, urcrnrlon=380, fix_aspect=True)
    map.drawparallels(np.arange( -90., 90.,30.),labels=[1,0,0,0],fontsize=5.5,
                    color='grey', linewidth=0.3)
    map.drawmeridians(np.arange(0.,380.,60.),labels=[0,0,0,1],fontsize=5.5,
                    color='grey', linewidth=0.3)
    map.drawcoastlines(linewidth=0.4, color='black')

    plt.title(tit_list[i], x=-0.071, y=0.98, fontsize=7, ha='left', weight='bold')
    plt.text(190,62.5,text_list[i],fontsize=6,ha='center')

    if i == 0:
        cax = plt.axes([0.1, 0.71, 0.85, 0.009])
        cbar = plt.colorbar(cax=cax, orientation='horizontal')
        cbar.ax.tick_params(labelsize=5.5,direction='in',length=3.5,width=0.4,color='black',zorder=6)
        plt.text(0.5,-4.5,r'Linear trend of OS (°C decade$^{-1}$)', fontsize=5.5, ha='center')

    elif i == 1:
        cax = plt.axes([0.1, 0.39, 0.85, 0.009])
        cbar = plt.colorbar(cax=cax, orientation='horizontal')
        cbar.ax.tick_params(labelsize=5.5,direction='in',length=3.5,width=0.4,color='black',zorder=6)
        plt.text(0.5,-4.5,r'Linear trend of OS (°C decade$^{-1}$)', fontsize=5.5, ha='center')

    elif i == 2:
        cax = plt.axes([0.1, 0.068, 0.85, 0.009])
        cbar = plt.colorbar(cax=cax, orientation='horizontal')
        cbar.ax.tick_params(labelsize=5.5,direction='in',length=3.5,width=0.4,color='black',zorder=6)
        plt.text(0.5,-4.5,r'Linear trend of OS (°C decade$^{-1}$)', fontsize=5.5, ha='center')

plt.tight_layout(h_pad=4,w_pad=1)
plt.subplots_adjust(bottom=0.10, top=0.95, left=0.10, right=0.95)
plt.savefig(o_path+o_name+'.jpg', format='jpeg', dpi=300)
plt.close()

