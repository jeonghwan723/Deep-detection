from netCDF4 import Dataset
import numpy as np
import os, pathlib

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

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

#====================================================================
# Load high frequency (HF) precipitation (PRCP)
# HF PRCP: 10-day high pass filtered by Lanczos cosine filter
# (from 'Filtering.py')
#====================================================================
# Load ERA5 (1980-2020) [14965,55,160]
i_path = hdir+'/dataset/prcp/filter/'
i_name = 'ERA5_prcp_lat_1979_2021_f01.nc'
f = Dataset(i_path+i_name,'r')
prcp_era5 = f['prcp'][365:-365,0,12:67]
prcp_era5 = np.append(prcp_era5, prcp_era5[:,:,:16], axis=2)
f.close()

# Load MSWEP (1980-2020) [14965,55,160]
i_path = hdir+'/dataset/prcp/filter/'
i_name = 'MSWEP_prcp_lat_1979_2021_f01.nc'
f = Dataset(i_path+i_name,'r')
prcp_mswep = f['prcp'][365:-365,0,12:67]
prcp_mswep = np.append(prcp_mswep, prcp_mswep[:,:,:16], axis=2)
f.close()

# merging [2,14965,55,160]
prcp = np.zeros((2,14965,55,160))
prcp[0] = prcp_era5
prcp[1] = prcp_mswep
del prcp_era5, prcp_mswep

#====================================================================
# crop area (tropics & mid-latitude)
#====================================================================
'''
EP ITECZ region
1: Pacific (200-260E, 0-25N)
2: Amazon (280-310E, 10S-10N)

Mid-latitude storm track region
1: North Pacific (140-235E, 35-60N)
2: North Atlantic (270-325E, 35-60N)
3: Southern ocean (0-360E, 55-40S)
'''

# set area
area = dict()
area[0,0] = [200, 260,   0, 25]
area[0,1] = [280, 310, -10, 10]

area[1,0] = [140, 235, 35, 60]
area[1,1] = [270, 325, 35, 60]
area[1,2] = [0, 360, -55, -40]

#====================================================================
# Function for cropping area
#====================================================================
def crop_area(dat, lon1, lon2, lat1, lat2):

    # crop [7300,55,160] -> [7300,ydim,xdim]
    x1, x2 = lon_to_xdim(lon1, lon2, 2.5, 0)
    y1, y2 = lat_to_ydim(lat1, lat2, 2.5, -60)
    dat_crop = dat[:,y1:y2,x1:x2]

    _, ydim, xdim = dat_crop.shape
    dat_crop = dat_crop.reshape(-1,xdim*ydim)

    return dat_crop

#====================================================================
# Function for computing linear trend
#====================================================================
def compute_trend(dat):

    _, gdim = dat.shape

    # compute STD for each year
    dat = dat.reshape(-1,365,gdim)
    dat = np.std(dat, axis=1)  # [yr,grid]

    # trend - domain avg
    ydim, gdim = dat.shape

    x = np.arange(ydim).reshape(ydim,1) # [yr,1]
    x = np.repeat(x, gdim, axis=1) # [yr,grid]
    x = np.ma.anom(x, axis=0)
    y = np.ma.anom(dat, axis=0)

    xx = np.mean(x**2, axis=0)    
    xy = np.mean(x*y, axis=0)
    trend = xy / xx * 10
    trend = np.mean(trend)

    return trend

for i in range(2):

    if i == 0:
        rname = 'trop'
        n_area = 2

    elif i == 1:
        rname = 'midlat'
        n_area = 3

    # PRCP product (ERA5, MSWEP)
    std_trend = np.zeros((2,2))
    for j in range(2):

        if i == 0 and j == 1:
            n_area = 1

        # crop & merging
        for k in range(n_area):

            if j == 0:
                lon1, lon2, lat1, lat2 = area[i,k]
            else:
                lon1, lon2, lat1, lat2 = area[i,k]

            tmp  = crop_area(prcp[j], lon1, lon2, lat1, lat2)

            if k == 0:
                merge = np.array(tmp)

            else:
                merge = np.append(merge, tmp, axis=1)

            del tmp
        
        # compute linear trend
        p1 = np.array(merge[:])
        p2 = np.array(merge[-20*365:])

        print(p1.shape)
        print(p2.shape)

        std_trend[0,j] = compute_trend(p1)
        std_trend[1,j] = compute_trend(p2)

    std_trend = std_trend.reshape(-1)

    #====================================================================
    # Set output path and name
    #====================================================================
    o_path = hdir+'/data/figure4/'
    o_name = 'std_trend_'+rname
    pathlib.Path(o_path).mkdir(parents=True,exist_ok=True)

    #====================================================================
    # Save as netCDF4
    #====================================================================
    std_trend.astype('float32').tofile(o_path+o_name+'.gdat',)

    ctl = open(o_path+o_name+'.ctl','w')
    ctl.write('dset ^'+o_name+'.gdat\n')
    ctl.write('undef -9.99e+08\n')
    ctl.write('xdef   1  linear   0.0 2.5\n')
    ctl.write('ydef   1  linear -90.0 2.5\n')
    ctl.write('zdef   1   linear  -2  0.5\n')
    ctl.write('tdef   4  linear jan0001 1yr\n')
    ctl.write('vars   1\n')
    ctl.write('p   1  1  STD trend\n')
    ctl.write('ENDVARS\n')
    ctl.close()

    os.system('cdo -f nc import_binary '+o_path+o_name+'.ctl '+o_path+o_name+'.nc')
    os.system('rm -f '+o_path+o_name+'.ctl '+o_path+o_name+'.gdat')


