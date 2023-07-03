'''
JHK

Python script for computing PDF ratio
*PDF ratio = [PDF of total period] / [PDFs of each decade]
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
o_name = 'pdf_prcp'
pathlib.Path(o_path).mkdir(exist_ok=True, parents=True)

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
# Load high frequency (HF) precipitation (PRCP) data
# HF PRCP: 10day high pass filtered PRCP (from 'Filtering.py')
#====================================================================
# Load ERA5 (1980-2020) [14965,55,160]
i_path = hdir+'/dataset/prcp/filter/'
i_name = 'ERA5_prcp_lat_1979_2021_f01.nc'
f = Dataset(i_path+i_name,'r')
era5 = f['prcp'][365:-365,0,12:67]
era5 = np.append(era5, era5[:,:,:16], axis=2)
f.close()

# Load MSWEP (1980-2020) [14965,55,160]
i_path = hdir+'/dataset/prcp/filter/'
i_name = 'MSWEP_prcp_lat_1979_2021_f01.nc'
f = Dataset(i_path+i_name,'r')
mswep = f['prcp'][365:-365,0,12:67]
mswep = np.append(mswep, mswep[:,:,:16], axis=2)
f.close()

# merging
prcp = np.append(era5, mswep, axis=0)
prcp = prcp.reshape(2,14965,55,160)
del era5, mswep

#====================================================================
# binning for each area [3,2,20]
#====================================================================
# set area
# A1+2+9, A5+6, A3+7

'''
EP ITCZ region
1: Pacific (200-260E, 0-25N)
2: Atlantic (280-310E, 10S-10N)

Mid-latitude storm track region
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

    # crop [2,14965,55,160] -> [2,14965,ydim,xdim]
    x1, x2 = lon_to_xdim(lon1, lon2, 2.5, 0)
    y1, y2 = lat_to_ydim(lat1, lat2, 2.5, -60)
    dat_crop = np.array(dat[:,:,y1:y2,x1:x2])

    # flatten [2,14965,ydim,xdim] -> [2,14965,ydim*xdim]
    dat_crop = dat_crop.reshape(2,14965,-1)

    return dat_crop

#====================================================================
# Function for computing bin list
#====================================================================
def compute_bin_list(x, mini, maxi, intv):

    # compute percentile
    rank = np.argsort(x)
    tdim = len(x)

    # make bin list
    n_bin = int((maxi - mini) / intv) + 1
    bin_list = []
    for i in range(n_bin):
     
        loc = rank[int((mini + (i * intv)) / 100 * tdim) - 1]
        bin_list = np.append(bin_list, x[loc])
    
    return bin_list

#====================================================================
# Function for computing probability density function (PDF)
#====================================================================
def compute_pdf(x, bin_list):

    n_bin = len(bin_list) + 1
    
    # compute PDF
    pdf = np.zeros((n_bin))
    for i in range(n_bin):

        if i == 0:
            pdf[i] = ((x < bin_list[i])).sum()

        elif i < (n_bin-1):
            pdf[i] = ((x >= bin_list[i-1]) & (x < bin_list[i])).sum()

        elif i == (n_bin-1):
            pdf[i] = ((x > bin_list[i-1])).sum()

    total = np.sum(pdf)
    pdf = pdf / total * 100

    return pdf

prcp_pdf1 = []
prcp_pdf2 = []
for i in range(3):

    if i == 0:
        n_area = 2
    elif i == 1:
        n_area = 3
    elif i == 2:
        n_area = 2
    
    # crop & merging
    for j in range(n_area):

        lon1, lon2, lat1, lat2 = area[i,j]

        tmp1 = crop_area(prcp, lon1, lon2, lat1, lat2)

        if j == 0:
            prcp_crop = np.array(tmp1)
        else:
            prcp_crop = np.append(prcp_crop, tmp1, axis=2)

        del tmp1

    # reshape [2,14965,xdim*ydim] -> [41,365,xdim*ydim]
    prcp_crop = prcp_crop.reshape(2,41,365,-1)

    # compute bin list (from 10th to 90th percentile)
    bin_list1 = compute_bin_list(prcp_crop[0].reshape(-1), 10, 90, 10)
    bin_list2 = compute_bin_list(prcp_crop[1].reshape(-1), 10, 90, 10)

    # compute PDF for total period (i.e., 1980-2020)
    pdf_tot1 = compute_pdf(prcp_crop[0].reshape(-1), bin_list=bin_list1) 
    pdf_tot2 = compute_pdf(prcp_crop[1].reshape(-1), bin_list=bin_list2) 
    
    # compute PDF for each decade (i.e., 1980s, 1990s, 2000s, 2010s)
    for j in range(4):
       
        if j == 0:
            tmp2 = compute_pdf(prcp_crop[0,0:11].reshape(-1), bin_list=bin_list1) 
            tmp3 = compute_pdf(prcp_crop[1,0:11].reshape(-1), bin_list=bin_list2) 
            
        else:
            tmp2 = compute_pdf(prcp_crop[0,1+j*10:11+j*10].reshape(-1), bin_list=bin_list1) 
            tmp3 = compute_pdf(prcp_crop[1,1+j*10:11+j*10].reshape(-1), bin_list=bin_list2) 

        # compute PDF ratio (PDF of each decade / PDF of total period)
        prcp_pdf1 = np.append(prcp_pdf1, tmp2 / pdf_tot1)
        prcp_pdf2 = np.append(prcp_pdf2, tmp3 / pdf_tot2)

#====================================================================     
# reshape [3,4,-1]
#====================================================================
prcp_pdf1 = prcp_pdf1.reshape(3,4,-1)
prcp_pdf2 = prcp_pdf2.reshape(3,4,-1)

#====================================================================
# Averaging (ERA5, MSWEP)
#====================================================================
prcp_pdf = (prcp_pdf1 + prcp_pdf2) / 2

n_bin = prcp_pdf.shape[2]

#====================================================================
# save as netCDF4
#====================================================================
prcp_pdf.astype('float32').tofile(o_path+o_name+'.gdat')

ctl = open(o_path+o_name+'.ctl','w')
ctl.write('dset ^'+o_name+'.gdat\n')
ctl.write('undef -9.99e+08\n')
ctl.write('xdef  '+str(n_bin)+'  linear   0.  2.5\n')
ctl.write('ydef   4  linear -60.  2.5\n')
ctl.write('zdef   1  linear 1 1\n')
ctl.write('tdef   3  linear 01jan0001 1yr\n')
ctl.write('vars   1\n')
ctl.write('p   1   1  variable\n')
ctl.write('ENDVARS\n')
ctl.close()

os.system('cdo -f nc import_binary '+o_path+o_name+'.ctl '+o_path+o_name+'.nc')
os.system('rm -f '+o_path+o_name+'.ctl '+o_path+o_name+'.gdat')

