# JHK
# Python script for generating Figure 1
# Also, ED Figures 3 and 4 are based on this script.

from netCDF4 import Dataset
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Set output path & name
#==========================================================
o_path = hdir+'/fig/'
o_name = 'Figure1'

#==========================================================
# Function for calculating 2.5th and 97.5th percentile values
# return: 2.5th and 97.5th percentile values [2]
#==========================================================
def em_level(x):
    rank = np.sort(x)
    tdim = len(rank)
    bot25 = rank[int((2.5/100)*tdim)]
    top25 = rank[int((97.5/100)*tdim)]
    level = np.append(bot25, top25)

    return level

#==========================================================
# Function for count the number of emergence days
# *Emergence days: Days above the natural variability
#==========================================================
def cal_doe(x, n_dy, lev):
    doe = np.array(x.reshape(-1,n_dy))
    doe[doe <= lev] = -9.99e+08
    doe[doe > lev] = 1
    doe = np.ma.masked_equal(doe, -9.99e+08)
    doe = np.sum(doe, axis=1) / n_dy * 100
    doe = np.array(doe)
    return doe

#==========================================================
# Function for calculating linear trend
#==========================================================
def cal_trend(y):

  x = np.arange(len(y))
  z = np.polyfit(x, y, 1)
  p = np.poly1d(z)

  reg = np.round(p[1] * 10,1)

  return p(x), reg

#==========================================================
# Load observed AGMT (HadCRUT5)
#==========================================================
i_path = hdir+'/dataset/'
i_name = 'HadCRUT5_1850_2022.nc'
f = Dataset(i_path+i_name,'r')  
obs_yr = f['tas_mean'][1980-1850:-2]
obs_yr_mean = np.mean(obs_yr[:31])
obs_yr = obs_yr - obs_yr_mean
obs_yr_std = np.std(obs_yr[:31])
f.close()

#==========================================================
# Load estimated AGMT (ERA5)
#==========================================================
i_path = hdir+'/output/dd_v01/'
i_name = 'ERA5_prcp_lat_1979_2021.gdat'
f = open(i_path+i_name,'r')
cnn1_dy = np.fromfile(f, np.float32)[365:-365]
cnn1_dy_mean = np.mean(cnn1_dy[:31*365])
cnn1_dy = cnn1_dy - cnn1_dy_mean
cnn1_yr = np.mean(cnn1_dy.reshape(-1,365), axis=1)
cnn1_yr_std = np.std(cnn1_yr[:31])
f.close()

#==========================================================
# Load estimated AGMT (MSWEP)
#==========================================================
i_name = 'MSWEP_prcp_lat_1979_2021.gdat'
f = open(i_path+i_name,'r')
cnn3_dy = np.fromfile(f, np.float32)[365:-365]
cnn3_dy = np.ma.masked_equal(cnn3_dy, -9.99e+08)
cnn3_dy = cnn3_dy - np.mean(cnn3_dy[:31*365])
f.close()   

cnn3_dy = np.ma.masked_equal(cnn3_dy, -9.99e+08)
cnn3_yr = np.mean(cnn3_dy.reshape(-1,365), axis=1)
cnn3_yr_std = np.std(cnn3_yr[:31])

#==========================================================
# Load estimated AGMT (IMERG)
#==========================================================
i_name = 'IMERG_prcp_lat_2000_2021.gdat'
f = open(i_path+i_name,'r')
cnn2_dy = np.full((14965), -9.99e+08)
cnn2_dy[7665:] = np.fromfile(f, np.float32)[214:-90]
cnn2_dy = np.ma.masked_equal(cnn2_dy, -9.99e+08)
cnn2_dy = cnn2_dy - cnn1_dy_mean
f.close()   

cnn2_dy = np.ma.masked_equal(cnn2_dy, -9.99e+08)
cnn2_yr = np.mean(cnn2_dy.reshape(-1,365), axis=1)

#==========================================================
# Load estimated AGMT (GPCP)
#==========================================================
i_name = 'GPCP_v3.2_prcp_lat_2000_2020.gdat'
f = open(i_path+i_name,'r')
cnn4_dy = np.full((14965), -9.99e+08)
cnn4_dy[7665:] = np.fromfile(f, np.float32)[365:]
cnn4_dy = np.ma.masked_equal(cnn4_dy, -9.99e+08)
cnn4_dy = cnn4_dy - cnn1_dy_mean
f.close()   

cnn4_dy = np.ma.masked_equal(cnn4_dy, -9.99e+08)
cnn4_yr = np.mean(cnn4_dy.reshape(-1,365), axis=1)

#==========================================================
# match STD of estimated AGMT to OBS's std
#==========================================================
cnn1_dy = cnn1_dy / cnn1_yr_std * obs_yr_std
cnn1_dy_org = np.array(cnn1_dy)
cnn1_yr = cnn1_yr / cnn1_yr_std * obs_yr_std

cnn2_dy = cnn2_dy / cnn1_yr_std * obs_yr_std
cnn2_yr = cnn2_yr / cnn1_yr_std * obs_yr_std

cnn3_dy = cnn3_dy / cnn3_yr_std * obs_yr_std
cnn3_yr = cnn3_yr / cnn3_yr_std * obs_yr_std

cnn4_dy = cnn4_dy / cnn1_yr_std * obs_yr_std
cnn4_yr = cnn4_yr / cnn1_yr_std * obs_yr_std

#==========================================================
# Load estimated AGMT from PRCP of CESM2 LE (historical period)
#==========================================================
ens_list = [
            '1001.001','1021.002','1041.003','1061.004','1081.005',
            '1101.006','1121.007','1141.008','1161.009','1181.010',
            '1231.001','1231.002','1231.003','1231.004','1231.005',
            '1231.006','1231.007','1231.008','1231.009','1231.010',
            '1231.011','1231.012','1231.013','1231.014','1231.015',
            '1231.016','1231.017','1231.018','1231.019','1231.020',
            '1251.001','1251.002','1251.003','1251.004','1251.005',
            '1251.006','1251.007','1251.008','1251.009','1251.010',
            '1281.001','1281.002','1281.003','1281.004','1281.005',
            '1281.006','1281.007','1281.008','1281.009','1281.010',
            '1281.011','1281.012','1281.013','1281.014','1281.015',
            '1281.016','1281.017','1281.018','1281.019','1281.020',
            '1301.001','1301.002','1301.003','1301.004','1301.005',
            '1301.006','1301.007','1301.008','1301.009','1301.010',
            '1301.011','1301.012','1301.013','1301.014','1301.015',
            '1301.016','1301.017','1301.018','1301.019','1301.020',
            ]

cnn_hist = np.zeros((80,91615))
for i in range(80):
    ens = ens_list[i]
    i_path = hdir+'/output/dd_v01/cesm2_test/'
    i_name = 'cesm2_test_'+ens+'.gdat'
    f = open(i_path+i_name,'r')
    cnn_hist[i] = np.fromfile(f, np.float32)
    f.close()

#==========================================================
# compute 1850-1950 mean [80]
#==========================================================
cnn_hist_mean = np.mean(cnn_hist[:,(1980-1850)*365:(2011-1850)*365], axis=1)

for i in range(80):
    cnn_hist[i] = cnn_hist[i] - cnn_hist_mean[i]

#==========================================================
# annual mean [80,1200]
#==========================================================
cnn_hist_yr = np.mean(cnn_hist.reshape(80,-1,365), axis=2)

#==========================================================
# yearly STD (1950-1979) [80]
#==========================================================
cnn_hist_yr_std = np.std(cnn_hist_yr[:,1980-1850:2011-1850], axis=1)

#==========================================================
# match STD of estimated AGMT to OBS's std
#==========================================================
for i in range(80):
    cnn_hist[i] = cnn_hist[i] / cnn_hist_yr_std[i] * obs_yr_std

#==========================================================
# calculating 2.5th and 97.5th percentile values
#=========================================================
cnn1_lev_dy = np.zeros((80,2))
for i in range(80):
    cnn1_lev_dy[i] = em_level(cnn_hist[i,:(1950-1850)*365])

cnn1_lev_dy = np.mean(cnn1_lev_dy, axis=0)

#==========================================================
# counting the number of emergence days
#==========================================================
doe_cnn1_dy = cal_doe(cnn1_dy, 365, cnn1_lev_dy[1])
doe_cnn2_dy = cal_doe(cnn2_dy, 365, cnn1_lev_dy[1])
doe_cnn3_dy = cal_doe(cnn3_dy, 365, cnn1_lev_dy[1])
doe_cnn4_dy = cal_doe(cnn4_dy, 365, cnn1_lev_dy[1])

#==========================================================
# calculating linear trend
#==========================================================
tr_cnn1_dy, reg_cnn1_dy = cal_trend(doe_cnn1_dy[:])
tr_cnn11_dy, reg_cnn11_dy = cal_trend(doe_cnn1_dy[2001-1980:])
tr_cnn2_dy, reg_cnn2_dy = cal_trend(doe_cnn2_dy[2001-1980:])
tr_cnn3_dy, reg_cnn3_dy = cal_trend(doe_cnn3_dy[:])
tr_cnn31_dy, reg_cnn31_dy = cal_trend(doe_cnn3_dy[2001-1980:])
tr_cnn4_dy, reg_cnn4_dy = cal_trend(doe_cnn4_dy[21:])

#==========================================================
# reshape
#==========================================================
cnn1_dy = cnn1_dy.reshape(41,365)
cnn2_dy = cnn2_dy.reshape(41,365)
cnn3_dy = cnn3_dy.reshape(41,365)
cnn4_dy = cnn4_dy.reshape(41,365)

#==========================================================
# Plot
#==========================================================
matplotlib.use('Agg')
plt.rcParams["figure.figsize"] = [6.4, 4.8]
plt.rcParams["pdf.fonttype"] = 42

tit_size = 9
lab_size = 7
min_size = 7

#==========================================================
# panel (a)
#==========================================================
ax1 = plt.subplot2grid((11,3),(0,0),rowspan=6,colspan=3)

# yearly AGMT
x = np.arange(41)
lines = plt.plot(x, obs_yr, 'black',
                 x, cnn1_yr, 'tab:red',
                 x, cnn3_yr, 'tab:blue',
                 x, cnn2_yr, 'tab:purple',
                 x, cnn4_yr, 'tab:orange')
plt.setp(lines,linewidth=1.4, marker='o', markersize=0, zorder=9, alpha=1.0)

# yearly AGMT (edge)
lines = plt.plot(x, obs_yr, 'white',
                 x, cnn1_yr, 'white',
                 x, cnn3_yr, 'white',
                 x, cnn2_yr, 'white',
                 x, cnn4_yr, 'white')
plt.setp(lines,linewidth=2.0, marker='o', markersize=0, zorder=8, alpha=1.0)

# daily AGMT (ERA5, dot)
x = np.arange(41)
for i in range(365):
    lines = plt.plot(x-0.1, cnn1_dy[:,i], 'tab:red')
    plt.setp(lines,linewidth=0.0, marker='o', markersize=0.8, zorder=4, alpha=0.1)

# daily AGMT (MSWEP, dot)
for i in range(365):
    lines = plt.plot(x+0.1, cnn3_dy[:,i], 'tab:blue')
    plt.setp(lines,linewidth=0.0, marker='o', markersize=0.8, zorder=4, alpha=0.1)

plt.xticks(np.arange(0,41,5), np.arange(1980,2021,5))
plt.yticks(np.arange(-0.6,1.6,0.2))
plt.tick_params(labelsize=min_size,direction='out',length=1.5,width=0.4,color='black')

plt.xlim([-0.3,40.3])
plt.ylim([-0.6,1.4])

# natural (or internal) variability
x = np.append(-0.3, x)
x = np.append(x, 40.3)
line1, line2 = np.full(x.shape, cnn1_lev_dy[0]), np.full(x.shape, cnn1_lev_dy[1])
plt.fill_between(x, line1, line2, facecolor='white', alpha=0.5, edgecolor=None, zorder=7)
plt.axhline(cnn1_lev_dy[0], xmin=0, xmax=1.0, color='black', linestyle='dashed', linewidth=0.8, zorder=12)
plt.axhline(cnn1_lev_dy[1], xmin=0, xmax=1.0, color='black', linestyle='dashed', linewidth=0.8, zorder=12)

plt.title('a', x=-0.075, y=0.97, fontsize=tit_size, ha='left', weight='bold')
plt.ylabel('AGMT (°C)', fontsize=lab_size)

leg_list = ['OBS (HadCRUT5)', 'ERA5', 'MSWEP', 'IMERG', 'GPCP']
plt.legend(leg_list,loc='upper left', prop={'size':min_size}, ncol=5)

#==========================================================
# panel (b)
#==========================================================
plt.subplot2grid((11,2),(7,0),rowspan=4,colspan=1)

# EM day
x = np.arange(41)
lines = plt.plot(x,       doe_cnn1_dy,       'tab:red',
                 x,       doe_cnn3_dy,       'tab:blue',
                 x[21:],  doe_cnn2_dy[21:],  'tab:purple',
                 x[21:],  doe_cnn4_dy[21:],  'tab:orange') 
plt.setp(lines,linewidth=1.2, marker='o', markersize=0, zorder=4, alpha=1.0)

plt.xticks(np.arange(0,41,10), np.arange(1980,2021,10))
plt.tick_params(labelsize=min_size,direction='out',length=1.5,width=0.4,color='black')

plt.xlim([0,40])
plt.ylim([0,100])

plt.title('b', x=-0.165, y=0.97, fontsize=tit_size, ha='left', weight='bold')
plt.xlabel('Year', fontsize=lab_size)
plt.ylabel('Fraction of EM days (%)', fontsize=lab_size)

plt.axhline(10.9, color='black', linestyle='dashed', linewidth=0.8, zorder=12)

leg_list = ['ERA5', 'MSWEP', 'IMERG', 'GPCP']
plt.legend(leg_list,loc='upper left', prop={'size':min_size}, ncol=1, frameon=False)

#==========================================================
# panel (c) - trend
#==========================================================
plt.subplot2grid((11,2),(7,1),rowspan=4,colspan=1)

# linear trend of EM day
bar1 = plt.bar(0, reg_cnn1_dy,  0.9, color='tab:red', edgecolor='black',    linewidth=0)
bar2 = plt.bar(1, reg_cnn3_dy,  0.9, color='tab:blue', edgecolor='black',   linewidth=0)
bar3 = plt.bar(2.5, reg_cnn11_dy, 0.9, color='tab:red', edgecolor='black',    linewidth=0)
bar4 = plt.bar(3.5, reg_cnn31_dy, 0.9, color='tab:blue', edgecolor='black',   linewidth=0)
bar5 = plt.bar(4.5, reg_cnn2_dy,  0.9, color='tab:purple', edgecolor='black', linewidth=0)
bar6 = plt.bar(5.5, reg_cnn4_dy,  0.9, color='tab:orange', edgecolor='black', linewidth=0)

# 95% confidence level for 1979-2020
lines = plt.plot([-0.75,1.75], [1.13, 1.13], 'black', linestyle='--')
plt.setp(lines,linewidth=1.0, marker='o', markersize=0, zorder=8, alpha=1.0)

# 95% confidence level for 2001-2020
lines = plt.plot([1.75,6.25], [3.27, 3.27], 'black', linestyle='--')
plt.setp(lines,linewidth=1.0, marker='o', markersize=0, zorder=8, alpha=1.0)

plt.legend([bar1[0], bar2[0], bar5[0], bar6[0]],leg_list,loc='upper left', prop={'size':min_size}, ncol=1, frameon=False)

plt.xticks([0.5, 4], [r'1980$-$2020', r'2001$-$2020'])
plt.yticks(np.arange(0,41,10))
plt.tick_params(labelsize=min_size,direction='out',length=1.5,width=0.4,color='black')

plt.title('c', x=-0.14, y=0.97, fontsize=tit_size, ha='left', weight='bold')

plt.ylabel(r"Linear trend (% decade$^{-1}$)", fontsize=lab_size)

plt.fill_between([1.75, 6.25], -100, 100, facecolor='black', alpha=0.2, edgecolor=None)

plt.xlim([-0.75, 6.25])
plt.ylim([0, 40])

plt.axhline(0,linewidth=0.5, color='black', linestyle='--')

plt.tight_layout(h_pad=1,w_pad=0.5)
plt.subplots_adjust(bottom=0.1, top=0.93, left=0.1, right=0.95)
plt.savefig(o_path+o_name+'.png', format='png', dpi=300)
plt.close()
