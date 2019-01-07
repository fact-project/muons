"""
Muon ring fuzziness
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: scoop_fuzz_amplitude.py --muon_dir=DIR --output_dir=DIR [--suffix=SUF]

Options:
    --muon_dir=DIR      The location of muon data
    --output_dir=DIR    The output of caluculated fuzzyness
    --suffix=SUF        [default: .phs.jsonl.gz] Format of the input file name
"""
import docopt
import scoop
import os
import muons
import photon_stream as ps
import muons.muon_ring_fuzzyness.ring_fuzziness_with_amplitude as rfwa


def run(job):
    rfwa.run_job(inpath=job["input_path"], outpath=job["output_path"])


def main():
    try:
        arguments = docopt.docopt(__doc__)
        muon_dir = arguments['--muon_dir']
        output_dir = arguments['--output_dir']
        suffix = arguments['--suffix']
        jobs = rfwa.create_jobs(
            muon_dir,
            output_dir,
            suffix)
        job_return_codes = list(scoop.futures.map(run, jobs))
    except docopt.DocoptExit as e:
        print(e)


if __name__ == "__main__":
    main()