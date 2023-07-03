#!/bin/csh
# JHK

# c-shell script for 7x7 occlusion sensitivity (OS)

setenv exp_name   'reg'       # experiment name
setenv input_var  'prcp'      # input variable

# # set test dataset (ERA5, IMERG)
foreach o_name  ( 'ERA5_prcp_lat_1979_2021_f01'\
                  'GPCP_v3.2_prcp_lat_2000_2020_f01'\
                  'IMERG_prcp_lat_2000_2021_f01'\
                  'MSWEP_prcp_lat_1979_2021_f01' )

setenv h_dir '/home/jhkim/model/deep_detection'          # Main directory

# test set
setenv test_inp  $input_var'/filter/'${o_name}'.nc'


#===================================================================================

echo 'Experiment: '$exp_name

# Number of ensemble
mkdir -p $h_dir/output/$exp_name/$input_var/src

cd $h_dir/output/$exp_name/$input_var/src
cp -f $h_dir/sample/reg_os7.sample ./run_os7.sample

#===================================================================================
# Run
#===================================================================================
sed "s#h_dir#$h_dir#g"          run_os7.sample > tmp1
sed "s/exp_name/$exp_name/g"              tmp1 > tmp2
sed "s#test_inp#$test_inp#g"              tmp2 > tmp1
sed "s/input_var/$input_var/g"            tmp1 > tmp2
sed "s/ooo/$o_name/g"                     tmp2 > run_os7.py
python run_os7.py



