'''
JHK
Python script for generating ED figure 5.
'''
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
import os

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

o_path = hdir+'/fig/'
o_name = 'ED_Figure5'

#==============================================================================
# Load total precipitation (MSWEP, 1980-2020)
#==============================================================================
i_path = hdir+'/data/'
i_name = 'MSWEP_prcp_total_1979_2021.nc'
f = Dataset(i_path+i_name,'r')
mswep = f['prcp'][365:-365,0]
f.close()

# split P1 (1980-1984) and P2 (2016-2020) [1825,73,144]
mswep_p1 = mswep[:5*365]
mswep_p2 = mswep[-5*365:]

# average [73,144]
mswep_p1 = np.mean(mswep_p1, axis=0)
mswep_p2 = np.mean(mswep_p2, axis=0)

#==============================================================================
# compute difference between P2 and P1 [73,1441]
#==============================================================================
mswep_change = mswep_p2 - mswep_p1

# expansion from [73,144] to [73,153]
mswep_change = np.append(mswep_change, mswep_change[:,:9], axis=1)

# crop 90S-90N to 60S-75N, [73,153] -> [55,153]
mswep_change = mswep_change[12:67]

#==============================================================================
# Load mean PRCP change of CESM2 LE (2016-2020 minus 1980-1984)
#==============================================================================
i_path = hdir+'/data/'
i_name = 'CESM2_LE_mean_change.nc'
f = Dataset(i_path+i_name,'r')
cesm_change = f['p'][:,0]
f.close()

# ensemble mean
cesm_change = np.mean(cesm_change, axis=0)

# extend [73,153]
cesm_change = np.append(cesm_change, cesm_change[:,:9], axis=1)

# crop 90S-90N to 60S-75N, [73,153] -> [55,153]
cesm_change = cesm_change[12:67]

#==========================================================
# Load fingerprint of ridge regression model (i.e., regression coefficient)
# [55,155]
#==========================================================
i_path = hdir+'/output/reg_v01/prcp/'
i_name = 'coef.nc'
f = Dataset(i_path+i_name,'r')
fing = f['coef'][0,0]
f.close()

# extend [55,144] -> [55,153]
fing = np.append(fing, fing[:,:9], axis=1)

#==============================================================================
# plot
#==============================================================================
plt.rcParams["figure.figsize"] = [3.4, 4.8]

tit_list = [
    'a',
    'b',
    'c'
]

text_list = [
    r'MSWEP, [2016-20] $-$ [1980-84]',
    r'CESM2 LE, [2016-20] $-$ [1980-84]',
    'Fingerprint of ridge regression'
]

x, y = np.meshgrid(np.arange(0,382.5,2.5), np.arange(-61.25,76.25,2.5))

for i in range(3):

    plt.subplot(3,1,i+1)

    if i == 0:
        cmap = plt.cm.get_cmap('BrBG')
        clevs = np.arange(-1.2,1.201,0.2)
        clevs = np.delete(clevs, np.argwhere(clevs==0))
        cax = plt.contourf(x, y, mswep_change, clevs, cmap=cmap, extend='both')

    elif i == 1:
        cmap = plt.cm.get_cmap('BrBG')
        clevs = np.arange(-0.6,0.601,0.1)
        clevs = np.delete(clevs, np.argwhere(clevs==0))
        cax = plt.contourf(x, y, cesm_change, clevs, cmap=cmap, extend='both')
    
    elif i == 2:
        cmap = plt.cm.get_cmap('RdBu_r')
        clevs = np.arange(-0.008,0.00801,0.001)
        clevs = np.delete(clevs, np.argwhere(clevs==0))
        cax = plt.contourf(x, y, fing, clevs, cmap=cmap, extend='both')

    map = Basemap(projection='cyl', llcrnrlat=-55,urcrnrlat=60, resolution='c',
                        llcrnrlon=20, urcrnrlon=380, fix_aspect=True)
    map.drawparallels(np.arange( -90., 90.,30.),labels=[1,0,0,0],fontsize=5.5,
                    color='grey', linewidth=0.3)
    map.drawmeridians(np.arange(0.,380.,60.),labels=[0,0,0,1],fontsize=5.5,
                    color='grey', linewidth=0.3)
    map.drawcoastlines(linewidth=0.4, color='black')

    plt.title(tit_list[i], x=-0.074, y=1, fontsize=7, ha='left', weight='bold')
    plt.text(190,62.5,text_list[i],fontsize=6,ha='center')

    if i == 0:
        cax = plt.axes([0.1, 0.72, 0.85, 0.01])
        cbar = plt.colorbar(cax=cax, orientation='horizontal', ticks=clevs)
        cbar.ax.tick_params(labelsize=6,direction='in',length=3.5,width=0.4,color='black',zorder=6)
        plt.text(0.5,-4.2,r'PRCP Clim. Diff. (mm day$^{-1}$)', fontsize=5.5, ha='center')

    elif i == 1:
        cax = plt.axes([0.1, 0.402, 0.85, 0.01])
        cbar = plt.colorbar(cax=cax, orientation='horizontal', ticks=clevs)
        cbar.ax.tick_params(labelsize=6,direction='in',length=3.5,width=0.4,color='black',zorder=6)
        plt.text(0.5,-4.2,r'PRCP Clim. Diff. (mm day$^{-1}$)', fontsize=5.5, ha='center')

    elif i == 2:
        cax = plt.axes([0.1, 0.08, 0.85, 0.01])
        cbar = plt.colorbar(cax=cax, orientation='horizontal', ticks=[-0.008,-0.006,-0.004,-0.002,0.002,0.004,0.006,0.008])
        cbar.ax.tick_params(labelsize=5.5,direction='in',length=3.5,width=0.4,color='black',zorder=6)
        plt.text(0.5,-4.2,r'Regression coefficient (°C mm$^{-1}$ day$^{-1}$)', fontsize=5.5, ha='center')

plt.tight_layout(h_pad=5,w_pad=1)
plt.subplots_adjust(bottom=0.12, top=0.95, left=0.10, right=0.95)
plt.savefig(o_path+o_name+'.jpg', format='jpeg', dpi=300)
plt.close()


