"""
Distribution of muon ring features
Call with 'python'

Usage: simulation_analysis_main.py --output_dir=DIR --scoop_hosts=PTH --preferencesFile=PTH --steps=INT --maximum_PSF=FLT

Options:
    --output_dir=DIR           The output of caluculated fuzzyness
    --scoop_hosts=PTH          Path to scoop_hosts
    --preferencesFile=PTH      Path to preferences file
    --steps=INT                Number of steps
    --maximum_PSF=FLT          Maximum PSF to be simulated
"""

import sys
import os
filePath = os.path.normpath(os.path.abspath(__file__))
fileDir = os.path.normpath(os.path.join(filePath, os.pardir))
import docopt
import acceptance_vs_openingAngle as eav
import extractionMethod_evaluation as eme
import psf_fuzz_analysis as pfa
import evaluate_detectionMethod as edM


def main(output_dir, scoop_hosts, preferencesFile, steps, maximum_PSF):
    oa_outDir = os.path.join(output_dir, "acceptance_vs_openingAngle")
    if not os.path.isdir(oa_outDir):
        os.makedirs(oa_outDir)
    fuzz_outDir = os.path.join(output_dir, "psf_fuzz_analysis")
    if not os.path.isdir(fuzz_outDir):
        os.makedirs(fuzz_outDir)
    extMethod_dir = os.path.join(output_dir, "extractionMethod_evaluation")
    if not os.path.isdir(extMethod_dir):
        os.makedirs(extMethod_dir)
    detectionMethod_dir = os.path.join(output_dir, "detectionMethod_evaluation")
    if not os.path.isdir(detectionMethod_dir):
        os.makedirs(detectionMethod_dir)
    simulationFileDir = os.path.join(fuzz_outDir, "simulations", "iterStep_0")
    simulationTruth_path = os.path.join(
        simulationFileDir, "psf_0.0.simulationtruth.csv")
    simulationFile = os.path.join(simulationFileDir, "psf_0.0.sim.phs")
    oa = eav.Acceptance_vs_OpeningAngle(
        scoop_hosts, preferencesFile, steps, oa_outDir)
    oa.investigate_acceptance_vs_openingAngle()
    fuzz = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF,
        steps, scoop_hosts, fuzz_outDir)
    fuzz.call_all()
    extraction = eme.ExtractionMethod_Evaluation(
        simulationFile, simulationTruth_path, extMethod_dir)
    extraction.evaluate_methods()
    detection = edM.DetectionMethodEvaluation(
        detectionMethod_dir, 1000, 10, 1.15, scoop_hosts)
    detection.multiple_nsb_rates()



if __name__=='__main__':
    try:
        arguments = docopt.docopt(__doc__)
        steps = int(arguments['--steps'])
        output_dir = arguments['--output_dir']
        scoop_hosts = arguments['--scoop_hosts']
        preferencesFile = arguments['--preferencesFile']
        maximum_PSF = float(arguments['--maximum_PSF'])
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        main(output_dir, scoop_hosts, preferencesFile, steps, maximum_PSF)
    except docopt.DocoptExit as e:
        print(e)