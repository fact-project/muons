#!/usr/bin/python
"""
Call scoop for simulation muon rings for different point spread functions (PSF)
Call with 'python'

Usage: multiple_openingAngle.py --preferencesFile_path=DIR --steps=INT [--output_dir=DIR]

Options:
    --preferencesFile_path=DIR          Path to the preferences file
    --steps=INT                         Number of steps to be iterated
    --output_dir=DIR                    [default: False] Directory for the simulations
"""
import subprocess
import docopt
import numpy as np
import os
from shutil import copy


def main():
    try:
        arguments = docopt.docopt(__doc__)
        preferencesFile_path = arguments['--preferencesFile_path']
        steps = int(arguments['--steps'])
        scoopDictionary = {}
        with open(preferencesFile_path) as fIn:
            for line in fIn:
                (key, value) = line.split("= ")
                scoopDictionary[key] = value
        output = arguments['--output_dir']
        if output == "False":
            output = scoopDictionary["--output_dir"].strip("\n")
        min_opening_angle = scoopDictionary["--min_opening_angle"].strip("\n")
        max_opening_angle = scoopDictionary["--max_opening_angle"].strip("\n")
        stepsize = (float(max_opening_angle) - float(min_opening_angle))/int(steps)
        if not os.path.isdir(output):
            os.mkdir(output)
        copy(preferencesFile_path, output)
        for i in range(steps+1):
            scoopList = [
                "python", "-m", "scoop", "--hostfile",
                "scoop_hosts.txt", "scoop_simulate_muon_rings.py"
            ]
            current_oa = round(float(min_opening_angle) + np.multiply(stepsize, i), 2)
            dirname = "_".join([
                "opening_angle_",
                str(current_oa)])
            output_dir = os.path.join(output, dirname)
            scoopDictionary["--output_dir"] = output_dir
            scoopDictionary["--min_opening_angle"] = (
                str(current_oa))
            scoopDictionary["--max_opening_angle"] = (
                str(current_oa))
            for key in scoopDictionary:
                scoopList.append(key)
                scoopList.append(scoopDictionary[key].rstrip('\n'))
            subprocess.call(scoopList)
    except docopt.DocoptExit as e:
        print(e)


if __name__ == "__main__":
    main()
