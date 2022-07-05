#!/bin/csh
# JHK

setenv exp_name   'reg'       # experiment name
setenv input_var  'prcp'      # input variable

# # set test dataset (ERA5, IMERG)
setenv o_name     'ERA5'

setenv h_dir '/home/jhkim/task/deep_detection/model'          # Main directory

# test set
set test_inp = $input_var'/'$o_name'_'$input_var'.nc'

#===================================================================================

echo 'Experiment: '$exp_name

# Number of ensemble
mkdir -p $h_dir/output/$exp_name/$input_var/src

cd $h_dir/output/$exp_name/$input_var/src
cp -f $h_dir/sample/reg_occ.sample ./occ.sample

#===================================================================================
# Run
#===================================================================================
sed "s#h_dir#$h_dir#g"          occ.sample > tmp1
sed "s/exp_name/$exp_name/g"          tmp1 > tmp2
sed "s#test_inp#$test_inp#g"          tmp2 > tmp1
sed "s/input_var/$input_var/g"        tmp1 > tmp2
sed "s/ooo/$o_name/g"                 tmp2 > occ.py
python occ.py



