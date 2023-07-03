#!/bin/csh
# JHK

# c-shell script for integrated gradient (IG)


# function selection
setenv op_gpu     'on'

setenv exp_name   'dd_v01'       # experiment type

setenv h_dir '/home/jhkim/model/deep_detection'          # Main directory

setenv n_gpu 3                      # GPU number
setenv n_ens 5                      # Ensemble number

# test set
foreach o_name  ( 'ERA5_prcp_lat_1979_2021_f01'\
                  'GPCP_v3.2_prcp_lat_2000_2020_f01'\
                  'IMERG_prcp_lat_2000_2021_f01'\
                  'MSWEP_prcp_lat_1979_2021_f01' )

setenv test_inp  'prcp/filter/'${o_name}'.nc'

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
cp -f $h_dir/sample/dd_v01_ig.sample ./run.sample

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

end


