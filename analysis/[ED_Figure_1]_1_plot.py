# JHK
# Python script for generating ED Figure 1

import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from scipy import stats
import os

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Set output path & name
#==========================================================
o_path = hdir+'/fig/'
o_name = 'ED_Figure1'

#==========================================================
# Function to convert to before applying Min-Max scaling
#==========================================================
def scaling(x):
    ts_min, ts_max = 280, 300
    x = (x * (ts_max - ts_min)) + ts_min - 273.15
    return x

#==========================================================
# Function for calculating 2.5th and 97.5th percentile values
# return: 2.5th and 97.5th percentile values [2]
#==========================================================
def em_level(x):
    rank = np.sort(x)
    tdim = len(rank)
    bot25 = rank[int((2.5/100)*tdim)]
    top25 = rank[int((97.5/100)*tdim)]
    return bot25, top25

#==========================================================
# Function for computing moving average (for fist dimension)
#==========================================================
def mov_avg(dat, window_size, msk=-9.99e+08):

    dshape = np.array(dat.shape)
    dshape[0] = dshape[0] - window_size + 1
    dshape = np.append(window_size, dshape)

    mov = np.full(dshape, msk)
    for i in range(window_size):

        if i == window_size-1:
            mov[i] = dat[i:]
        else:
            mov[i] = dat[i:i-window_size+1]

    mov = np.ma.masked_equal(mov, msk)
    mov = np.mean(mov, axis=0)

    mov[mov.mask == True] = msk
    mov = np.ma.masked_equal(mov, msk)

    return mov

#==========================================================================
# Load the AGMT estimated by ridge regression
# from 2m air temperature, surface specific humidity, precipitation
# train & validation: CESM2 pi-Control (latest 150yr) + 2xCO2 (latest 150yr) + 4xCO2 (latest 150yr)
# test: CESM2 Historical + SSP370
#==========================================================================
var_list = ['t2m', 'huss', 'prcp']
scen_list = ['historical', 'ssp370']

fin = np.full((int(251*365),3), -9.99e+08)
for i in range(3):

    var = var_list[i]

    for j in range(2):

        scen = scen_list[j]

        i_path = hdir+'/output/reg_v01_hold/'+var+'/'
        i_name = scen+'.nc'
        f = Dataset(i_path+i_name,'r')
        dat = f['agmt'][:,0,0,0]
        f.close()

        if j == 0:
            fin[:165*365,i] = dat
        
        else:
            fin[165*365:,i] = dat

fin = np.ma.masked_equal(fin, -9.99e+08)

#==========================================================================
# Load ground truth
#==========================================================================
lab = np.full((int(251*365)), -9.99e+08)
i_path = hdir+'/dataset/agmt/'
for i in range(2):

    scen = scen_list[i]

    i_name = scen+'_agmt.nc'
    f = Dataset(i_path+i_name, 'r')
    dat = f['agmt'][:,0,0,0] - 273.15
    f.close()

    if i == 0:
        lab[:165*365] = dat - 3.3
    
    else:
        lab[165*365:] = dat

lab = np.ma.masked_equal(lab, -9.99e+08)

merge = np.array(fin)
merge = np.ma.masked_equal(merge, -9.99e+08)

#==========================================================================
# scaling [251*365,4]
#==========================================================================
merge = scaling(merge)

#==========================================================================
# compute annual mean [251,4]
#==========================================================================
merge_yr = np.mean(merge.reshape(251,365,3), axis=1)
lab_yr = np.mean(lab.reshape(251,365), axis=1)

#==========================================================================
# Compute linear trend (2015-2100) [3]
#==========================================================================
trend = np.zeros((3))
x = np.arange(365*86)
for i in range(3):
    trend[i], _, _, _, _ = stats.linregress(x, merge[165*365:,i])

trend = trend * 365

#=========================================================================
# Compute 2.5th and 97.5th percentile values
#=========================================================================
bot25, top25 = np.zeros((3)), np.zeros((3))
for i in range(3):
    bot25[i], top25[i] = em_level(merge[:(1951-1850)*365,i])

#==========================================================================
# The ratio of the annually-averaged AGMT to the AGMT of upper limit of test statistics 
# (i.e., 97.5th percentile of the daily estimated AGMT in 1850–1950)
#==========================================================================
merge_ratio_yr = np.zeros(merge_yr.shape)
merge_ratio_dy = np.zeros(merge.shape)
for i in range(3):

    merge_ratio_dy[:,i] = merge[:,i]/ top25[i]
    merge_ratio_yr[:,i] = merge_yr[:,i] / top25[i]

#==========================================================================
# mean, STD (1850-1980) [4]
#==========================================================================
merge_mean, merge_std = np.zeros((3)), np.zeros((3))
for i in range(3):
    merge_mean[i] = np.mean(merge[:(1951-1850)*365,i])
    merge_std[i] = np.std(merge[:(1951-1850)*365,i])

bar_bot = merge_mean - (merge_std / 2)
bar_top = merge_std

print(np.round(trend / merge_std * 100, 3))

# top25 [4]
# merge_mean + merge_std [4]
# merge_mean [4]
# merge_mean - merge_std [4]
# bot25 [4]
boxp = np.append(top25, merge_mean + merge_std)
boxp = np.append(boxp, merge_mean)
boxp = np.append(boxp, merge_mean - merge_std)
boxp = np.append(boxp, bot25)

# [5,4]
boxp = boxp.reshape(5,3)

#==========================================================================
# 11-yr moving average
#==========================================================================
merge_ratio_11yr = mov_avg(merge_ratio_yr, 11)
merge_ratio_11yr = np.append(np.zeros((10,3)), merge_ratio_11yr, axis=0)
merge_ratio_11yr = np.ma.masked_equal(merge_ratio_11yr, 0)

#==========================================================================
# Find the first year that the ratio exceeds 1 for each case is indicated as a number.
#==========================================================================
em_yr1 = (len(merge_ratio_11yr[:,0][merge_ratio_11yr[:,0]<1]) ) * 365 
em_yr2 = (len(merge_ratio_11yr[:,1][merge_ratio_11yr[:,1]<1]) ) * 365 
em_yr3 = (len(merge_ratio_11yr[:,2][merge_ratio_11yr[:,2]<1]) ) * 365 

#==========================================================================
# plot
#==========================================================================
plt.rcParams["figure.figsize"] = [6.4, 2.5]
col_list = ['black', 'navy', 'dodgerblue', 'orange', 'red']

#==========================================================================
# panel (a)
#==========================================================================
ax = plt.subplot(1,2,1)

# daily
x = np.arange(0,251*365,365).reshape(251,1)
x = np.repeat(x, 365, axis=1).reshape(-1)

plt.scatter(x, merge[:,2], s=1.0, c='tab:blue', linewidths=0, edgecolors='face')
plt.scatter(x, merge[:,1], s=1.0, c='tab:orange', linewidths=0, edgecolors='face')
plt.scatter(x, merge[:,0], s=1.0, c='tab:green', linewidths=0, edgecolors='face')

line1, line2 = np.full(x.shape, -100), np.full(x.shape, 100)
plt.fill_between(x, line1, line2, facecolor='white', alpha=0.6, edgecolor=None)

# yearly
x = np.arange(0,251*365,365)
lines = plt.plot(x, lab_yr, 'black',
                 x, merge_yr[:,0], 'tab:green',
                 x, merge_yr[:,1], 'tab:orange',
                 x, merge_yr[:,2], 'tab:blue')
plt.setp(lines,linewidth=0.8, marker='o', markersize=0)

plt.xlim([0,300*365-1])
plt.ylim([10,16])

plt.xticks(np.arange(0,251*365,50*365), np.arange(1850,2101,50))
plt.tick_params(labelsize=6,direction='out',length=1.5,width=0.4,color='black')

leg_list = ['Ground truth', 
            'T2m', 
            'SH2m',
            'PRCP']
plt.legend(leg_list,loc='upper left', prop={'size':6}, ncol=1)

plt.axvline(250*365+200, color='black', linewidth=1)

plt.title('a', x=-0.12, y=0.98, fontsize=8, ha='left',weight='bold')

plt.xlabel('Year', fontsize=7)
plt.ylabel('AGMT (°C)', fontsize=7)

# thick bar
ax.add_patch(plt.Rectangle((254*365,bar_bot[0]),365*12, merge_std[0],facecolor='tab:green',
                              clip_on=False,linewidth = 0, zorder=7))

ax.add_patch(plt.Rectangle((269*365,bar_bot[1]),365*12, merge_std[1],facecolor='tab:orange',
                              clip_on=False,linewidth = 0, zorder=7))

ax.add_patch(plt.Rectangle((284*365,bar_bot[2]),365*12, merge_std[2],facecolor='tab:blue',
                              clip_on=False,linewidth = 0, zorder=7))


# error bar
ax.add_patch(plt.Rectangle((259*365+150,bot25[0]), 600, top25[0]-bot25[0],facecolor='black',
                              clip_on=False,linewidth = 0, zorder=6))

ax.add_patch(plt.Rectangle((256*365,bot25[0]), 3000, 0.031,facecolor='black',
                              clip_on=False,linewidth = 0, zorder=6))

ax.add_patch(plt.Rectangle((256*365,top25[0]), 3000, 0.031,facecolor='black',
                              clip_on=False,linewidth = 0, zorder=6))


ax.add_patch(plt.Rectangle((274*365+150,bot25[1]), 600, top25[1]-bot25[1],facecolor='black',
                              clip_on=False,linewidth = 0, zorder=6))

ax.add_patch(plt.Rectangle((271*365,bot25[1]), 3000, 0.031,facecolor='black',
                              clip_on=False,linewidth = 0, zorder=6))

ax.add_patch(plt.Rectangle((271*365,top25[1]), 3000, 0.031,facecolor='black',
                              clip_on=False,linewidth = 0, zorder=6))


ax.add_patch(plt.Rectangle((289*365+150,10), 600, top25[2]-10,facecolor='black',
                              clip_on=False,linewidth = 0, zorder=6))

ax.add_patch(plt.Rectangle((286*365,top25[2]), 3000, 0.031,facecolor='black',
                              clip_on=False,linewidth = 0, zorder=6))

#==========================================================================
# panel (b)                       
#==========================================================================
ax = plt.subplot(1,2,2)

# 11-year mov
x = np.arange(0,251*365,365)
lines = plt.plot(x, merge_ratio_11yr[:,0], 'tab:green',
                 x, merge_ratio_11yr[:,1], 'tab:orange',
                 x, merge_ratio_11yr[:,2], 'tab:blue')
plt.setp(lines,linewidth=1.6, marker='o', markersize=0, zorder=6)

plt.xlim([0,250*365-1])

plt.xticks(np.arange(0,251*365,50*365), np.arange(1850,2101,50))
plt.tick_params(labelsize=6,direction='out',length=1.5,width=0.4,color='black')

plt.title('b', x=-0.12, y=0.98, fontsize=8, ha='left', weight='bold')

plt.xlabel('Year', fontsize=7)
plt.ylabel('AGMT / upper bound', fontsize=7)

plt.axhline(y=1, linewidth=0.5, color='black')
plt.axvline(x=em_yr1, ymin=0, ymax=0.335, linewidth=0.5, linestyle='--', color='tab:green', zorder=6)
plt.axvline(x=em_yr2, ymin=0, ymax=0.335, linewidth=0.5, linestyle='--', color='tab:orange', zorder=6)
plt.axvline(x=em_yr3, ymin=0, ymax=0.335, linewidth=0.5, linestyle='--', color='tab:blue', zorder=6)

line = plt.plot([em_yr1, em_yr1-6700], [1, 1.05], 'tab:green',
                [em_yr2, em_yr2-2000], [1, 1.05], 'tab:orange',
                [em_yr3, em_yr3], [1, 1.05], 'tab:blue')
plt.setp(line,linewidth=0.5, marker='o', markersize=0, linestyle='--', zorder=6)

plt.text(em_yr1-7000, 1.06, str(int(em_yr1/365)+1850), fontsize=6, ha='right', color='tab:green', weight='semibold')
plt.text(em_yr2-2000, 1.06, str(int(em_yr2/365)+1850), fontsize=6, ha='center', color='tab:orange', weight='semibold')
plt.text(em_yr3, 1.06, str(int(em_yr3/365)+1850), fontsize=6, ha='center', color='tab:blue', weight='semibold')

leg_list = ['T2m', 'SH2m', 'PRCP']
leg = plt.legend(leg_list,loc='upper left', prop={'size':6}, ncol=1)
leg.set_zorder(7)

plt.tight_layout(h_pad=1,w_pad=1)
plt.subplots_adjust(bottom=0.15, top=0.88, left=0.07, right=0.96)
plt.savefig(o_path+o_name+'.jpg', format='jpeg', dpi=300)
plt.close()

