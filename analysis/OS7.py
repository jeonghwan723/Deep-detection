'''
JHK
Python script for computing occlusion sensitivity
'''

import numpy as np
import os
from cdo import Cdo

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/task/ccd_anom_backup'

cdo = Cdo()

f_name_list = [
               'ERA5_prcp_lat_1979_2021_f01',
               'MSWEP_prcp_lat_1979_2021_f01',
               'IMERG_prcp_lat_2000_2021_f01',
               'GPCP_v3.2_prcp_lat_2000_2020_f01'
               ]

for f_name in f_name_list:

    #==========================================================
    # set output path and name
    #==========================================================
    o_path = hdir+'/data/os7/'
    o_name = 'DD_'+f_name

    dat = np.zeros((5,25915,55,160))
    for i in range(5):

        #==========================================================
        # Load result with 7x7 occluding [25915,55,160]
        #==========================================================
        i_path = hdir+'/output/dd_v01/EN'+str(i+1)+'/'
        i_name = 'os7_'+f_name+'.gdat'
        f = open(i_path+i_name, 'r')
        occlusion = np.fromfile(f, np.float32).reshape(-1,55,160)
        f.close()

        occlusion = np.ma.masked_equal(occlusion, 0)

        if i == 0:
            msk = occlusion.mask
        
        #==========================================================
        # open original test result [25915,55,160]
        #==========================================================
        i_path = hdir+'/output/dd_v01/EN'+str(i+1)+'/'
        i_name = f_name+'.gdat'
        f = open(i_path+i_name, 'r')
        fcst = np.fromfile(f, np.float32).reshape(-1,1)
        f.close()

        tdim = len(fcst)

        fcst = np.repeat(fcst, 55*160, axis=1).reshape(-1,55,160)

        #==========================================================
        # scaling
        #==========================================================
        occlusion = occlusion * 10 + 280 - 273.15
        fcst = fcst * 10 + 280 - 273.15

        #==========================================================
        # computing occlusion sensitivity
        # i.e., [original result] - [result with 7x7 occluding]
        #==========================================================
        tmp = fcst - occlusion

        #==========================================================
        # maskout
        #==========================================================
        tmp[msk==True] = 0

        dat[i,:tdim] = tmp
        del occlusion, fcst, tmp

    #==========================================================
    # crop
    #==========================================================
    dat = dat[:,:tdim] 

    #==========================================================
    # ensemble mean [25915,55,160]
    #==========================================================
    dat = np.mean(dat, axis=0)
    dat = np.array(dat)

    #==========================================================
    # Save as netCDF4
    #==========================================================
    dat.astype('float32').tofile(o_path+o_name+'.gdat')

    ctl = open(o_path+o_name+'.ctl','w')
    ctl.write('dset ^'+o_name+'.gdat\n')
    ctl.write('undef -9.99e+08\n')
    ctl.write('xdef 160  linear   0.  2.5\n')
    ctl.write('ydef  55  linear -60.  2.5\n')
    ctl.write('zdef   1  linear 1 1\n')
    ctl.write('tdef '+str(tdim)+'  linear 01jan1979 1dy\n')
    ctl.write('vars   1\n')
    ctl.write('p   1   1  variable\n')
    ctl.write('ENDVARS\n')
    ctl.close()

    cdo.import_binary(input=o_path+o_name+'.ctl', output=o_path+o_name+'.nc', options='-f nc')
    os.system('rm -f '+o_path+o_name+'.ctl '+o_path+o_name+'.gdat')



