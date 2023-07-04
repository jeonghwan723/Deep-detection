'''
JHK
Python script for calculating the linear trend of SHAP values.
'''
import numpy as np
from netCDF4 import Dataset
from scipy import signal
import os, pathlib
from scipy import stats

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

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

            slope, intercept, _, pv[i,j], _ = stats.linregress(x, dat[:,i,j])

            tr[i,j] = slope * 365 * 10
    
    return tr, pv


i_name_list = [
    'gshap_ERA5_prcp_lat_1979_2021_f01.nc',
    'gshap_MSWEP_prcp_lat_1979_2021_f01.nc'
    ]

for i_name in i_name_list:

    for i in range(5):

        #==========================================================
        # load DeepSHAP results (15330,55,160)
        #==========================================================
        i_path = hdir+'/output/dd_v01/EN'+str(i+1)+'/'
        f = Dataset(i_path+i_name,'r')

        if i == 0:
            dat = f['p'][365:-365,0]
        else:
            dat = dat + f['p'][365:-365,0]

        f.close()

    #==========================================================
    # ensemble mean
    #==========================================================
    dat = dat / 5

    trend_dat, pval_dat = comp_trend(dat)

    #==========================================================
    # set output path & name
    #==========================================================
    o_path = hdir+'/data/gshap/'
    o_name = i_name[:-3]+'_trend'
    pathlib.Path(o_path).mkdir(parents=True, exist_ok=True)

    #==========================================================
    # save as netCDF4
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

