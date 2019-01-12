#!/usr/bin/python
"""
Call scoop for simulation muon rings for different point spread functions (PSF)
Call with 'python'

Usage: multiple_PSF.py --preferencesFile_path=DIR --maximum_PSF=FLT --steps=INT

Options:
    --preferencesFile_path=DIR          Path to the preferences file
    --amount_of_different_PSF=INT       Number of different PSF to be simulated
    --maximum_PSF=FLT                   Maximum PSF value to be simulated
    --steps=INT                         Number of steps to be iterated
"""
import subprocess
import docopt
import numpy as np
import os
from shutil import copy


def main():
    try:
        arguments = docopt.docopt(__doc__)
    except docopt.DocoptExit as e:
        print(e)
    preferencesFile_path = arguments['--preferencesFile_path']
    steps = int(arguments['--steps'])
    maximum_PSF = np.deg2rad(
        float(arguments['--maximum_PSF'])
    )
    stepsize = maximum_PSF/steps
    scoopDictionary = {}
    with open(preferencesFile_path) as fIn:
        for line in fIn:
            (key, value) = line.split("= ")
            scoopDictionary[key] = value
    psf = float(scoopDictionary["--point_spread_function"].strip("\n"))
    output = scoopDictionary["--output_dir"].strip("\n")
    if not os.path.isdir(output):
        os.mkdir(output)
    copy(preferencesFile_path, output)
    for i in range(steps+1):
        scoopList = [
            "python", "-m", "scoop", "--hostfile",
            "scoop_hosts.txt", "scoop_simulate_muon_rings.py"
        ]
        dirname = "_".join(["iterStep", str(i)])
        output_dir = os.path.join(output, dirname)
        scoopDictionary["--output_dir"] = output_dir
        scoopDictionary["--point_spread_function"] = (
            str((np.multiply(stepsize, i))))
        for key in scoopDictionary:
            scoopList.append(key)
            scoopList.append(scoopDictionary[key].rstrip('\n'))
        subprocess.call(scoopList)


if __name__ == "__main__":
    main()
