from netCDF4 import Dataset
import numpy as np
import os, pathlib

#==========================================================
# Script for computing Lanczos cosine filter
# 
# Time filtering for sensitivity test
# f01: 10dy high pass filter
# f02: 10-30dy band pass filter
# f03: 30-90dy band pass filter
# f04: 90-365dy band pass filter
# f05: 365dy low pass filter
#==========================================================

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/task/ccd_anom_backup/'

#==========================================================
# set input path & name
#==========================================================
i_path = hdir+'dataset/'
i_name_list = [
               'ERA5_prcp_lat_1979_2021.nc',
               'MSWEP_prcp_lat_1979_2021.nc',
               'IMERG_prcp_lat_2000_2021.nc',
               'GPCP_v3.2_prcp_lat_2000_2020.nc',
               ]

#==========================================================
# Set output path
#==========================================================
o_path = hdir+'dataset/filter/'
pathlib.Path(o_path).mkdir(parents=True, exist_ok=True)

#==========================================================
# Function for computing Lanczos cosine filtering
#==========================================================
def lanczos(data, typ='band', dt=1, cut1=20, cut2=100, half_w=50, missing=-9.99e+08):

    '''
    # data: input data

    # typ: filter type
        - band: band-pass filter
        - low: low-pass filter
        - high: high-pass filter

    # dt: Delta T
        - daily = 1
        - pentad = 5
        - monthly = 30

    # cut1 & cut2: cut off period
        - ex 1) if you want to conduct 20-100 day band-pass filtering,
                set to cut1 = 20, cut2 = 100
        - ex 2) if you want to donduct 50day low-pass (or high-pass) filtering,
                set to cut1 = 50 (cut2 is not used in this case)

    # half_w: Half number of weight of the function (sinc function)
              It is must be smaller than half of total data size

    # return: first and latest half-w value will replace zero (zero padding)
    '''

    tdim = len(data)
    twopi = 2*np.pi
    weight = half_w * 2 + 1

    cut_frq = np.zeros((2))
    cut_frq[0] = 1/cut1
    cut_frq[1] = 1/cut2

    xl = np.zeros(np.append([2], data.shape))
    xh = np.zeros(np.append([2], data.shape))

    if typ == 'low' or typ == 'high':
      itr = int(1)

    if typ == 'band':
      itr = int(2)

    for k in range(itr):

        #==============================================================================================
        # make HN, Sigma factor, Hn*
        #==============================================================================================
        hn = np.zeros((int(weight)))
        sf = np.zeros((int(weight)))
        hns = np.zeros((int(weight)))
        for i in range(int(-1*half_w),int(half_w+1),1):
            hn[i + half_w]  = 2 * cut_frq[k] * (np.sin(twopi * cut_frq[k] * i * dt) / (twopi * cut_frq[k] * i * dt))
            sf[i + half_w]  = np.sin((twopi * i) / weight) / ((twopi * i) / weight)
            hns[i + half_w] = hn[i + half_w] * sf[i + half_w]
  
            if i == 0:
              hns[half_w] = 2 * cut_frq[k]
        
        #==============================================================================================
        # Normalize (i.e. weight function)
        #==============================================================================================
        hns /= np.sum(hns)

        #==============================================================================================
        # extend
        #==============================================================================================
        res_dim = int(np.prod(data.shape[1:]))
        if res_dim != 1:

            hn = hn.reshape(int(weight), 1)
            sf = sf.reshape(int(weight), 1)
            hns = hns.reshape(int(weight), 1)

            hn = np.repeat(hn, res_dim, axis=1)
            sf = np.repeat(sf, res_dim, axis=1)
            hns = np.repeat(hns, res_dim, axis=1)

            hn = hn.reshape(np.append(int(weight), data.shape[1:]))
            sf = sf.reshape(np.append(int(weight), data.shape[1:]))
            hns = hns.reshape(np.append(int(weight), data.shape[1:]))

        #==============================================================================================
        # Convolution
        #==============================================================================================
        for i in range(half_w, tdim - half_w, 1):
          
            for j in range(weight):

              xl[k, i] = xl[k, i] + data[i + j - half_w] * hns[j]

            xh[k, i] = data[i] - xl[k, i]

    #==============================================================================================
    # return
    #==============================================================================================
    if typ == 'low':
        data = xl[0,:]

    elif typ == 'high':
        data = xh[0,:]

    elif typ == 'band':
        data = xl[0,:] - xl[1,:]

    data = np.array(data)
    data[data==0] = -9.99e+08

    return data

for i_name in i_name_list:

    #==========================================================
    # Load original data [time,lat,lon]
    #==========================================================
    f = Dataset(i_path+i_name,'r')
    dat = f['prcp'][:,0]
    f.close()

    tdim = len(dat)

    for i in range(5):

        #==========================================================
        # time filtering using lanzos cosine filter
        #==========================================================
        if i == 0:
            tmp = lanczos(dat, typ='high', dt=1, cut1=10)
        
        elif i == 1:
            tmp = lanczos(dat, typ='band', dt=1, cut1=10, cut2=30)
        
        elif i == 2:
            tmp = lanczos(dat, typ='band', dt=1, cut1=30, cut2=90)
        
        elif i == 3:
            tmp = lanczos(dat, typ='band', dt=1, cut1=90, cut2=365)

        elif i == 4:
            tmp = lanczos(dat, typ='low', dt=1, cut1=365)

        #==========================================================
        # generate output name
        #==========================================================
        o_name = i_name[:-3]+'_f'+str(i+1).zfill(2)

        #==========================================================
        # save as netCDF4
        #==========================================================
        tmp = np.array(tmp)
        tmp.astype('float32').tofile(o_path+o_name+'.gdat')

        ctl = open(o_path+o_name+'.ctl','w')
        ctl.write('dset ^'+o_name+'.gdat\n')
        ctl.write('undef -9.99e+08\n')
        ctl.write('xdef   144  linear   0.  2.5\n')
        ctl.write('ydef    73  linear -90.  2.5\n')
        ctl.write('zdef     1  linear 1 1\n')
        ctl.write('tdef '+str(tdim)+'  linear 01jan1950 1dy\n')
        ctl.write('vars   1\n')
        ctl.write('prcp    1   1  variable\n')
        ctl.write('ENDVARS\n')
        ctl.close()

        os.system('cdo -f nc import_binary '+o_path+o_name+'.ctl '+o_path+o_name+'.nc')
        os.system('rm -f '+o_path+o_name+'.ctl '+o_path+o_name+'.gdat')

        del tmp


