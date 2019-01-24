"""
Comparison of PSF and fuzzinessand reeconstruction of muon events runwise
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage:
    scoop_compare_psf_fuzz.py --simulation_dir=DIR --preferencesFile_path=PTH --maximum_PSF=FLT --steps=INT --output_dir=DIR --scoop_hosts=PTH

Options:
    --simulation_dir=DIR          Directory of the simulations
    --preferencesFile_path=PTH      Path to the preferences file needed for psf_fuzz class
    --maximum_PSF=FLT               Maximum PSF needed for the psf_fuzz class
    --steps=INT                     Number of different PSF to be simulated. Needed for psf_fuzz class
    --output_dir=DIR                Output directory needed for psf_fuzz class
    --scoop_hosts=PTH               Path to scoop_hosts
"""
import sys
import os
filePath = os.path.normpath(os.path.abspath(__file__))
parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
scriptDir = os.path.normpath(os.path.join(parentDir, os.pardir))
sys.path.insert(0, scriptDir)
import psf_fuzz_analysis as pfa
import numpy as np
import scoop
import docopt


def main(
    simulation_dir, preferencesFile_path,
    maximum_PSF, steps, output_dir, scoop_hosts
):
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile_path,
        maximum_PSF, steps,
        scoop_hosts,
        output_dir
    )
    jobs = Analysis.find_all_simulation_files()
    runInfos = list(
        scoop.futures.map(Analysis.extract_fuzzParam_from_single_run, jobs))
    reconstructed_muon_eventsHs = []
    responseR_avgs = []
    responseR_stdevs = []
    fuzzR_avgs = []
    fuzzR_stdevs = []
    number_muonsHs = []
    reconstructed_muon_eventsRs = []
    responseH_avgs = []
    responseH_stdevs = []
    fuzzH_avgs = []
    fuzzH_stdevs = []
    number_muonsRs = []
    point_spread_functions = []
    for singleRun in runInfos:
        inpath = singleRun['inpath']
        responseR_avgs.append(singleRun['responseR_avg'])
        responseR_stdevs.append(singleRun['responseR_stdev'])
        fuzzR_avgs.append(singleRun['fuzzR_avg'])
        fuzzR_stdevs.append(singleRun['fuzzR_stdev'])
        number_muonsHs.append(singleRun['number_muonsH'])
        responseH_avgs.append(singleRun['responseH_avg'])
        responseH_stdevs.append(singleRun['responseH_stdev'])
        fuzzH_avgs.append(singleRun['fuzzH_avg'])
        fuzzH_stdevs.append(singleRun['fuzzH_stdev'])
        number_muonsRs.append(singleRun['number_muonsR'])
        point_spread_functions.append(singleRun['point_spread_function'])
        Analysis.save_muon_events(
            singleRun['reconstructed_muon_eventsR'], inpath, "ringM")
        Analysis.save_muon_events(
            singleRun['reconstructed_muon_eventsH'], inpath, "hough")
    Analysis.save_fuzz_info(
        point_spread_functions, "ringM", "response",
        number_muonsRs, responseR_avgs, responseR_stdevs)
    Analysis.save_fuzz_info(
        point_spread_functions, "ringM", "stdev",
        number_muonsRs, fuzzR_avgs, fuzzR_stdevs)
    Analysis.save_fuzz_info(
        point_spread_functions, "hough", "response",
        number_muonsHs, responseH_avgs, responseH_stdevs)
    Analysis.save_fuzz_info(
        point_spread_functions, "hough", "stdev",
        number_muonsHs, fuzzH_avgs, fuzzH_stdevs)



if __name__ == '__main__':
    try:
        arguments = docopt.docopt(__doc__)
        simulation_dir = arguments['--simulation_dir']
        preferencesFile_path = arguments['--preferencesFile_path']
        maximum_PSF = float(arguments['--maximum_PSF'])
        steps = int(arguments['--steps'])
        output_dir = arguments['--output_dir']
        scoop_hosts = arguments['--scoop_hosts']
        main(
            simulation_dir, preferencesFile_path,
            maximum_PSF, steps, output_dir, scoop_hosts
        )
    except docopt.DocoptExit as e:
        print(e)