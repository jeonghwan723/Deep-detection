
# JHK
# Python script for generating Figure 4.

import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.basemap import Basemap, cm
from pylab import *

#==========================================================
# Set main directory
#==========================================================
hdir = '/home/jhkim/model/deep_detection'

#==========================================================
# Set output path and name
#==========================================================
o_path = hdir+'/fig/'
o_name = 'Figure4'

#==========================================================
# Load STD trend (for panel a) [2,4] [2-region, 2-products x 2-period]
# 1st dim: EP ITCZ and Mid-latitude
# 2nd dim: ERA5 (1980-2020), MSWEP (1980-2020), ERA5 (2001-2020), MSWEP (2001-2020)
# (from '[Figure_4]_1_STD_trend.py')
#==========================================================
std_trend = np.zeros((2,4))

# EP ITCZ region
i_path = hdir+'/data/figure4/'
i_name = 'std_trend_trop.nc'
f = Dataset(i_path+i_name,'r')
std_trend[0,:] = f['p'][:,0,0,0]
f.close()

# mid latitude storm track region
i_name = 'std_trend_midlat.nc'
f = Dataset(i_path+i_name,'r')
std_trend[1,:] = f['p'][:,0,0,0]
f.close()

#==========================================================
# Load HF PRCP variability change (for panel b) [73,144]
# i.e., STD for 2016-2020 minus STD for 2001-2005
# (from '[Figure_4]_2_var_change.py')
#==========================================================
i_name = 'var_change.nc'
f = Dataset(i_path+i_name,'r')
vdiff = f['p'][0,0,:,:]
f.close()

# expansion [73,144] -> [73,153]
vdiff = np.append(vdiff, vdiff[:,:9], axis=1)

#==========================================================
# Load ratio between ΔSTD and ΔClim (for panel c) [3,2] [3-regions, 2-product]
# 1st dim: EP ITCZ, Mid-latitude, Subtropics
# 2nd dim: ERA5 (1980-2020), MSWEP (1980-2020)
# (from '[Figure_4]_3_STD_Clim_ratio.py')
#==========================================================
i_name = 'ratio_std_mean.nc'
f = Dataset(i_path+i_name,'r')
sc_ratio = f['ratio'][:,:,0,0]
f.close()

#==========================================================
# Load HF PRCP var change (for panel d) [2,120,300] [2-period, latitude, longitude]
# (from '[Figure_4]_4_CPCU_var_change.py')
#==========================================================
i_name = 'CPCU_var_change.nc'
f = Dataset(i_path+i_name,'r')
diff = f['p'][:,0,:,:] 
f.close()

# set missing value
diff = np.array(diff)
diff[diff==0] = -9.99e+08
diff = np.ma.masked_equal(diff, -9.99e+08)

#==========================================================
# bootstrap results for STD trend
# (from '[Figure_4]_5_bootstrap_STD_trend.py')
#==========================================================
# bootstrap results (confidence level)
std_trend_up950 = np.array([0.00984413, 0.0300174,  0.00290159, 0.00664675]).reshape(1,4,1)

# expansion [1,4,1] -> [2,4,2] -> [2,2,4]
std_trend_up950 = np.repeat(np.repeat(std_trend_up950, 2, axis=0), 2, axis=2).reshape(2,2,4)

#==========================================================
# bootstrap results for ratio between ΔSTD and ΔClim.
# (from '[Figure_4]_5_bootstrap_STD_Clim_ratio.py')
#==========================================================
sc_ratio_up950 = np.array([0.21500588, 0.08309076, 0.22457268]).reshape(1,3,1)

# expansion [1,3,1] -> [2,3,2]
sc_ratio_up950 = np.repeat(np.repeat(sc_ratio_up950, 2, axis=0), 2, axis=2)

#==========================================================
# plot
#==========================================================
mpl.use('Agg')
plt.rcParams["figure.figsize"] = [6.4, 4.2]
plt.rcParams["pdf.fonttype"] = 42

#==========================================================
# panel (a)
#==========================================================
plt.subplot2grid((27,15),(0,0),rowspan=11,colspan=7)

mpl.rcParams['hatch.linewidth'] = 0.4
plt.rcParams["pdf.fonttype"] = 42
mpl.rcParams['hatch.color'] = 'gray'

x = np.arange(2)
bar1 = plt.bar(x-0.3, std_trend[:,0], 0.2, yerr=std_trend_up950[:,:,0], error_kw=dict(lw=0.6, capsize=2, capthick=0.6),  color='tab:red', edgecolor='black', linewidth=0.0, zorder=6)
bar2 = plt.bar(x-0.1, std_trend[:,1], 0.2, yerr=std_trend_up950[:,:,1],  error_kw=dict(lw=0.6, capsize=2, capthick=0.6), color='tab:blue', edgecolor='black', linewidth=0.0, zorder=6)
bar3 = plt.bar(x+0.1, std_trend[:,2], 0.2, yerr=std_trend_up950[:,:,2],  error_kw=dict(lw=0.6, capsize=2, capthick=0.6), color='tab:red', edgecolor='white', linewidth=0.0, zorder=6, hatch='/////')
bar4 = plt.bar(x+0.3, std_trend[:,3], 0.2, yerr=std_trend_up950[:,:,3],  error_kw=dict(lw=0.6, capsize=2, capthick=0.6), color='tab:blue', edgecolor='white', linewidth=0.0, zorder=6, hatch='/////')

plt.xticks(x, ['EP ITCZ', 'Mid-latitude'])
plt.tick_params(labelsize=6,direction='out',length=1.5,width=0.4,color='black')

plt.ylabel(r'Normalized STD trend', fontsize=6)

plt.xlim([-0.55,1.55])
plt.ylim([0., 0.145])

leg_list1 = ['ERA5', 'MSWEP']
l1 = plt.legend([bar1[0], bar2[0]], leg_list1, 
            loc=(0.47, 0.68), prop={'size':6}, ncol=1, frameon=False)

leg_list2 = ['ERA5', 'MSWEP']
plt.legend([bar3[0], bar4[0]], leg_list2, 
            loc=(0.75, 0.68), prop={'size':6}, ncol=1, frameon=False)

gca().add_artist(l1)

plt.text(x=0.68, y=0.132, s=r'1980$-$2020', fontsize=6, ha='center')
plt.text(x=1.26, y=0.132, s=r'2001$-$2020', fontsize=6, ha='center')

plt.axhline(1.45, xmin=0.455, xmax=0.61, color='black', linestyle='solid', linewidth=0.3, zorder=12)
plt.axhline(1.45, xmin=0.76, xmax=0.915, color='black', linestyle='solid', linewidth=0.3, zorder=12)

plt.title('a', x=-0.1, y=0.96, ha='left', fontsize=8, weight='bold')

#==========================================================
# panel (b)
#==========================================================
plt.subplot2grid((27,19),(15,0),rowspan=12,colspan=13)

cmap = plt.cm.get_cmap('RdBu_r')
x, y = np.meshgrid(np.arange(0,382.5,2.5), np.arange(-91.25,91.25,2.5))
clevs = np.arange(-0.2,0.201,0.02)
clevs = np.delete(clevs, [int(len(clevs)/2)])

cax = plt.contourf(x, y, vdiff, clevs, cmap=cmap, extend='both')

map = Basemap(projection='cyl', llcrnrlat=-55,urcrnrlat=60, resolution='c',
                    llcrnrlon=20, urcrnrlon=380, fix_aspect=False)
map.drawparallels(np.arange( -90., 90.,30.),labels=[1,0,0,0],fontsize=6,
                color='grey', linewidth=0.2)
map.drawmeridians(np.arange(0.,380.,60.),labels=[0,0,0,1],fontsize=6,
                color='grey', linewidth=0.2)
map.drawcoastlines(linewidth=0.4, color='dimgray')

plt.title('b', x=-0.068, y=0.99, fontsize=8, ha='left', weight='bold')

plt.text(190,63,r'Satellite & reanalysis, [2016-20] $-$ [2001-05]', fontsize=7, ha='center')

def draw_box(x1, x2, y1, y2, color):
    x = [x1, x2, x2, x1, x1]
    y = [y1, y1, y2, y2, y1]
    plt.plot(x,y,'black',zorder=4,linewidth=1.0, color=color)

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

# color bar
cax = plt.axes([0.07, 0.09, 0.615, 0.015])
cbar = plt.colorbar(cax=cax, orientation='horizontal', ticks=[-0.2,-0.16,-0.12,-0.08,-0.04,0.04,0.08,0.12,0.16,0.2])
cbar.ax.tick_params(labelsize=6,direction='in',length=5,width=0.4,color='black',zorder=6)
plt.text(0.5,-3.5,r'PRCP Var. Diff. (normallized)', fontsize=6, ha='center')

#==========================================================
# panel (c)
#==========================================================
plt.subplot2grid((27,15),(0,8),rowspan=11,colspan=7)

x = np.arange(3)

plt.bar(x-0.2, sc_ratio[:,0], 0.4, yerr=sc_ratio_up950[:,:,0], error_kw=dict(lw=0.6, capsize=2, capthick=0.6), color='tab:red', edgecolor='black', linewidth=0)
plt.bar(x+0.2, sc_ratio[:,1], 0.4, yerr=sc_ratio_up950[:,:,1], error_kw=dict(lw=0.6, capsize=2, capthick=0.6), color='tab:blue', edgecolor='black', linewidth=0)

plt.xticks(x, ['EP ITCZ', 'Mid-latitude', 'Subtropics'])
plt.tick_params(labelsize=6,direction='out',length=1.5,width=0.4,color='black')
plt.ylabel('Fractional ΔSTD / Frac. ΔClim.', fontsize=6)

plt.title('c', x=-0.1, y=0.96, ha='left', fontsize=8, weight='bold')

plt.text(x=2.18, y=3.85, s='1980-2020', fontsize=6, ha='center')

plt.xlim([-0.6,2.6])
plt.ylim([-0.3,4.3])

plt.legend(['ERA5', 'MSWEP'], bbox_to_anchor=[1, 0.9], prop={'size':6}, ncol=1, edgecolor='white')

plt.axhline(0, linewidth=0.6, color='black', linestyle='--', zorder=7)

#==========================================================
# panel (d)
#==========================================================
plt.subplot2grid((27,19),(15,14),rowspan=5,colspan=5)

cmap = plt.cm.get_cmap('RdBu_r')
clevs = np.arange(-35,35.01,5)
clevs = np.delete(clevs, [int(len(clevs)/2)])

x, y = np.meshgrid(np.arange(230.125,304.8750001,0.25), np.arange(20.125,49.8750001,0.25))

cax = plt.contourf(x, y, diff[0], clevs, cmap=cmap, extend='both', zorder=4)

map = Basemap(projection='cyl', llcrnrlat=25,urcrnrlat=49.1, resolution='c',
                    llcrnrlon=235, urcrnrlon=293, fix_aspect=False)
map.drawparallels(np.arange( -90., 90.,10.),labels=[1,0,0,0],fontsize=6,
                color='grey', linewidth=0.3, zorder=7)
map.drawmeridians(np.arange(0.,380.,20.),labels=[0,0,0,1],fontsize=6,
                color='grey', linewidth=0.3, zorder=7)
map.drawcoastlines(linewidth=0.3, color='gray',zorder=5)
map.fillcontinents(color='lightgray',lake_color='white', alpha=0.5)

plt.title('d', x=-0.11, y=0.90, fontsize=8, ha='left', weight='bold')

draw_box(270, 325, 35, 60, col1)

plt.text(264,56,'CPC rain gauge data', fontsize=7, ha='center')
plt.text(264,50.5,r'[2016-20] $-$ [1980-84]', fontsize=7, ha='center')

#==========================================================
# panel (e)
#==========================================================
plt.subplot2grid((27,19),(22,14),rowspan=5,colspan=5)

cmap = plt.cm.get_cmap('RdBu_r')
clevs = np.arange(-35,35.01,5)
clevs = np.delete(clevs, [int(len(clevs)/2)])

x, y = np.meshgrid(np.arange(230.125,304.8750001,0.25), np.arange(20.125,49.8750001,0.25))

cax = plt.contourf(x, y, diff[1], clevs, cmap=cmap, extend='both', zorder=4)

map = Basemap(projection='cyl', llcrnrlat=25,urcrnrlat=49.1, resolution='c',
                    llcrnrlon=235, urcrnrlon=293, fix_aspect=False)
map.drawparallels(np.arange( -90., 90.,10.),labels=[1,0,0,0],fontsize=6,
                color='grey', linewidth=0.3, zorder=7)
map.drawmeridians(np.arange(0.,380.,20.),labels=[0,0,0,1],fontsize=6,
                color='grey', linewidth=0.3, zorder=7)
map.drawcoastlines(linewidth=0.3, color='gray',zorder=5)
map.fillcontinents(color='lightgray',lake_color='white', alpha=0.5)

plt.title('e', x=-0.11, y=0.90, fontsize=8, ha='left', weight='bold')

plt.text(264,50.5,r'[2001-20] $-$ [1960-79]', fontsize=7, ha='center')

draw_box(270, 325, 35, 60, col1)

# color bar
cax = plt.axes([0.742, 0.09, 0.227, 0.015])
cbar = plt.colorbar(cax=cax, orientation='horizontal', ticks=[-30,-20,-10,10,20,30])
cbar.ax.tick_params(labelsize=6,direction='in',length=5,width=0.4,color='black',zorder=6)
plt.text(0.5,-3.5,r'PRCP Var. Diff. (%)', fontsize=6, ha='center')

plt.subplots_adjust(bottom=0.15, top=0.93, left=0.09, right=0.97)
plt.savefig(o_path+o_name+'.png', dpi=300)
plt.close()
