#!/bin/csh
# JHK
# C-shell script for generate occlusion sensitivity

# function selection
setenv op_gpu     'off'

# set experiment name
setenv exp_name   'cnn'       

# set output name(ERA5, IMERG)
set o_name = 'ERA5'

# set main directory
setenv h_dir '/home/jhkim/task/deep_detection/model' 

# set gpu number (for multi-GPU environment)
setenv n_gpu 0

# number of ensemble members
setenv n_ens 5                    

# test data set
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
cp -f $h_dir/sample/cnn_occ.sample ./run.sample
cp -f $h_dir/sample/cnn_ensmean_occlusion.sample ./ensmean.sample

#===================================================================================
# Run
#===================================================================================
sed "s#h_dir#$h_dir#g"                       run.sample > tmp1
sed "s/exp_name/$exp_name/g"                       tmp1 > tmp2
sed "s/ensemble/$ens/g"                            tmp2 > tmp1
sed "s#test_inp#$test_inp#g"                       tmp1 > tmp2
sed "s/option_gpu/$op_gpu/g"                       tmp2 > tmp1
sed "s/o_name/$o_name/g"                           tmp1 > tmp2
sed "s/gpu_number/$n_gpu/g"                        tmp2 > run.py
python run.py

@ ens = $ens + 1
end

#===================================================================================
# combination mean
#===================================================================================
sed "s#h_dir#$h_dir#g"         ensmean.sample > tmp1
sed "s/exp_name/$exp_name/g"             tmp1 > tmp2
sed "s/o_name/$o_name/g"                 tmp2 > tmp1
sed "s/n_ens/$n_ens/g"                   tmp1 > ensmean.py
endif


