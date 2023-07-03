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

#==========================================================
# Set output path and name
#==========================================================
o_path = hdir+'/data/figure4/'
o_name = 'ratio_std_mean'
pathlib.Path(o_path).mkdir(parents=True,exist_ok=True)

#==========================================================
# Load total precipitation (PRCP)
#==========================================================
# Total precipitation (ERA5, 1980-2020) [14965,55,144]
i_path = hdir+'/data/'
i_name = 'ERA5_prcp_total_1979_2021.nc'
f = Dataset(i_path+i_name,'r')
era5_tot = f['prcp'][365:-365,0,12:67]
f.close()

# Total precipitation (MSWEP, 1980-2020) [14965,55,144]
i_path = hdir+'/data/'
i_name = 'MSWEP_prcp_total_1979_2021.nc'
f = Dataset(i_path+i_name,'r')
mswep_tot = f['prcp'][365:-365,0,12:67]
f.close()

# merging [2,14965,55,144]
prcp_tot = np.append(era5_tot, mswep_tot, axis=0)
prcp_tot = prcp_tot.reshape(2,14965,55,144)
del era5_tot, mswep_tot

#==========================================================
# Load high frequency (HF) PRCP
# from 'Filtering.py'
#==========================================================
# HF PRCP (ERA5, 1980-2020) [14965,55,144]
i_path = hdir+'/dataset/prcp/filter/'
i_name = 'ERA5_prcp_lat_1979_2021_f01.nc'
f = Dataset(i_path+i_name,'r')
era5_anom_f01 = f['prcp'][365:-365,0,12:67]
f.close()

# HF PRCP (MSWEP, 1980-2020) [14965,55,144]
i_path = hdir+'/dataset/prcp/filter/'
i_name = 'MSWEP_prcp_lat_1979_2021_f01.nc'
f = Dataset(i_path+i_name,'r')
mswep_anom_f01 = f['prcp'][365:-365,0,12:67]
f.close()

# merging [2,14965,55,144]
prcp_anom_f01 = np.append(era5_anom_f01, mswep_anom_f01, axis=0)
prcp_anom_f01 = prcp_anom_f01.reshape(2,14965,55,144)
del era5_anom_f01, mswep_anom_f01

#==========================================================
# Function for computing ratio between ΔSTD and ΔClim
#==========================================================
def compute_ratio(dat1, dat2):

    # compute STD
    _, tdim, gdim = dat1.shape
    dat1 = dat1.reshape(2,-1,365,gdim)
    dat1 = np.std(dat1, axis=2)

    # compute climatology
    dat2 = dat2.reshape(2,-1,365,gdim)
    dat2 = np.mean(dat2, axis=2)

    # compute p1
    p1_f01 = np.mean(dat1[:,:5], axis=1) # [2,gdim]
    p1_tot = np.mean(dat2[:,:5], axis=1) # [2,gdim]

    # compute linear trend [2,tdim,gdim]
    _, tdim, gdim = dat1.shape
    x = np.ma.anom(np.arange(tdim)).reshape(1,tdim,1)
    x = np.repeat(x, 2, axis=0)
    x = np.repeat(x, gdim, axis=2)

    y1 = np.ma.anom(dat1, axis=1) # [2,tdim,gdim]
    y2 = np.ma.anom(dat2, axis=1) # [2,tdim,gdim]

    xx = np.mean(x**2, axis=1)  # [2,gdim]  
    xy1 = np.mean(x*y1, axis=1) # [2,gdim]
    xy2 = np.mean(x*y2, axis=1) # [2,gdim]

    trend1 = xy1 / xx * 10  # [2,gdim]
    trend2 = xy2 / xx * 10  # [2,gdim]

    #=======================================================
    # domain avg - ratio - ratio
    #=======================================================
    dstd = np.mean(trend1, axis=1) / np.mean(p1_f01, axis=1) # [2]
    dclim = np.mean(trend2, axis=1) / np.mean(p1_tot, axis=1) # [2]
    ratio = dstd / dclim

    return ratio

#==========================================================
# crop area & compute ratios for target locations
#==========================================================
'''
EP ITCZ region
1: Pacific (200-260E, 0-25N)
2: Atlantic (280-310E, 10S-10N)

Mid-latitude storm track region
1: North Pacific (140-235E, 35-60N)
2: North Atlantic (270-325E, 35-60N)
3: Southern ocean (0-360E, 55-40S)

Subtropics region
1: North Atlantic (320-360E, 25-40N)
2: South Pacific (245-285E ,35-20S)
'''

area = dict()
area[0,0] = [200, 260, 0, 25]
area[0,1] = [280, 310, -10, 10]

area[1,0] = [140, 235, 35, 60]
area[1,1] = [270, 325, 35, 60]
area[1,2] = [0, 360, -55, -40]

area[2,0] = [320, 360, 25, 40]
area[2,1] = [245, 285, -35, -20]

#==========================================================
# Function for cropping area
#==========================================================
def crop_area(dat, lon1, lon2, lat1, lat2):

    # crop [2,14965,55,160] -> [2,14965,ydim,xdim]
    x1, x2 = lon_to_xdim(lon1, lon2, 2.5, 0)
    y1, y2 = lat_to_ydim(lat1, lat2, 2.5, -60)
    dat_crop = dat[:,:,y1:y2,x1:x2]

    # reshape [2,14965,ydim,xdim] -> [14965,ydim*xdim]
    dat_crop = dat_crop.reshape(2,14965,-1)

    return dat_crop

ratios = np.zeros((3,2))
for i in range(3):

    if i == 0:
        n_area = 2
    elif i == 1:
        n_area = 3
    elif i == 2:
        n_area = 2

    # crop & merging [14965,hdim]
    for j in range(n_area):
        lon1, lon2, lat1, lat2 = area[i,j]
        tmp1 = crop_area(prcp_anom_f01, lon1, lon2, lat1, lat2)
        tmp2 = crop_area(prcp_tot, lon1, lon2, lat1, lat2)

        if j == 0:
            crop_anom_f01 = np.array(tmp1)
            crop_tot = np.array(tmp2)
        
        else:
            crop_anom_f01 = np.append(crop_anom_f01, tmp1, axis=2)
            crop_tot = np.append(crop_tot, tmp2, axis=2)
        
        del tmp1, tmp2
    
    ratios[i] = compute_ratio(crop_anom_f01, crop_tot)

#==========================================================
# save as netCDF4
#==========================================================
ratios = np.array(ratios)
ratios.astype('float32').tofile(o_path+o_name+'.gdat')

ctl = open(o_path+o_name+'.ctl','w')
ctl.write('dset ^'+o_name+'.gdat\n')
ctl.write('undef -9.99e+08\n')
ctl.write('xdef   1  linear   0.0 2.5\n')
ctl.write('ydef   1  linear -90.0 2.5\n')
ctl.write('zdef   2  linear  1  1\n')
ctl.write('tdef   3  linear jan0001 1yr\n')
ctl.write('vars   1\n')
ctl.write('ratio  2  1  t1: tropics, t2: mid_latitude, t3: subtropics\n')
ctl.write('ENDVARS\n')
ctl.close()

os.system('cdo -f nc import_binary '+o_path+o_name+'.ctl '+o_path+o_name+'.nc')
os.system('rm -f '+o_path+o_name+'.ctl '+o_path+o_name+'.gdat')



