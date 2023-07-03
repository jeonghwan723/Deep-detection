import numpy as np
from netCDF4 import Dataset
import os, pathlib

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Set output path and name
#==========================================================
o_path = hdir+'/data/figure4/'
o_name = 'CPCU_var_change'
pathlib.Path(o_path).mkdir(parents=True,exist_ok=True)

#====================================================================
# Load high frequency (HF) precipitation (PRCP) data 
# of 'CPC unified rain gauge data for CONUS' (1949-2020)
#====================================================================
i_path = hdir+'/data/CPCU/'
i_name = 'CPCU_us_1948_2021_noleap_10hf.nc'
f = Dataset(i_path+i_name,'r')
cpcu = f['prcp'][365:-365,0]
f.close()

tdim, ydim, xdim = cpcu.shape

#====================================================================
# compute variability for each period
#====================================================================
# var1 : variability for 1980-1984
var1 = np.std(cpcu[(1980-1949)*365:(1984-1949)*365].reshape(-1,ydim,xdim), axis=0)

# var2: variability for 2016-2020
var2 = np.std(cpcu[(2016-1949)*365:(2020-1949)*365].reshape(-1,ydim,xdim), axis=0)

# var3: variability for 1960-1979
var3 = np.std(cpcu[(1960-1949)*365:(1979-1949)*365].reshape(-1,ydim,xdim), axis=0)

# var4: variability for 2001-2020
var4 = np.std(cpcu[(2001-1949)*365:(2020-1949)*365].reshape(-1,ydim,xdim), axis=0)

#====================================================================
# compute fractional change [2,120,300]
#====================================================================
diff = np.zeros((2,ydim,xdim))
diff[0] = (var2 - var1) / var1 * 100  # fractional change between 2016-2020 and 1980-1984
diff[1] = (var4 - var3) / var3 * 100  # fractional change between 2001-2020 and 1960-1979

#====================================================================
# save as netCDF4 [2,120,300]
#====================================================================
diff = np.array(diff)
diff.astype('float32').tofile(o_path+o_name+'.gdat')

ctl = open(o_path+o_name+'.ctl','w')
ctl.write('dset ^'+o_name+'.gdat\n')
ctl.write('undef -9.99e+08\n')
ctl.write('xdef   300  linear  230.125 0.25\n')
ctl.write('ydef   120  linear   20.125 0.25\n')
ctl.write('zdef     1  linear 1 1\n')
ctl.write('tdef     2  linear 01jan1948 1dy\n')
ctl.write('vars   1\n')
ctl.write('p   1   1  t1: p2-p1, t2: p4-p3\n')
ctl.write('ENDVARS\n')
ctl.close()

os.system('cdo -f nc import_binary '+o_path+o_name+'.ctl '+o_path+o_name+'.nc')
os.system('rm -f '+o_path+o_name+'.ctl '+o_path+o_name+'.gdat')


