'''
JHK
Python script for conducting bootstraping for AGMT trend
'''

import numpy as np
from netCDF4 import Dataset

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Load oberved AGMT
#==========================================================
i_path = hdir+'/dataset/'
i_name = 'HadCRUT5_1850_2022.nc'
f = Dataset(i_path+i_name,'r')  
obs_yr = f['tas_mean'][1980-1850:-2]
obs_yr_mean = np.mean(obs_yr[:31]) # climatology for 1980-2010
obs_yr = obs_yr - obs_yr_mean # anomaly
obs_yr_std = np.std(obs_yr[:31]) # STD
f.close()

#==========================================================
# Load estimated AGMT from CESM2 LE (historical, 1850-2014)
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
# computing climatologty (1980-2010)
#==========================================================
cnn_hist_mean = np.mean(cnn_hist[:,(1980-1850)*365:(2011-1850)*365], axis=1)

#==========================================================
# computing anomaly (removing 1980-2010 average)
#==========================================================
for i in range(80):
    cnn_hist[i] = cnn_hist[i] - cnn_hist_mean[i]

#==========================================================
# Computing annual mean [80,1200]
#==========================================================
cnn_hist_yr = np.mean(cnn_hist.reshape(80,-1,365), axis=2)

#==========================================================
# Computing STD of annual mean AGMT (1979-2011) [80]
#==========================================================
cnn_hist_yr_std = np.std(cnn_hist_yr[:,1979-1850:2011-1850], axis=1)

#==========================================================
# STD of daily AGMT match to OBS
#==========================================================
for i in range(80):
    cnn_hist[i] = cnn_hist[i] / cnn_hist_yr_std[i] * obs_yr_std

#==========================================================
# Function for computing linear trend of daily AGMT
#==========================================================
def cal_trend(y):

  x = np.arange(len(y))
  z = np.polyfit(x, y, 1)
  p = np.poly1d(z)

  reg = p[1] * 10 *365

  return p(x), reg

#==========================================================
# computing linear trend of AGMT in 41-year window
# with 5-year spacing
#==========================================================
sig41 = np.zeros((80,12))
for i in range(80):
    for j in range(12):
        _, sig41[i,j] = cal_trend(cnn_hist[i,j*5*365:(41*365)+j*5*365])

sig41 = sig41.reshape(-1)

rank = np.sort(sig41)
upper41 = rank[int((97.5/100)*80*12)]  # 97.5th percentile value
up95_41 = rank[int((95/100)*80*12)]    # 95th percentile value
lower41 = rank[int((2.5/100)*80*12)]   # 2.5th percentile value

print('linear trend with 41yr window')
print('97.5th: ', upper41)
print('95th: ', up95_41)
print('2.5th: ', lower41)

#==========================================================
# computing linear trend of AGMT in 20-year window
# with 10-year spacing
#==========================================================
sig20 = np.zeros((80,9))
for i in range(80):
    for j in range(9):
        _, sig20[i,j] = cal_trend(cnn_hist[i,j*10*365:(20*365)+j*10*365])

sig20 = sig20.reshape(-1)

rank = np.sort(sig20)
upper20 = rank[int((97.5/100)*80*9)] # 97.5th percentile value
up95_20 = rank[int((95/100)*80*9)] # 95th percentile value
lower20 = rank[int((2.5/100)*80*9)] # 2.5th percentile value

print('')
print('linear trend with 20yr window (10 year spacing)')
print('97.5th: ', upper20)
print('95th: ', up95_20)
print('2.5th: ', lower20)

#==========================================================
# 20yr linear trend (5 year spacing)
# with 10-year spacing
#==========================================================
sig20 = np.zeros((80,18))
for i in range(80):
    for j in range(18):
        _, sig20[i,j] = cal_trend(cnn_hist[i,j*5*365:(20*365)+j*5*365])

sig20 = sig20.reshape(-1)

rank = np.sort(sig20)
upper20 = rank[int((97.5/100)*80*18)] # 97.5th percentile value
up95_20 = rank[int((95/100)*80*18)] # 95th percentile value
lower20 = rank[int((2.5/100)*80*18)] # 2.5th percentile value

print('')
print('linear trend with 20yr window (5 year spacing)')
print('97.5th: ', upper20)
print('95th: ', up95_20)
print('2.5th: ', lower20)