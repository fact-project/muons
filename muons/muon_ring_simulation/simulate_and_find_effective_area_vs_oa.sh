#!/bin/bash

python ./multiple_openingAngle.py --preferencesFile_path ./preferences_file.csv \
    --steps 10
echo "Simulations with different point spread functions has finished!"
simulation_directory=$(grep --only-matching \
    --perl-regex "(?<=--output_dir\=).*" ./preferences_file.csv)
number_of_muons=$(grep --only-matching \
    --perl-regex "(?<=--number_of_muons\=).*" ./preferences_file.csv)
python -m scoop --hostfile scoop_hosts.txt ./compare_opening_angle.py \
    --simulation_dir $simulation_directory --output_dir $simulation_directory \
    --number_of_muons $number_of_muons
