#!/usr/bin/python
"""
Call scoop for simulation muon rings for different point spread functions (PSF)
Call with 'python'

Usage: multiple_PSF.py --preferencesFile_path=DIR --maximum_PSF=FLT --steps=INT --scoop_hostFile=PTH [--output_dir=DIR]

Options:
    --preferencesFile_path=DIR          Path to the preferences file
    --amount_of_different_PSF=INT       Number of different PSF to be simulated
    --maximum_PSF=FLT                   Maximum PSF value to be simulated
    --steps=INT                         Number of steps to be iterated
    --scoop_hostFile=PTH                Path to scoop_hosts.txt
    --output_dir=DIR                    [default: False] Output directory for simulations
"""
import subprocess
import docopt
import numpy as np
import os
from shutil import copy
from muons.muon_ring_simulation import many_simulations as ms


def main():
    try:
        arguments = docopt.docopt(__doc__)
        preferencesFile_path = arguments['--preferencesFile_path']
        steps = int(arguments['--steps'])
        maximum_PSF = np.deg2rad(
            float(arguments['--maximum_PSF'])
        )
        output = arguments['--output_dir']
        scoop_hostFile = arguments['--scoop_hostFile']
        stepsize = maximum_PSF/steps
        if output == "False":
            output = scoopDictionary["--output_dir"].strip("\n")
    except docopt.DocoptExit as e:
        print(e)
    scoopDictionary = {}
    with open(preferencesFile_path) as fIn:
        for line in fIn:
            (key, value) = line.split("= ")
            scoopDictionary[key] = value
    psf = float(scoopDictionary["--point_spread_function"].strip("\n"))
    if not os.path.isdir(output):
        os.makedirs(output)
    copy(preferencesFile_path, output)
    filePath = os.path.normpath(os.path.abspath(ms.__file__))
    parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
    scoop_script_path = os.path.join(parentDir, "scoop_simulate_muon_rings.py")
    for i in range(steps+1):
        scoopList = [
            "python", "-m", "scoop", "--hostfile",
            scoop_hostFile, scoop_script_path
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
