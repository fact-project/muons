#!/bin/bash

python ./multiple_PSF.py --preferencesFile_path ./preferences_file.csv \
    --maximum_PSF 0.25 --steps 20
echo "Simulations with different point spread functions has finished!"
simulation_directory=$(grep --only-matching \
    --perl-regex "(?<=--output_dir\=).*" ./preferences_file.csv)
python -m scoop --hostfile scoop_hosts.txt ./compare_psf_fuzz.py \
    --simulation_dir $simulation_directory --output_dir $simulation_directory \
    --filename psf_fuzz.csv
