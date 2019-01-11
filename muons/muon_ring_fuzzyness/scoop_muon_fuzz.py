"""
Muon ring fuzziness
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: scoop_muon_fuzz.py --muon_dir=DIR --output_dir=DIR [--suffix=SUF] [--method=NME]

Options:
    --muon_dir=DIR      The location of muon data
    --output_dir=DIR    The output of caluculated fuzzyness
    --suffix=SUF        [default: .phs.jsonl.gz] Format of the input file name
    --method=NME        [default: hough] Method to be used. Options: 'hough' or 'ringM'
"""
import docopt
import scoop
import os
import muons
import photon_stream as ps


def run(job):
    muons.muon_ring_fuzzyness.muon_ring_fuzzyness.run_job(
        inpath=job["input_path"],
        outpath=job["output_path"],
        method=job["method"])


def main():
    try:
        arguments = docopt.docopt(__doc__)
        muon_dir = arguments['--muon_dir']
        output_dir = arguments['--output_dir']
        suffix = arguments['--suffix']
        method = arguments['--method']
        if method == "hough":
            detection = muons.detection
        elif if method == "ringM":
            detection = (
                muons.detection_with_simple_ring_fit.detection_with_simple_ring_fit)
        jobs = muons.muon_ring_fuzzyness.muon_ring_fuzzyness.create_jobs(
            muon_dir,
            output_dir,
            method,
            suffix)
        job_return_codes = list(scoop.futures.map(run, jobs))
    except docopt.DocoptExit as e:
        print(e)


if __name__ == "__main__":
    main()
