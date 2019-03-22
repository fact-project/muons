"""
Find point spread function for all runs
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: scoop_find_all.py --muon_dir=DIR --output_dir=DIR

Options:
    --muon_dir=DIR      The location of muon data
    --output_dir=DIR    The output of caluculated fuzzyness
"""
import docopt
import scoop
import os
import glob
import fact
from muons.psf_monitoring import single_event_PSF as sep


def run(job):
    sep.calculate_one_run(
        inpath=job["input_path"],
        outpath=job["output_path"]
    )


def create_jobs(muon_dir, output_dir, suffix=".phs.jsonl.gz"):
    jobs = []
    wild_card_path = os.path.join(muon_dir, "*", "*", "*", "*"+suffix)
    for path in glob.glob(wild_card_path):
        job = {}
        job["input_path"] = path
        fact_path = fact.path.parse(path)
        job["output_path"] = fact.path.tree_path(
            night=fact_path["night"],
            run=fact_path["run"],
            suffix=".psf.jsonl",
            prefix=output_dir)
        jobs.append(job)
    return jobs


def main():
    try:
        arguments = docopt.docopt(__doc__)
        muon_dir = arguments['--muon_dir']
        output_dir = arguments['--output_dir']
        jobs = create_jobs(
            muon_dir,
            output_dir,)
        job_return_codes = list(scoop.futures.map(run, jobs))
    except docopt.DocoptExit as e:
        print(e)


if __name__ == "__main__":
    main()