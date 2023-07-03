#!/bin/csh
# JHK
# C-shell script for Shapley Additive exPlanations (SHAP) with Gradient explainer

# function selection
setenv op_gpu     'on'

setenv exp_name   'dd_v01'       # experiment type

setenv h_dir '/home/jhkim/model/deep_detection'          # Main directory

setenv n_gpu 0                      # GPU number
setenv n_ens 5                      # Ensemble number

# training set
setenv tr_inp     'prcp/CESM2_LE_prcp_lat_tr.nc'

@ itr = 1
while( $itr <= 10)

# test set
foreach o_name  ( 'MSWEP_prcp_lat_1979_2021_f01' )

setenv test_inp  'prcp/filter/'${o_name}'.nc'
setenv o_name2 'gshap_'${o_name}'_'${itr}

#===================================================================================
echo 'Experiment: '$exp_name
echo 'Input: '${o_name}

# Number of ensemble
@ ens = 1
while ( $ens <= $n_ens )

echo '  Ensemble: '$ens'/'$n_ens

mkdir -p $h_dir/output/$exp_name/src
mkdir -p $h_dir/output/$exp_name/EN$ens

cd $h_dir/output/$exp_name/src
cp -f $h_dir/sample/dd_gshap.sample ./gshap_run.sample

#===================================================================================
# Run
#===================================================================================
sed "s#h_dir#$h_dir#g"                 gshap_run.sample > tmp1
sed "s/exp_name/$exp_name/g"                       tmp1 > tmp2
sed "s/ensemble/$ens/g"                            tmp2 > tmp1
sed "s#tr_inp#$tr_inp#g"                           tmp1 > tmp2
sed "s#test_inp#$test_inp#g"                       tmp2 > tmp1
sed "s/option_gpu/$op_gpu/g"                       tmp1 > tmp2
sed "s/o_name/$o_name2/g"                          tmp2 > tmp1
sed "s/gpu_number/$n_gpu/g"                        tmp1 > gshap_run.py
python gshap_run.py

@ ens = $ens + 1
end

end

@ itr = $itr + 1
end
