# JHK

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
o_name = 'var_change'
pathlib.Path(o_path).mkdir(parents=True,exist_ok=True)

#====================================================================
# Load HF PRCP of ERA5 (2001-2020) [7300,73,144]
# from 'Filtering.py'
#====================================================================
i_path = hdir+'/dataset/prcp/filter/'
i_name = 'ERA5_prcp_lat_1979_2021_f01.nc'
f = Dataset(i_path+i_name,'r')
era5 = f['prcp'][8030:-365,0]
f.close()

#====================================================================
# Load HF PRCP of MSWEP (2001-2020) [7300,73,144]
# from 'Filtering.py'
#====================================================================
i_name = 'MSWEP_prcp_lat_1979_2021_f01.nc'
f = Dataset(i_path+i_name,'r')
mswep = f['prcp'][8030:-365,0]
f.close()

#====================================================================
# Load HF PRCP of IMERG (2001-2020) [7300,73,144]
# from 'Filtering.py'
#====================================================================
i_name = 'IMERG_prcp_lat_2000_2021_f01.nc'
f = Dataset(i_path+i_name,'r')
imerg = f['prcp'][214:-90,0]
f.close()

#====================================================================
# Load HF PRCP of GPCP (2001-2020) [7300,73,144]
# from 'Filtering.py'
#====================================================================
i_name = 'GPCP_v3.2_prcp_lat_2000_2020_f01.nc'
f = Dataset(i_path+i_name,'r')
gpcp = f['prcp'][365:,0]
f.close()

# crop & compute STD
# p1: 2001-2005
# p2: 2016-2020
era5_p1 = np.std(era5[:5*365], axis=0)
era5_p2 = np.std(era5[-5*365:], axis=0)
mswep_p1 = np.std(mswep[:5*365], axis=0)
mswep_p2 = np.std(mswep[-5*365:], axis=0)
imerg_p1 = np.std(imerg[:5*365], axis=0)
imerg_p2 = np.std(imerg[-5*365:], axis=0)
gpcp_p1 = np.std(gpcp[:5*365], axis=0)
gpcp_p2 = np.std(gpcp[-4*365:], axis=0)

# compute change (difference between P2 and P1)
era5_diff = (era5_p2 - era5_p1)
mswep_diff = (mswep_p2 - mswep_p1)
imerg_diff = (imerg_p2 - imerg_p1)
gpcp_diff = (gpcp_p2 - gpcp_p1)

# average [73,144]
diff = (era5_diff + mswep_diff + imerg_diff + gpcp_diff) / 4
diff = np.array(diff)

#====================================================================
# save as netCDF4 [73,144]
#====================================================================
diff.astype('float32').tofile(o_path+o_name+'.gdat')

ctl = open(o_path+o_name+'.ctl','w')
ctl.write('dset ^'+o_name+'.gdat\n')
ctl.write('undef -9.99e+08\n')
ctl.write('xdef 144  linear   0.  2.5\n')
ctl.write('ydef  73  linear -90.  2.5\n')
ctl.write('zdef   1  linear 1 1\n')
ctl.write('tdef   1  linear 01jan0001 1yr\n')
ctl.write('vars   1\n')
ctl.write('p   1   1  variable\n')
ctl.write('ENDVARS\n')
ctl.close()

os.system('cdo -f nc import_binary '+o_path+o_name+'.ctl '+o_path+o_name+'.nc')
os.system('rm -f '+o_path+o_name+'.ctl '+o_path+o_name+'.gdat')

