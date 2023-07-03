# JHK
# Python script for generating Figure 2.

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.basemap import Basemap, cm
from pylab import *
from scipy import stats
import os, pathlib

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Set output path & name
#==========================================================
o_path = hdir+'/fig/'
o_name = 'Figure2'

#==========================================================
# Bootstrap results
# Obtained from '[Figure_2]_bootstrap.py'
#==========================================================
# 95th percentile of 41yr window
up950_41 = 0.033

# 95th percentile of 20yr window
up950_20 = 0.071

#==========================================================
# computing linear trend of estimated AGMT
#==========================================================
def cal_trend(y):
  tdim = len(y)
  x = np.arange(tdim)
  reg, itcp, _, p, _ = stats.linregress(x, y)
  yhat = x * reg + itcp
  return yhat, reg, p

#==========================================================
# Load observed AGMT (HadCRUT5)
#==========================================================
i_path = hdir+'/dataset/'
i_name = 'HadCRUT5_1850_2022.nc'
f = Dataset(i_path+i_name,'r')  
obs_yr = f['tas_mean'][1950-1850:-2]
obs_yr_mean = np.mean(obs_yr[:30])   # climatology for 1950-1980
obs_yr_mean2 = np.mean(obs_yr[1980-1950:2011-1950])  # climatology for 1980-2010
obs_yr2 = obs_yr - obs_yr_mean2 # anomaly for 1950-1980
obs_yr = obs_yr - obs_yr_mean # anomaly for 1980-2010
obs_yr_std = np.std(obs_yr[:30]) # STD for 1950-1980
obs_yr_std2 = np.std(obs_yr2[1980-1950:2011-1950]) # STD for 1980-2010
f.close()

#==========================================================
# Load estiamted AGMT [data type, experiment type, time]
#
# experiment type
# Total: Estimated AGMT from total daily precipitation
# Trend: Estimated AGMT from linear trend component of daily precipitation
# f01: Estimated AGMT from 10dy high pass filtered PRCP
# f02: Estimated AGMT from 10-30dy band pass filtered PRCP
# f03: Estimated AGMT from 30-90dy band pass filtered PRCP
# f04: Estimated AGMT from 90dy - 1yr band pass filtered PRCP
# f05: Estimated AGMT from 1yr low pass filtered PRCP
#
# f01-f05: Filtered data using the Lanczos cosine filter technique
# See the following Python script: 'Filtering.py'
#
# Period
# ERA5 & MSWEP: 1980-2020
# IMERG & GPCP: 2001-2020 
#
# *GPCP originally had data up to 2020. 
# However, due to the application of the Lanczos consine filter, data after November 10, 2020 is truncated.
#==========================================================
fcst_dy = np.zeros([4,7,14965])
era5_dy = np.zeros([7,25915])

exp_list = ['', '_trend', '_f01', '_f02', '_f03', '_f04', '_f05']
dat_list = [
    'ERA5_prcp_lat_1979_2021',
    'MSWEP_prcp_lat_1979_2021',
    'IMERG_prcp_lat_2000_2021',
    'GPCP_v3.2_prcp_lat_2000_2020',
            ]

for i in range(4):
    for j in range(7):

        i_path = hdir+'/output/dd_v01/'
        i_name = dat_list[i]+exp_list[j]+'.gdat'

        f = open(i_path+i_name,'r')

        # for ERA5
        if i == 0:
            tmp = np.fromfile(f, np.float32)
            fcst_dy[i,j] = tmp[10950:-365]
            era5_dy[j] = tmp[:-365]
        
        # for MSWEP
        elif i == 1:
            tmp = np.fromfile(f, np.float32)
            fcst_dy[i,j] = tmp[365:-365]
        
        # for IMERG
        elif i == 2:
            tmp = np.fromfile(f, np.float32)
            fcst_dy[i,j,7665:] = tmp[214:7514]
        
        # for GPCP
        elif i == 3:
            tmp = np.fromfile(f, np.float32)
            fcst_dy[i,j,7665:-50] = tmp[365:-50]

        f.close()

#==========================================================
# Setting missing value
#==========================================================
fcst_dy[fcst_dy==0] = -9.99e+08
fcst_dy = np.ma.masked_equal(fcst_dy, -9.99e+08)

#==========================================================
# Computing climatology for period 1980-2010
#==========================================================
fcst_mean = np.mean(fcst_dy[:2,:,:32*365], axis=2).reshape(2,7,1)

# IMERG and GPCP do not have the 1950-1980 period, 
# so we used the climatology of ERA5 for these.
fcst_mean = np.append(fcst_mean, fcst_mean[0:1], axis=0)
fcst_mean = np.append(fcst_mean, fcst_mean[0:1], axis=0)
fcst_mean = np.repeat(fcst_mean, 14965, 2)

#==========================================================
# Removing climatology (1950-1980) from total AGMT
# i.e., making anoamalies
#==========================================================
fcst_dy -= fcst_mean  

#==========================================================
# Computing annual mean AGMT
#==========================================================
fcst_yr = fcst_dy.reshape(4,7,41,365)
fcst_yr = np.ma.masked_equal(fcst_yr, -9.99e+08)
fcst_yr = np.mean(fcst_yr, axis=3)    # [4,7,41]
fcst_yr = np.ma.masked_equal(fcst_yr, -9.99e+08)
fcst_dy = np.ma.masked_equal(fcst_dy, -9.99e+08)

#==========================================================
# Computing standard deviation of annual mean AGMT
#==========================================================
era5_yr = np.mean(era5_dy.reshape(7,-1,365), axis=2)  # [7,-1]
fcst_yr_std = np.std(era5_yr[:,:30], axis=1).reshape(1,7,1) # [1,7,1]
fcst_yr_std = np.repeat(fcst_yr_std, 4, 0)  # [4,7,1]
fcst_yr_std1 = np.repeat(fcst_yr_std, 14965, 2)
fcst_yr_std2 = np.repeat(fcst_yr_std, 41, 2)

# MSWEP
mswep_yr_std = np.std(fcst_yr[1,:30], axis=1).reshape(7,1)
mswep_yr_std1 = np.repeat(mswep_yr_std, 14965, 1)
mswep_yr_std2 = np.repeat(mswep_yr_std, 41, 1)

fcst_yr_std1[1] = mswep_yr_std1
fcst_yr_std2[1] = mswep_yr_std2

#==========================================================
# match STD of estimated AGMT to OBS's std
#==========================================================
fcst_yr_corr = fcst_yr / fcst_yr_std2 * obs_yr_std  # [4,7,71]
fcst_dy_corr = fcst_dy / fcst_yr_std1 * obs_yr_std  # [4,7,25915]

# IMERG and GPCP do not have the 1950-1980 period, 
# so we used the STD of ERA5 for these.
fcst_yr_corr[1] = fcst_yr[1] / fcst_yr_std2[1] * obs_yr_std2  # [4,7,71]
fcst_dy_corr[1] = fcst_dy[1] / fcst_yr_std1[1] * obs_yr_std2  # [4,7,25915]

#==========================================================
# compute trend [4,7]
#==========================================================
# linear trend of estimated AGMT and EM day
reg_fcst = np.zeros((4,7))
pval_fcst = np.zeros((4,7))
for i in range(4):
    for j in range(7):

        # linear trend of estimated AGMT for ERA5 & MSWEP (1980-2020)
        if i == 0 or i == 1:
            _, reg_fcst[i,j], pval_fcst[i,j] = cal_trend(fcst_yr_corr[i,j,:])

        # linear trend of estimated AGMT for IMERG & GPCP (2001-2020)
        elif i == 2:
            _, reg_fcst[i,j], pval_fcst[i,j] = cal_trend(fcst_yr_corr[i,j,2001-1980:])

        elif i == 3:
            _, reg_fcst[i,j], pval_fcst[i,j] = cal_trend(fcst_yr_corr[i,j,2001-1980:])

# scaling from [degree per year] to [degree per decade]
reg_fcst *= 10

#==========================================================
# reshape
#==========================================================
fcst_dy = fcst_dy.reshape(4,7,41,365)

#==========================================================
# pre processing for panel (c)
#==========================================================
# load 7x7 occlusion sensitivity (OS) of DD model for ERA5 HF PRCP [14965,55,160]
# See the following Python script: 'OS7.py'
i_path = hdir+'/data/os7/'
i_name = 'DD_ERA5_prcp_lat_1979_2021_f01.nc'
f = Dataset(i_path+i_name,'r')
era5 = np.array(f['p'][365:-365,0]) # crop to 1980-2020
f.close()

# open OS for MSWEP HF PRCP [14965,55,160]
i_path = hdir+'/data/os7/'
i_name = 'DD_MSWEP_prcp_lat_1979_2021_f01.nc'
f = Dataset(i_path+i_name,'r')
mswep = np.array(f['p'][365:-365,0]) # crop to 1980-2020
f.close()

# calculate linear trend of OS [55,160]
def comp_trend(dat):
    tr = np.zeros((55,160))
    pv = np.zeros((55,160))
    tdim = len(dat)
    x = np.arange(tdim)
    for i in range(55):
        for j in range(160):

            slope, intercept, _, pv[i,j], _ = stats.linregress(x, dat[:,i,j])

            tr[i,j] = slope * 365 * 10
    
    return tr, pv

trend_era5, pval_era5 = comp_trend(era5)
trend_mswep, pval_mswep = comp_trend(mswep)

# averaging OS trend
trend_occ = (trend_era5 + trend_mswep) / 2

# merging p-values
pval_occ = np.zeros((2,55,160))
pval_occ[0] = pval_era5
pval_occ[1] = pval_mswep

# Removing smaller p-value
pval_occ = np.max(pval_occ, axis=0)

# maskout by p-value 0.05
trend_occ[pval_occ >= 0.05] = 0
trend_occ = np.ma.masked_equal(trend_occ, 0)

#==========================================================
# Plot
#==========================================================
mpl.use('Agg')
plt.rcParams["figure.figsize"] = [5.8, 4.8]
plt.rcParams["pdf.fonttype"] = 42

#==========================================================
# panel (a)
#==========================================================
plt.subplot(2,2,1)

x = np.arange(7)
bar1 = plt.bar(x-0.2, reg_fcst[0], 0.4, color='tab:red', zorder=5, edgecolor='black', linewidth=0.5)
bar2 = plt.bar(x+0.2, reg_fcst[1], 0.4, color='tab:blue', zorder=5, edgecolor='black', linewidth=0.5)

plt.xticks(x, ['Total', 'Trend', '10d\nHP', '10-30d\nBP', '30-90d\nBP', '90d-1y\nBP', '1y\nLP'])
plt.tick_params(labelsize=6,direction='out',length=2,width=0.4,color='black')

plt.axhline(0, linewidth=0.5, color='black', linestyle='-')
plt.axhline(up950_41, linewidth=0.5, color='black', linestyle='--', zorder=7)

plt.xlabel('Experiments', fontsize=6)
plt.ylabel(r'Linear trend (°C decade$^{-1}$)', fontsize=6)

plt.title('a', x=-0.1, y=0.97, ha='left', fontsize=8, weight='bold')
plt.text(3,0.37, '1980-2020',fontsize=7, ha='center')

plt.xlim([-0.5, 6.5])
plt.ylim([-0.32,0.35])

plt.legend([bar1[0], bar2[0]], ['ERA5', 'MSWEP'], loc='upper right', prop={'size':6}, ncol=1, frameon=False)

plt.fill_between([-0.5, 0.5], -100, 100, facecolor='black', alpha=0.2, edgecolor=None)
plt.fill_between([0.5, 1.5], -100, 100, facecolor='black', alpha=0.1, edgecolor=None)

#==========================================================
# panel (b)
#==========================================================
plt.subplot(2,2,2)

x = np.arange(7)
mpl.rcParams['hatch.linewidth'] = 0.4

bar1 = plt.bar(x-0.2, reg_fcst[2], 0.4, color='tab:purple', zorder=5, edgecolor='black', linewidth=0.5)
bar2 = plt.bar(x+0.2, reg_fcst[3], 0.4, color='tab:orange', zorder=5, edgecolor='black', linewidth=0.5)

plt.xticks(x, ['Total', 'Trend', '10d\nHP', '10-30d\nBP', '30-90d\nBP', '90d-1y\nBP', '1y\nLP'])
plt.tick_params(labelsize=6,direction='out',length=2,width=0.4,color='black')

plt.axhline(0, linewidth=0.5, color='black', linestyle='-')
plt.axhline(up950_20, linewidth=0.5, color='black', linestyle='--', zorder=7)

plt.xlabel('Experiments', fontsize=6)

plt.title('b', x=-0.1, y=0.97, ha='left', fontsize=8, weight='bold')
plt.text(3,0.37, '2001-2020',fontsize=7, ha='center')

plt.xlim([-0.5, 6.5])
plt.ylim([-0.32,0.35])

plt.legend([bar1[0], bar2[0]], ['IMERG', 'GPCP'], loc='upper right', prop={'size':6}, ncol=1, frameon=False)

plt.fill_between([-0.5, 0.5], -100, 100, facecolor='black', alpha=0.2, edgecolor=None)
plt.fill_between([0.5, 1.5], -100, 100, facecolor='black', alpha=0.1, edgecolor=None)

#==========================================================
# panel (c)
#==========================================================
plt.subplot(2,1,2)

cmap = plt.cm.get_cmap('RdBu_r')
x, y = np.meshgrid(np.arange(0,400,2.5), np.arange(-61.25,76.25,2.5))
clevs = np.arange(-0.014,0.01401,0.002)
clevs = np.delete(clevs, [7])

cax = plt.contourf(x, y, trend_occ, clevs, cmap=cmap, extend='both')

map = Basemap(projection='cyl', llcrnrlat=-55,urcrnrlat=60, resolution='c',
                    llcrnrlon=20, urcrnrlon=380, fix_aspect=False)
map.drawparallels(np.arange( -90., 90.,30.),labels=[1,0,0,0],fontsize=6,
                color='grey', linewidth=0.3)
map.drawmeridians(np.arange(0.,380.,60.),labels=[0,0,0,1],fontsize=6,
                color='grey', linewidth=0.3)
map.drawcoastlines(linewidth=0.4, color='dimgray')

plt.text(4, 67, 'c', fontsize=8, ha='left', weight='bold')

# Highlighting hot spot regions
def draw_box(x1, x2, y1, y2, color):
    x = [x1, x2, x2, x1, x1]
    y = [y1, y1, y2, y2, y1]
    plt.plot(x,y,'black',zorder=4,linewidth=0.8, color=color)

col1 = 'black'

# Equatorial Eastern Pacific (200-260E, 0-25N)
draw_box(200, 260, 0, 25, col1)

# Northern part of South America (280-310E, 10S-10N)
draw_box(280, 310, -10, 10, col1)

# North Pacific (140-235E, 35-60N)
draw_box(140, 235, 35, 60, col1)

# North Atlantic (270-325E, 35-60N)
draw_box(270, 325, 35, 60, col1)

# Southern ocean (0-360E, 55-40S)
draw_box(20, 380, -55, -40, col1)

# Colorbar
cax = plt.axes([0.1, 0.095, 0.85, 0.015])
cbar = plt.colorbar(cax=cax, orientation='horizontal', ticks=[-0.012, -0.008, -0.004, 0.004, 0.008, 0.012])
cbar.ax.tick_params(labelsize=6,direction='in',length=5,width=0.4,color='black',zorder=6)
plt.text(0.5,-3.1,r'Linear trend of occlusion sensitivity (°C decade$^{-1}$)', fontsize=6, ha='center')

plt.tight_layout(h_pad=1.,w_pad=0.5)
plt.subplots_adjust(bottom=0.15, top=0.95, left=0.1, right=0.95)
plt.savefig(o_path+o_name+'.png', dpi=300)

