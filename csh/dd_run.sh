#!/bin/csh
# JHK

# C-shell script for Deep Detection model

# function selection
setenv op_train   'on'   # train on/off
setenv op_test    'on'   # test on/off
setenv op_ensmean 'on'   # ensemble average on/off
setenv op_gpu     'off'  # using GPU on/off

setenv exp_name   'dd_v01'       # experiment name

# set output name (ERA5, IMERG)
set o_name = 'ERA5'

# set main directory
setenv h_dir '/home/jhkim/model/deep_detection'

# set gpu number (for multi-GPU environment, not number of gpu)
setenv n_gpu 0                  

# number of ensemble members
setenv n_ens 5

# set training data set
setenv tr_inp     'prcp/CESM2_LE_prcp_tr.nc'
setenv tr_lab     'agmt/CESM2_LE_agmt_tr.nc'

# set validation data set
setenv val_inp    'prcp/CESM2_LE_prcp_val.nc'
setenv val_lab    'agmt/CESM2_LE_agmt_val.nc'

# set test data set
setenv test_inp  'prcp/ERA5_prcp.nc'

#===================================================================================

echo 'Experiment: '$exp_name

# Number of ensemble
@ ens = 1
while ( $ens <= $n_ens )

echo '  Ensemble: '$ens'/'$n_ens

mkdir -p $h_dir/output/$exp_name/src
mkdir -p $h_dir/output/$exp_name/EN$ens

cd $h_dir/output/$exp_name/src
cp -f $h_dir/sample/dd_run.sample ./run.sample
cp -f $h_dir/sample/dd_ensmean.sample ./ensmean.sample

#===================================================================================
# Run
#===================================================================================
if ( $op_train == 'on' | $op_test == 'on' ) then
sed "s#h_dir#$h_dir#g"                       run.sample > tmp1
sed "s/exp_name/$exp_name/g"                       tmp1 > tmp2
sed "s/ensemble/$ens/g"                            tmp2 > tmp1
sed "s/op_training/$op_train/g"                    tmp1 > tmp2
sed "s/op_testing/$op_test/g"                      tmp2 > tmp1
sed "s#tr_inp#$tr_inp#g"                           tmp1 > tmp2
sed "s#tr_lab#$tr_lab#g"                           tmp2 > tmp1
sed "s#val_inp#$val_inp#g"                         tmp1 > tmp2
sed "s#val_lab#$val_lab#g"                         tmp2 > tmp1
sed "s#test_inp#$test_inp#g"                       tmp1 > tmp2
sed "s/option_gpu/$op_gpu/g"                       tmp2 > tmp1
sed "s/o_name/$o_name/g"                           tmp1 > tmp2
sed "s/gpu_number/$n_gpu/g"                        tmp2 > run.py
python run.py
endif

@ ens = $ens + 1
end

#===================================================================================
# combination mean
#===================================================================================
if ( $op_ensmean == 'on' ) then
sed "s#h_dir#$h_dir#g"         ensmean.sample > tmp1
sed "s/exp_name/$exp_name/g"             tmp1 > tmp2
sed "s/o_name/$o_name/g"                 tmp2 > tmp1
sed "s/n_ens/$n_ens/g"                   tmp1 > ensmean.py
python ensmean.py
endif
