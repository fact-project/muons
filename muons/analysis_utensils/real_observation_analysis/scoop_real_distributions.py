"""
Distribution of muon ring features
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: scoop_real_distributions.py --muon_dir=DIR --output_dir=DIR --epochFile=PTH --scoop_hosts=PTH --fitDir=DIR

Options:
    --muon_dir=DIR               The location of muon data
    --output_dir=DIR             The output of caluculated fuzzyness
    --epochFile=PTH              Path to the epoch file
    --scoop_hosts=PTH            Path to scoop_hosts.txt
    --fitDir=DIR                 Directory for function fits.
"""
import photon_stream as ps
import os
import docopt
import sys
filePath = os.path.normpath(os.path.abspath(__file__))
fileDir = os.path.normpath(os.path.join(filePath, os.pardir))
parentDir = os.path.normpath(os.path.join(
    fileDir, os.pardir))
scriptDir = os.path.join(parentDir, "real_observation_analysis")
sys.path.insert(0, scriptDir)
import real_observation_analysis as roa
import scoop


def main(
    muon_dir, output_dir,
    scoop_hosts, epochFile,
    fitDir
):
    Analysis = roa.RealObservationAnalysis(
        muon_dir, output_dir, epochFile,
        scoop_hosts, fitDir
    )
    jobs = Analysis.create_jobs()
    job_return_codes = list(scoop.futures.map(Analysis.run_job, jobs))


if __name__=='__main__':
    try:
        arguments = docopt.docopt(__doc__)
        muon_dir = arguments['--muon_dir']
        output_dir = arguments['--output_dir']
        scoop_hosts = arguments['--scoop_hosts']
        epochFile = arguments['--epochFile']
        fitDir = arguments['--fitDir']
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        main(
            muon_dir, output_dir, scoop_hosts,
            epochFile, fitDir
        )
    except docopt.DocoptExit as e:
        print(e)