# Deep-detection (DD) model for climate change detection
  The deep detection (DD) model, which refers to the CNN model for detecting climate change signals embedded in daily precipitation anomalies, comprises an input layer, four convolution layers, two pooling layers, one fully connected layer, and an output layer. The size of the convolution kernel, which extracts key features from the input to produce feature maps, is 3x3. Spatial pooling was performed after the first two convolution processes using by 2x2 max pooling with a stride of 2. L2 regularization was applied to minimize overfitting.
 
## Processes of the climate change detection

   - Training & validation & test (csh/cnn_run.sh)
   
   - Occlusion sensitivity analysis (csh/cnn_occ.sh)

## Data set (netCDF4)

   -  you can download data set here: in preparation (33GB).
   
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
   
   
   
