#!/bin/csh
# JHK
# C-shell script for 7x7 occlusion sensitivity (OS)

# function selection
setenv op_gpu     'off'

# set experiment name
setenv exp_name   'dd_v01'       

# set output name
set o_name = 'ERA5'

# set main directory
setenv h_dir '/home/jhkim/model/deep_detection'

# set gpu number (for multi-GPU environment)
setenv n_gpu 0

# number of ensemble members
setenv n_ens 5                    

# test data set
foreach o_name  ( 'ERA5_prcp_lat_1979_2021_f01'\
                  'GPCP_v3.2_prcp_lat_2000_2020_f01'\
                  'IMERG_prcp_lat_2000_2021_f01'\
                  'MSWEP_prcp_lat_1979_2021_f01' )

setenv test_inp  'prcp/filter/'${o_name}'.nc'

#===================================================================================

echo 'Experiment: '$exp_name

# Number of ensemble
@ ens = 1
while ( $ens <= $n_ens )

echo '  Ensemble: '$ens'/'$n_ens

mkdir -p $h_dir/output/$exp_name/src
mkdir -p $h_dir/output/$exp_name/EN$ens

cd $h_dir/output/$exp_name/src
cp -f $h_dir/sample/dd_os7.sample ./run_os7.sample

#===================================================================================
# Run
#===================================================================================
sed "s#h_dir#$h_dir#g"                   run_os7.sample > tmp1
sed "s/exp_name/$exp_name/g"                       tmp1 > tmp2
sed "s/ensemble/$ens/g"                            tmp2 > tmp1
sed "s#test_inp#$test_inp#g"                       tmp1 > tmp2
sed "s/option_gpu/$op_gpu/g"                       tmp2 > tmp1
sed "s/o_name/$o_name/g"                           tmp1 > tmp2
sed "s/gpu_number/$n_gpu/g"                        tmp2 > run_os7.py
python run_os7.py

@ ens = $ens + 1
end

end

