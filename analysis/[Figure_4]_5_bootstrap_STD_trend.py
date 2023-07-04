'''
JHK
Python script for calculating internal variability range of linear trend of HF PRCP variability.
'''
import numpy as np
from netCDF4 import Dataset
import os

#===========================================================================
# Function for converting from longitude to X-dimension
#===========================================================================
def lon_to_xdim(lon_st, lon_nd, lon_int=2.5, lon_init=0.0):

  x_st = int( ( ( lon_st - lon_init ) / lon_int ) )
  x_nd = int( ( ( lon_nd - lon_init ) / lon_int ) + 1 )

  return x_st, x_nd

#===========================================================================
# Function for converting latitude to Y-dimension
#===========================================================================
def lat_to_ydim(lat_st, lat_nd, lat_int=2.5, lat_init=-90.0):

  y_st = int( ( lat_st - lat_init ) / lat_int )
  y_nd = int( ( ( lat_nd - lat_init ) / lat_int ) + 1 )

  return y_st, y_nd

#==========================================================
# Function for cropping area
#==========================================================
def crop_area(dat, lon1, lon2, lat1, lat2):

    # crop [2,7300,55,144] -> [2,7300,ydim,xdim]
    x1, x2 = lon_to_xdim(lon1, lon2, 2.5, 0)
    y1, y2 = lat_to_ydim(lat1, lat2, 2.5, -60)
    dat_crop = dat[:,y1:y2,x1:x2]

    _, ydim, xdim = dat_crop.shape
    dat_crop = dat_crop.reshape(-1,xdim*ydim)

    return dat_crop

#==========================================================
# Load estimated AGMT from CESM2 LE (historical, 80 ensemble member)
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

std_trend_41 = np.zeros((2,80,12))  # [area,ens,windows]
std_trend_20 = np.zeros((2,80,17))  # [area,ens,windows]
for i in range(80):

    ens = ens_list[i]
    print(i+1, '/ 80')

    # Load HF PRCP [36500,55,144]
    # from 'Filtering.py'
    i_path = '/home/jhkim/task/ccd_anom_backup/dataset/prcp/cesm2_test_f01/'
    i_name = 'CESM2_LE_prcp_lat_test_'+ens+'.nc'
    f = Dataset(i_path+i_name,'r')
    prcp = f['prcp'][365:37230,0,12:67]
    f.close()

    prcp = np.array(prcp)

    # crop area
    '''
    EP ITCZ region
    1: Pacific (200-260E, 0-25N)
    2: Atlantic (280-310E, 10S-10N)

    Mid-latitude storm track region
    1: North Pacific (140-235E, 35-60N)
    2: North Atlantic (270-325E, 35-60N)
    3: Southern ocean (0-360E, 55-40S)
    '''

    area = dict()
    area[0,0] = [200, 260,   0, 25]
    area[0,1] = [280, 310, -10, 10]

    area[1,0] = [140, 235, 35, 60]
    area[1,1] = [270, 325, 35, 60]
    area[1,2] = [0, 360, -55, -40]

    for j in range(2):

        if j == 0:
            rname = 'trop'
            n_area = 2
        
        elif j == 1:
            rname = 'midlat'
            n_area = 3
        
        #==========================================
        # crop & merging
        #==========================================
        for k in range(n_area):

            lon1, lon2, lat1, lat2 = area[j,k]
            tmp  = crop_area(prcp, lon1, lon2, lat1, lat2)

            if k == 0:
                merge = np.array(tmp)

            else:
                merge = np.append(merge, tmp, axis=1)

            del tmp
        

        #==========================================
        # Compute STD trend for 41yr window
        #==========================================
        for k in range(12):

            window = merge[k*5*365:(41*365)+k*5*365]

            tdim, gdim = window.shape

            window = window.reshape(-1,365,gdim)
            window = np.std(window, axis=1)

            tdim, gdim = window.shape

            x = np.ma.anom(np.arange(tdim)).reshape(tdim,1)
            x = np.repeat(x, gdim, axis=1)
            y = np.ma.anom(window, axis=0)

            xx = np.mean(x**2, axis=0)
            xy = np.mean(x*y, axis=0)

            std_trend_41[j,i,k] = np.mean(xy / xx * 10)

        #==========================================
        # Compute STD trend for 41yr window with 5yr spacing
        #==========================================
        for k in range(17):

            window = merge[k*5*365:(20*365)+k*5*365]
            
            tdim, gdim = window.shape

            window = window.reshape(-1,365,gdim)
            window = np.std(window, axis=1)

            tdim, gdim = window.shape

            x = np.ma.anom(np.arange(tdim)).reshape(tdim,1)
            x = np.repeat(x, gdim, axis=1)
            y = np.ma.anom(window, axis=0)

            xx = np.mean(x**2, axis=0)
            xy = np.mean(x*y, axis=0)

            std_trend_20[j,i,k] = np.mean(xy / xx * 10)

#==========================================
# flatten
#==========================================
std_trend_41 = std_trend_41.reshape(2,-1)
std_trend_20 = std_trend_20.reshape(2,-1)

#==========================================
# sorting
#==========================================
rank_41 = np.sort(std_trend_41, axis=1)
rank_20 = np.sort(std_trend_20, axis=1)

#==========================================
# compute confidence level
#==========================================
# 95th percentile
up950 = np.zeros((4))
up950[0] = rank_41[0,int((95/100)*80*12)]
up950[1] = rank_20[0,int((95/100)*80*17)]
up950[2] = rank_41[1,int((95/100)*80*12)]
up950[3] = rank_20[1,int((95/100)*80*17)]

print(up950)

