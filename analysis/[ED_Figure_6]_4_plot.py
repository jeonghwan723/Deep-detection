'''
JHK
Python script for generating ED figure 6.
'''
import matplotlib
matplotlib.use('Agg')
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import os

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Set output path & name
#==========================================================
o_path = hdir+'/fig/'
o_name = 'ED_Figure6'

#==================================================================
# Load linear trend of 5x5 'occlusion sensitivity' test [2,55,160]
# for HF PRCP (ERA5 and MSWEP)
# (from '[ED_Figure_6]_1_OS5_trend.py')
#==================================================================
i_name_list = [
               'DD_ERA5_prcp_lat_1979_2021_f01_trend.nc',
               'DD_MSWEP_prcp_lat_1979_2021_f01_trend.nc',
               ]

occ5 = np.zeros((2,55,160))
for i in range(2):

    i_path = hdir+'/data/os5/'
    i_name = i_name_list[i]
    f = Dataset(i_path+i_name,'r')
    occ5[i] = f['p'][0,0]
    f.close()

occ5 = np.ma.masked_equal(occ5, -9.99e+08)
occ5 = np.sum(occ5, axis=0).reshape(1,55,160)

#==================================================================
# Load linear trend of 'Gradient SHAP' [2,55,160]
# for HF PRCP (ERA5 and MSWEP)
# (from '[ED_Figure_6]_2_GSHAP_trend.py')
#==================================================================
i_name_list = [
               'gshap_ERA5_prcp_lat_1979_2021_f01_trend.nc',
               'gshap_MSWEP_prcp_lat_1979_2021_f01_trend.nc',
               ]

gshap = np.zeros((2,55,160))
for i in range(2):

    i_path = hdir+'/data/gshap/'

    # linear trend
    i_name = i_name_list[i]
    f = Dataset(i_path+i_name,'r')
    gshap[i] = f['p'][0,0]
    f.close()

gshap = np.ma.masked_equal(gshap, -9.99e+08)
gshap = np.sum(gshap, axis=0)

# scaling
gshap *= 1000

#==================================================================
# Load linear trend of 'input * integrated gradient' [2,55,160]
# for HF PRCP (ERA5 and MSWEP)
# (from '[ED_Figure_6]_3_IG_trend.py')
#==================================================================
i_name_list = ['ig_ERA5_prcp_lat_1979_2021_f01_trend.nc',
               'ig_MSWEP_prcp_lat_1979_2021_f01_trend.nc',
               ]

ig = np.zeros((2,55,160))
for i in range(2):

    i_path = hdir+'/data/revision_2/ig/'
    i_name = i_name_list[i]
    f = Dataset(i_path+i_name,'r')
    ig[i] = f['p'][0,0]
    f.close()

ig = np.ma.masked_equal(ig, -9.99e+08)
ig = np.sum(ig, axis=0).reshape(1,55,160)

# scaling
ig *= 1000

#==================================================================
# merging [3,55,160]
#==================================================================
merg = np.zeros((3,55,160))
merg[0] = occ5
merg[1] = gshap
merg[2] = ig
del occ5, gshap, ig

merg = np.ma.masked_equal(merg, -9.99e+08)
merg = np.ma.masked_equal(merg, 0)

#==================================================================
# plot
#==================================================================
plt.rcParams["figure.figsize"] = [3.2, 4.8]

text_list = [
    '5x5 occlusion sensitivity',
    'Gradient SHAP',
    'Input x integrated gradient',
            ]

tit_list = ['a','b','c']

for i in range(3):

    plt.subplot(3,1,i+1)

    cmap = plt.cm.get_cmap('RdBu_r')


    clevs = np.arange(-0.02,0.0201,0.002)
    x, y = np.meshgrid(np.arange(0,400,2.5), np.arange(-61.25,76.25,2.5))

    cax = plt.contourf(x, y, merg[i], clevs, cmap=cmap, extend='both')

    map = Basemap(projection='cyl', llcrnrlat=-55,urcrnrlat=60, resolution='c',
                        llcrnrlon=20, urcrnrlon=380, fix_aspect=True)
    map.drawparallels(np.arange( -90., 90.,30.),labels=[1,0,0,0],fontsize=5.5,
                    color='grey', linewidth=0.4)
    map.drawmeridians(np.arange(0.,380.,60.),labels=[0,0,0,1],fontsize=5.5,
                    color='grey', linewidth=0.4)
    map.drawcoastlines(linewidth=0.4, color='dimgray')

    plt.title(tit_list[i], x=-0.07, y=0.99, ha='left', fontsize=7, weight='bold')
    plt.text(190,63,text_list[i],fontsize=6.5,ha='center')

    #==============================================
    # highlight hot spot regions
    #==============================================
    def draw_box(x1, x2, y1, y2, color):
        x = [x1, x2, x2, x1, x1]
        y = [y1, y1, y2, y2, y1]
        plt.plot(x,y,'black',zorder=4,linewidth=0.8, color=color)

    col1 = 'black'

    # Pacific (200-260E, 0-25N)
    draw_box(200, 260, 0, 25, col1)

    # Atlantic (280-310E, 10S-10N)
    draw_box(280, 310, -10, 10, col1)

    # North Pacific (140-235E, 35-60N)
    draw_box(140, 235, 35, 60, col1)

    # North Atlantic (270-325E, 35-60N)
    draw_box(270, 325, 35, 60, col1)

    # Southern ocean (0-360E, 55-40S)
    draw_box(20, 380, -55, -40, col1)

    if i == 0:
        cax = plt.axes([0.1, 0.725, 0.85, 0.010])
        cbar = plt.colorbar(cax=cax, orientation='horizontal')
        cbar.ax.tick_params(labelsize=5.5,direction='in',length=3.5,width=0.4,color='black',zorder=6)
        plt.text(0.5,-4.2,r'Linear trend', fontsize=5.5, ha='center')

    elif i == 1:
        cax = plt.axes([0.1, 0.41, 0.85, 0.010])
        cbar = plt.colorbar(cax=cax, orientation='horizontal')
        cbar.ax.tick_params(labelsize=5.5,direction='in',length=3.5,width=0.4,color='black',zorder=6)
        plt.text(0.5,-4.2,r'Linear trend', fontsize=5.5, ha='center')
        plt.text(1,-4, r'($\times$10$^{-3}$)', fontsize=5.5, ha='center')

    elif i == 2:
        cax = plt.axes([0.1, 0.094, 0.85, 0.010])
        cbar = plt.colorbar(cax=cax, orientation='horizontal')
        cbar.ax.tick_params(labelsize=5.5,direction='in',length=3.5,width=0.4,color='black',zorder=6)
        plt.text(0.5,-4.2,r'Linear trend', fontsize=5.5, ha='center')
        plt.text(1,-4, r'($\times$10$^{-3}$)', fontsize=5.5, ha='center')

plt.tight_layout(h_pad=5,w_pad=1)
plt.subplots_adjust(bottom=0.12, top=0.95, left=0.1, right=0.95)
plt.savefig(o_path+o_name+'.jpg', format='jpeg', dpi=300)
plt.close()


