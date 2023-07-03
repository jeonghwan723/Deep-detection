import numpy as np
from netCDF4 import Dataset
import os, pathlib
from scipy import stats

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

i_name_list = [
               'DD_ERA5_prcp_lat_1979_2021.nc',  # total PRCP
               'DD_MSWEP_prcp_lat_1979_2021.nc',  # total PRCP
               'DD_IMERG_org_prcp_lat_2000_2021_f01.nc', # HF PRCP
               'DD_GPCP_v3.2_prcp_lat_2000_2020_f01.nc' # HF PRCP
               ]

#==========================================================
# Function for computing linear trend [55,160]
#==========================================================
def comp_trend(dat):
    tr = np.zeros((55,160))
    pv = np.zeros((55,160))
    tdim = len(dat)
    x = np.arange(tdim)
    for i in range(55):
        for j in range(160):

            slope, _, _, pv[i,j], _ = stats.linregress(x, dat[:,i,j])

            tr[i,j] = slope * 365 * 10
    
    return tr, pv

for i_name in i_name_list:

    #==========================================================
    # Load data (14965,55,160)
    #==========================================================
    i_path = hdir+'/OS7/'
    f = Dataset(i_path+i_name,'r')
    dat = f['p'][:,0]
    f.close

    #==========================================================
    # Truncate to 1980-2020 for ERA5 and MSWEP, 
    # and 2001-2020 for IMERG and GPCP.
    #
    # GPCP originally had data up to 2020. 
    # However, due to the application of the Lanczos consine filter, data after November 10, 2020 is truncated.
    #==========================================================
    prod = i_name.split('_')[2]

    if prod == 'ERA5' or prod == 'MSWEP':
        dat = dat[365:-365]
    
    elif prod == 'GPCP':
        dat = dat[365:-50]

    elif prod == 'IMERG':
        dat = dat[214:-90]

    #==========================================================
    # Compute linear trend [55,160]
    #==========================================================
    trend_dat, pval_dat = comp_trend(dat)

    #==========================================================
    # Remove non-significant values
    #==========================================================
    trend_dat[pval_dat >= 0.05] = -9.99e+08

    #==========================================================
    # Set output path & name
    #==========================================================
    o_path = hdir+'/data/os7/'
    o_name = i_name[:-3]+'_trend'
    pathlib.Path(o_path).mkdir(parents=True,exist_ok=True)

    #==========================================================
    # Save as netCDF4
    #==========================================================
    trend_dat = np.array(trend_dat)

    trend_dat.astype('float32').tofile(o_path+o_name+'.gdat')

    ctl = open(o_path+o_name+'.ctl','w')
    ctl.write('dset ^'+o_name+'.gdat\n')
    ctl.write('undef -9.99e+08\n')
    ctl.write('xdef 160  linear   0.  2.5\n')
    ctl.write('ydef  55  linear -60.  2.5\n')
    ctl.write('zdef   1  linear 1 1\n')
    ctl.write('tdef   1  linear 01jan0001 1yr\n')
    ctl.write('vars   1\n')
    ctl.write('p    1   1  variable\n')
    ctl.write('ENDVARS\n')
    ctl.close()

    os.system('cdo -f nc import_binary '+o_path+o_name+'.ctl '+o_path+o_name+'.nc')
    os.system('rm -f '+o_path+o_name+'.ctl '+o_path+o_name+'.gdat')

