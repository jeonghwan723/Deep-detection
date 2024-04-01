## Deep detection (DD) model for climate change detection
  The deep detection (DD) model, which refers to the CNN model for detecting climate change signals embedded in daily precipitation anomalies, comprises an input layer, four convolution layers, two pooling layers, one fully connected layer, and an output layer. The size of the convolution kernel, which extracts key features from the input to produce feature maps, is 3x3. Spatial pooling was performed after the first two convolution processes using by 2x2 max pooling with a stride of 2. L2 regularization was applied to minimize overfitting.

  The DD model accepts gridded data of normalized daily precipitation anomalies as an input variable. These anomalies were determined by subtracting the daily climatology data for 1980–2010 and then normalizing it by dividing the longitudinally-averaged standard deviation of the daily precipitation anomalies at the corresponding latitude during the same time period. The input variable has the dimension of 160×55 (2.5°×2.5° resolution over 0°–400°E, 62.5°S–76.5°N). To properly consider the precipitation pattern over around 360°(0°)E, the data was longitudinally extended by concatenating 0°–360°E and 360°–400°E. Through five convolutional and two max-pooling processes, the horizontal dimension of the feature map is reduced to 40 × 14. As the last convolutional layer uses 16 convolutional filters, the size of the dimension of the final feature map is 8,960 (i.e., 40×14×16). Then, each element of the final feature map is connected to the 1st dense layer with 32 neurons, and lastly, 1st dense layer is connected to the 2nd dense layer with a single neuron to output a scalar value representing the AGMT anomaly of the corresponding year. The variability of the estimated annual-mean AGMT anomaly was matched to the observed data to avoid the influence of systematic differences between the training and testing samples. Note that this post-processing did not affect the detection results, as both the test statistics (i.e., internal variability of the estimated AGMT) and detection metric (i.e., AGMT on any specific day) were modified to the same degree.

  We generated five ensemble members with different random initial weights and defined the ensemble-averaged AGMT as the final forecast. The Xavier initialization technique was applied to initialize weights and biases. Tangent hyperbolic and sigmoid functions were used as the activation functions for the convolutional and fully connected layers, respectively. Adam optimization was applied as the gradient descent method, and the mean absolute error was applied as the loss function.

## Repository structure
>Deep-detection/: main directory

>> analysis/: Python scripts for conducting analysis and generagting figures
 
>> csh/: C-shell scripts for constructing DD & ridge regression model, and conducting interpretation techniques

>> sample/: Python sample scripts used in C-shell scripts

## C-shell scripts for constructing DD & ridge regression model, and conducting interpretation techniques (csh/)
- **Training & validation & test of DD model**: <code>dd_run.sh</code>
  
- **Training & test of ridge regression model**: <code>reg_run.sh</code>
  
- **7x7 occlusion sensitivity test for DD model**: <code>dd_os7.sh</code>
  
- **7x7 occlusion sensitivity test for ridge regression model**: <code>reg_os7.sh</code>

- **5x5 occlusion sensitivity test for DD model**: <code>dd_os5.sh</code>

- **Shapley Additive exPlanations (SHAP) with gradient explainer for DD model**: <code>dd_gshap.sh</code>

- **Integrated gradient for DD model**: <code>dd_ig.sh</code>

## Python scripts for generating main figures (analysis/)
- **Figure 1**: <code>[Figure_1]_1_plot.py</code>
  
- **Figure 2**: <code>[Figure_2]_1_bootstrap.py</code> and <code>[Figure_2]_2_plot.py</code>
  
- **Figure 3**: <code>[Figure_3]_1_binning.py</code>, <code>[Figure_3]_2_PDF_ratio.py</code>, and <code>[Figure_3]_3_plot.py</code>
  
- **Figure 4**: <code>[Figure_4]_1_STD_trend.py</code>, <code>[Figure_4]_2_var_change.py</code>, <code>[Figure_4]_3_STD_Clim_ratio.py</code>
                <code>[Figure_4]_4_CPCU_var_change.py</code>, <code>[Figure_4]_5_bootstrap_STD_trend.py</code>, <code>[Figure_4]_6_bootstrap_STD_Clim_ratio.py</code>
                , and <code>[Figure_4]_7_plot.py</code>

## Python scripts for generating extended data (ED) figures (analysis/)
- **ED Fig. 1**: <code>[ED_Figure_1]_1_plot.py</code>
  
- **ED Fig. 3 & 4**: <code>[Figure_1]_1_plot.py</code>
  
- **ED Fig. 5**: <code>[ED_Figure_5]_1_plot.py</code>
  
- **ED Fig. 6**: <code>[ED_Figure_6]_1_OS5_trend.py</code>, <code>[ED_Figure_6]_2_GSHAP_trend.py</code>, <code>[ED_Figure_6]_3_IG_trend.py</code>
                 , and <code>[ED_Figure_6]_4_plot.py</code>
  
- **ED Fig. 7**: <code>[ED_Figure_7]_1_OS7_trend.py</code>, <code>[ED_Figure_7]_2_plot.py</code>
  
- **ED Fig. 8**: <code>[ED_Figure_8]_1_plot.py</code>
  
- **ED Fig. 9**: <code>[ED_Figure_9]_1_std_ratio.py</code>, <code>[ED_Figure_9]_2_STD_Clim_ratio.py</code>, and <code>[ED_Figure_9]_3_plot.py</code>
  
- **ED Fig. 10**: <code>[ED_Figure_10]_1_plot.py</code>

## Data set (netCDF4)
#### You can download data set here (36.1GB): https://drive.google.com/file/d/10KhUscOB8F0Y7j-trMPWxYVXnZV4exmQ/view?usp=sharing
#### The data set consists of the following:
(1) Training set: 
- Input: <code>dataset/prcp/CESM2_LE_prcp_lat_tr.nc</code>
- Label: <code>dataset/agmt/CESM2_LE_agmt_tr.nc</code>
       
(2) validation set:
- Input: <code>dataset/prcp/CESM2_LE_prcp_lat_val.nc</code>
- Label: <code>dataset/agmt/CESM2_LE_agmt_val.nc</code>
   
(3) Test set (observed precipitation products):
          
- Input: <code>dataset/prcp/ERA5_prcp_lat_1979_2021.nc</code>,
         <code>dataset/prcp/MSWEP_prcp_lat_1979_2021.nc</code>,
         <code>dataset/prcp/IMERG_prcp_lat_2000_2021.nc</code>,
         <code>dataset/prcp/GPCP_v3.2_prcp_lat_2000_2020.nc</code>
- Label: <code>dataset/agmt/HadCRUT5_1850_2022.nc</code>

## Requirements
   -  python v3.6.10
   -  tensorflow-gpu v2.1.0
   -  scikit-learn v0.23.1
   -  netcdf4 v1.5.1.2
   -  numpy v1.18.1
   -  scipy v1.1.0
   -  matplotlib v3.1.3
   -  basemap v1.2.0
     
## Our Linux environment
   -  OS: Ubuntu 18.04.6 LTS
   -  GPU: Nvidia Tesla V100
   -  CUDA version: 11.4

## Reference
**Ham, Y. G., Kim, J. H., Min, S. K., Kim, D., Li, T., Timmermann, A., & Stuecker, M. F. (2023). Anthropogenic fingerprints in daily precipitation revealed by deep learning. Nature, 1-7. https://doi.org/10.1038/s41586-023-06474-x**
