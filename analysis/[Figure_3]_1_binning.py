'''
JHK

Python script for conducting binnning analysis
'''

from netCDF4 import Dataset
import numpy as np
import os, pathlib

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Set output path & name
#==========================================================
o_path = hdir+'/data/figure3/'
o_name1 = 'bin_prcp_occ_dd'
o_name2 = 'bin_prcp_occ_reg'
pathlib.Path(o_path).mkdir(exist_ok=True, parents=True) # generate directory

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

    # crop [14965,55,160] -> [14965,ydim,xdim]
    x1, x2 = lon_to_xdim(lon1, lon2, 2.5, 0)
    y1, y2 = lat_to_ydim(lat1, lat2, 2.5, -60)
    dat_crop = dat[:,y1:y2,x1:x2]

    # flatten [14965,ydim,xdim] -> [14965*ydim*xdim]
    dat_crop = dat_crop.reshape(-1)

    return dat_crop

#===========================================================================
# Function for binning for X, Y according to Y's percentile
#===========================================================================
def binning_perc(x, y, min, max, intv):

    '''
    Function for binning for percentile
    x: 1d array
    y: 1d array
    min: minimum
    max: maximum
    intv: interval (percentile)

    return: binned data [2,n_bin]
    '''

    # compute percentile of dat1
    rank = np.argsort(x)
    tdim = len(x)

    # make bin list
    n_bin = int((max - min) / intv) + 1
    bin_list = []
    for i in range(n_bin):
     
        loc = rank[int((min + (i * intv)) / 100 * tdim) - 1]
        bin_list = np.append(bin_list, x[loc])

    n_bin += 1
       
    # binning
    dat_bin = np.zeros((2,n_bin))
    for i in range(n_bin):

        if i == 0:
            bin = bin_list[i]
            loc = np.argwhere(x >= bin).reshape(-1)

        elif i < (n_bin - 1):
            bin1 = bin_list[i-1]
            bin2 = bin_list[i]
            loc1 = np.argwhere(x < bin1).reshape(-1)
            loc2 = np.argwhere(x >= bin2).reshape(-1)
            loc = np.append(loc1,loc2)
        
        elif i == (n_bin - 1):
            bin = bin_list[i-1]
            loc = np.argwhere(x <= bin).reshape(-1)

        tmp1 = np.delete(x, loc)
        tmp2 = np.delete(y, loc)

        if len(tmp1) == 0:
            dat_bin[0,i] = 0
            dat_bin[1,i] = 0
        else:
            dat_bin[0,i] = np.mean(tmp1)
            dat_bin[1,i] = np.mean(tmp2)

        dat_bin[0,i] = np.mean(tmp1)
        dat_bin[1,i] = np.mean(tmp2)

    return dat_bin

#====================================================================
# load 7x7 occlusion sensitivity (OS) of deep detection (DD) model [14965,55,160]
# (from 'OS7.py')
#====================================================================
i_path = hdir+'/data/os7/'
i_name = 'DD_ERA5_1950_2020_f01.nc'
f = Dataset(i_path+i_name,'r')
occ_dd = np.array(f['p'][30*365:,0])
f.close()

#====================================================================
# load 7x7 OS of ridge regression model [14965,55,160]
# (from 'OS7.py')
#====================================================================
i_name = 'REG_ERA5_1950_2020_f01.nc'
f = Dataset(i_path+i_name,'r')
occ_reg = np.array(f['p'][30*365:,0])
f.close()

#====================================================================
# load observed high frequency (HF) precipitation (PRCP) [14965,55,160]
# HF PRCP: 10day high pass filtered PRCP
# (from 'Filtering.py')
#====================================================================
i_path = hdir+'/dataset/prcp/filter/'
i_name = 'ERA5_prcp_lat_1979_2021_f01.nc'
f = Dataset(i_path+i_name,'r')
prcp = f['prcp'][365:-365,0,12:67]
prcp = np.append(prcp, prcp[:,:,:16], axis=2)
f.close()

#====================================================================
# binning for each area [3,2,20]
#====================================================================
# set area
# A1+2+9, A5+6, A3+7

'''
Tropics
1: Pacific (200-260E, 0-25N)
2: Atlantic (280-310E, 10S-10N)

Mid-latitude
1: North Pacific (140-235E, 35-60N)
2: North Atlantic (270-325E, 35-60N)
3: Southern ocean (0-360E, 55-40S)

Subtropics
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

#====================================================================
# Function for cropping area
#====================================================================
def crop_area(dat, lon1, lon2, lat1, lat2):

    # crop [14965,55,160] -> [14965,ydim,xdim]
    x1, x2 = lon_to_xdim(lon1, lon2, 2.5, 0)
    y1, y2 = lat_to_ydim(lat1, lat2, 2.5, -60)
    dat_crop = dat[:,y1:y2,x1:x2]

    # flatten [14965,ydim,xdim] -> [14965*ydim*xdim]
    dat_crop = dat_crop.reshape(-1)

    return dat_crop

bins_dd, bins_reg = [], []
for i in range(3):

    if i == 0:
        n_area = 2
    elif i == 1:
        n_area = 3
    elif i == 2:
        n_area = 2
    
    # crop & merging & flatten
    occ_dd_crop, occ_reg_crop, prcp_crop = [], [], []
    for j in range(n_area):
        lon1, lon2, lat1, lat2 = area[i,j]
        tmp1 = crop_area(occ_dd, lon1, lon2, lat1, lat2)
        tmp2 = crop_area(occ_reg, lon1, lon2, lat1, lat2)
        tmp3 = crop_area(prcp, lon1, lon2, lat1, lat2)

        occ_dd_crop = np.append(occ_dd_crop, tmp1)
        occ_reg_crop = np.append(occ_reg_crop, tmp2)
        prcp_crop = np.append(prcp_crop, tmp3)
        del tmp1, tmp2, tmp3
        
    # binning (5th to 95th percentile)
    tmp1 = binning_perc(prcp_crop, occ_dd_crop, 5, 95, 5)
    tmp2 = binning_perc(prcp_crop, occ_reg_crop, 5, 95, 5)
    bins_dd = np.append(bins_dd, tmp1)
    bins_reg = np.append(bins_reg, tmp2)
    del tmp1, occ_dd_crop, occ_reg_crop, prcp_crop

# reshape [3,2,20]
bins_dd = bins_dd.reshape(3,2,-1)
bins_reg = bins_reg.reshape(3,2,-1)

n_bin = bins_dd.shape[2]

#====================================================================
# making minimun absolute value to zero [3,2,20]
#====================================================================
for i in range(3):

    loc = np.argsort(np.abs(bins_dd[i,0,:]))[0]

    refer_cnn = bins_dd[i,1,loc]
    refer_reg = bins_reg[i,1,loc]

    bins_dd[i,1,:] = bins_dd[i,1,:] - refer_cnn
    bins_reg[i,1,:] = bins_reg[i,1,:] - refer_reg

#====================================================================
# save as netCDF4
#====================================================================
# save binned data of deep detection
bins_dd.astype('float32').tofile(o_path+o_name1+'.gdat')

ctl = open(o_path+o_name1+'.ctl','w')
ctl.write('dset ^'+o_name1+'.gdat\n')
ctl.write('undef -9.99e+08\n')
ctl.write('xdef  '+str(n_bin)+'  linear   0.  2.5\n')
ctl.write('ydef   2  linear -60.  2.5\n')
ctl.write('zdef   1  linear 1 1\n')
ctl.write('tdef   3  linear 01jan0001 1yr\n')
ctl.write('vars   1\n')
ctl.write('p   1   1  variable\n')
ctl.write('ENDVARS\n')
ctl.close()

os.system('cdo -f nc import_binary '+o_path+o_name1+'.ctl '+o_path+o_name1+'.nc')
os.system('rm -f '+o_path+o_name1+'.ctl '+o_path+o_name1+'.gdat')

# save binned data of ridge regression
bins_reg.astype('float32').tofile(o_path+o_name2+'.gdat')

ctl = open(o_path+o_name2+'.ctl','w')
ctl.write('dset ^'+o_name2+'.gdat\n')
ctl.write('undef -9.99e+08\n')
ctl.write('xdef  '+str(n_bin)+'  linear   0.  2.5\n')
ctl.write('ydef   2  linear -60.  2.5\n')
ctl.write('zdef   1  linear 1 1\n')
ctl.write('tdef   3  linear 01jan0001 1yr\n')
ctl.write('vars   1\n')
ctl.write('p   1   1  variable\n')
ctl.write('ENDVARS\n')
ctl.close()

os.system('cdo -f nc import_binary '+o_path+o_name2+'.ctl '+o_path+o_name2+'.nc')
os.system('rm -f '+o_path+o_name2+'.ctl '+o_path+o_name2+'.gdat')

