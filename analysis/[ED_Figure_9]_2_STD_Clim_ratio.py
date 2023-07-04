'''
JHK
Python script for calculating the ratio between dSTD and dClim. of HF PRCP.
'''
import numpy as np
from netCDF4 import Dataset
import os

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Set output path & name
#==========================================================
o_path = hdir+'/data/CPCU/'
o_name = 'CPCU_dstd_dclim_ratio'

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

#===========================================================================
# Function for cropping area
#===========================================================================
def crop_area(dat, lon1, lon2, lat1, lat2):

    tdim = len(dat)

    # crop 
    x1, x2 = lon_to_xdim(lon1, lon2, 0.25, 230.125)
    y1, y2 = lat_to_ydim(lat1, lat2, 0.25, 20.125)
    dat_crop = dat[:,y1:y2,x1:x2]

    # flatten [14965,ydim,xdim] -> [14965,ydim*xdim]
    dat_crop = dat_crop.reshape(tdim,-1)

    return dat_crop

#============================================================
# Load high frequency (HF) preipiction (PRCP) of CPC (1949-2020) [26280,120,300]
# HF PRCP: 10-day high pass filtered PRCP
# (from 'Filtering.py')
#============================================================
i_path = hdir+'/data/CPCU/'
i_name = 'CPCU_us_1948_2021_noleap_10hf.nc'
f = Dataset(i_path+i_name,'r')
anom = f['prcp'][365:-365,0]
f.close()

#============================================================
# Load total PRCP of CPC (1949-2020) [26280,120,300]
#============================================================
i_path = hdir+'/data/CPCU/'
i_name = 'CPCU_us_1948_2021_noleap.nc'
f = Dataset(i_path+i_name,'r')
tot = f['p'][365:-365,0]
f.close()

area = dict()
area[0] = [235,250,30,50] # Western U.S
area[1] = [270,305,35,50] # Eastern U.S

ratio = np.zeros((2,2))
for i in range(2,2):

    lon1, lon2, lat1, lat2 = area[i]

    crop_anom = crop_area(anom, lon1, lon2, lat1, lat2)
    crop_tot = crop_area(tot, lon1, lon2, lat1, lat2)

    tdim, zdim = crop_anom.shape

    crop_anom = crop_anom.reshape(-1,365,zdim)
    crop_tot = crop_tot.reshape(-1,365,zdim)

    #============================================================
    # compute STD for each period
    #============================================================
    std_p1 = np.std(crop_anom[1960-1949:1980-1949].reshape(-1,zdim), axis=0)
    std_p2 = np.std(crop_anom[2001-1949:2021-1949].reshape(-1,zdim), axis=0)
    std_p3 = np.std(crop_anom[1980-1949:1985-1949].reshape(-1,zdim), axis=0)
    std_p4 = np.std(crop_anom[2016-1949:2021-1949].reshape(-1,zdim), axis=0)

    #============================================================
    # compute climatology for each period
    #============================================================
    mean_p1 = np.mean(crop_tot[1960-1949:1980-1949].reshape(-1,zdim), axis=0)
    mean_p2 = np.mean(crop_tot[2001-1949:2021-1949].reshape(-1,zdim), axis=0)
    mean_p3 = np.mean(crop_tot[1980-1949:1985-1949].reshape(-1,zdim), axis=0)
    mean_p4 = np.mean(crop_tot[2016-1949:2021-1949].reshape(-1,zdim), axis=0)

    #============================================================
    # compute ratio
    #============================================================
    dstd1 = np.abs(np.mean((std_p2 - std_p1) / std_p1 * 100))
    dstd2 = np.abs(np.mean((std_p4 - std_p3) / std_p3 * 100))
    dmean1 = np.abs(np.mean((mean_p2 - mean_p1) / mean_p1 * 100))
    dmean2 = np.abs(np.mean((mean_p4 - mean_p3) / mean_p3 * 100))

    #============================================================
    # compute ratio
    #============================================================
    ratio[i,0] = dstd2 / dmean2
    ratio[i,1] = dstd1 / dmean1

#============================================================    
# save as netCDF4
#============================================================
ratio = np.array(ratio)
ratio.astype('float32').tofile(o_path+o_name+'.gdat',)

ctl = open(o_path+o_name+'.ctl','w')
ctl.write('dset ^'+o_name+'.gdat\n')
ctl.write('undef -9.99e+08\n')
ctl.write('xdef   1  linear   0.0 2.5\n')
ctl.write('ydef   1  linear -90.0 2.5\n')
ctl.write('zdef   1   linear  1  1\n')
ctl.write('tdef   2  linear jan0001 1yr\n')
ctl.write('vars   2\n')
ctl.write('p1  1  1  Ratio between dSTD and dClim 2016-2020 minus 1980-1984\n')
ctl.write('p2  1  1  Ratio between dSTD and dClim 2001-2020 minus 1960-1979\n')
ctl.write('ENDVARS\n')
ctl.close()

os.system('cdo -f nc import_binary '+o_path+o_name+'.ctl '+o_path+o_name+'.nc')
os.system('rm -f '+o_path+o_name+'.ctl '+o_path+o_name+'.gdat')
