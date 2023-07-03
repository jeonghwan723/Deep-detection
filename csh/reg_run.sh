#!/bin/csh
# JHK

# function selection
setenv op_train   'off'
setenv op_test    'on'

setenv exp_name   'reg'       # experiment name
setenv input_var  'prcp'      # input variable

# # set test dataset (ERA5, IMERG)
setenv o_name     'ERA5'       # test set

setenv h_dir '/home/jhkim/model/deep_detection'          # Main directory

# training set
setenv tr_inp    'prcp/CESM2_LE_prcp_tr.nc'
setenv tr_lab    'agmt/CESM2_LE_agmt_tr.nc'

# test set
set test_inp = 'prcp/'${o_name}'_prcp.nc'

#===================================================================================

echo 'Experiment: '$exp_name

# Number of ensemble
mkdir -p $h_dir/output/$exp_name/$input_var/src

cd $h_dir/output/$exp_name/$input_var/src
cp -f $h_dir/sample/reg_run.sample ./run.sample

#===================================================================================
# Run
#===================================================================================
if ( $op_train == 'on' | $op_test == 'on') then
sed "s#h_dir#$h_dir#g"                       run.sample > tmp1
sed "s/op_training/$op_train/g"                    tmp1 > tmp2
sed "s/op_testing/$op_test/g"                      tmp2 > tmp1
sed "s/exp_name/$exp_name/g"                       tmp1 > tmp2
sed "s#tr_inp#$tr_inp#g"                           tmp2 > tmp1
sed "s#tr_lab#$tr_lab#g"                           tmp1 > tmp2
sed "s#test_inp#$test_inp#g"                       tmp2 > tmp1
sed "s/input_var/$input_var/g"                     tmp1 > tmp2
sed "s/ooo/$o_name/g"                              tmp2 > run.py
python run.py
endif


