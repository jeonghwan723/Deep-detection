# Deep-detection
CNN based climate change detection model

## Processes of the climate change detection

   - Training & validation & test (csh/cnn_run.sh)
   
   - Occlusion sensitivity analysis (csh/cnn_occ.sh)

## Data set (netCDF4)

   -  you can download data set here: now preparing..
   
   -  The data set consists of the following:
   
   
          (1) Training set for training (CESM2 LE): 
          
              Input: [CESM2_LE_prcp_tr.nc]
              Label: [CESM2_LE_agmt_tr.nc]
       
          (2) validation set for training (CESM2 LE):
          
              Input: [CESM2_LE_prcp_val.nc]
              Label: [CESM2_LE_agmt_val.nc]
   
          (3) Test set (ERA5 & IMERG data set):
          
              Input: [ERA5_prcp.nc] and [IMERG_prcp.nc]

## Requirement (python packages)

   -  Tensowflow (> version 2.0, https://www.tensorflow.org/install/)
   -  netCDF4
   -  numpy
   
   
   
