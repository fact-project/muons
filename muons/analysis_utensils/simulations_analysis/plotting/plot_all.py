"""
Do all plotting
Call with 'python'

Usage:
    plot_all.py --simulation_dir=DIR

Options:
    --simulation_dir=DIR      Directory to the simulations
"""

import subprocess
import docopt
import os
import glob


def create_jobs(simulation_dir, suffix="**/psf*.sim.phs"):
    paths = []
    wild_card_path = os.path.join(simulation_dir, suffix)
    for path in glob.glob(wild_card_path, recursive=True):
        paths.append(path)
    return paths


def main():
    try:
        arguments = docopt.docopt(__doc__)
        simulation_dir = arguments["--simulation_dir"]
        paths = create_jobs(simulation_dir)
    except docopt.DocoptExit as e:
        print(e)
    for path in paths:
        directoryNames = path.split("/")
        iterstep_dirName = directoryNames[-3]
        pathDirectory = os.path.dirname(os.path.realpath(path))
        simulation_ParentDir = os.path.normpath(
            os.path.join(pathDirectory, os.pardir))
        plotting_dir = os.path.join(
            simulation_ParentDir, "Plots", iterstep_dirName)
        splitInpath = path.split(".")
        fileName_noSuffix = ".".join([splitInpath[0], splitInpath[1]])
        simTruthPath = "".join([fileName_noSuffix, ".simulationtruth.csv"])
        extracted_muons_path = os.path.join(
            pathDirectory, "reconstructed_muon_events.csv")
        filePath = os.path.normpath(os.path.abspath(__file__))
        parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
        plot_simulation_scriptName = os.path.join(
            parentDir, "plot_simulation.py")
        plot_simulation_call = [
            "python", plot_simulation_scriptName, "--extracted_muons_path",
            extracted_muons_path, "--simTruthPath", simTruthPath,
            "--plot_dir", plotting_dir
        ]
        subprocess.call(plot_simulation_call)
    psf_fuzz_csv_path = os.path.join(simulation_dir, "psf_fuzz.csv")
    preferences_filePath = os.path.join(simulation_dir,"preferences_file.csv")
    filePath = os.path.normpath(os.path.abspath(__file__))
    parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
    psf_fuzz_scriptPath = os.path.join(parentDir, "plot_psf_fuzz.py")
    plot_psf_fuzz_call = [
        "python", psf_fuzz_scriptPath, "--psf_fuzz_csv_path",
        psf_fuzz_csv_path, "--plot_dir", simulation_dir,
        "--preferences_filePath", preferences_filePath
    ]
    subprocess.call(plot_psf_fuzz_call)


if __name__ == '__main__':
    main()
