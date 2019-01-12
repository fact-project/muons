"""
Distribution of muon ring features
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: scoop_real_distributions.py --muon_dir=DIR --output_dir=DIR

Options:
    --muon_dir=DIR      The location of muon data
    --output_dir=DIR    The output of caluculated fuzzyness
"""
import photon_stream as ps
import os
import glob
import matplotlib.pyplot as plt
from muons.detection import detection
import numpy as np
import docopt
import fact


def create_jobs(muon_dir, output_dir):
    jobs = []
    wild_card_path = os.path.join(muon_dir, "*", "*", "*", "*.phs.jsonl.gz")
    for inpath in glob.glob(wild_card_path):
        job = {}
        job["inpath"] = inpath
        job["output_dir"] = output_dir
        jobs.append(job)
    return jobs


def run_job(job):
    results = []
    inpath = job["inpath"]
    output_dir = job["output_dir"]
    run = ps.EventListReader(inpath)
    muon_ring_features = []
    for event in run:
        clusters = ps.PhotonStreamCluster(event.photon_stream)
        muon_props = detection(event, clusters)
        if muon_props["is_muon"]:
            muon_ring_feature = [
                muon_props["muon_ring_cx"],
                muon_props["muon_ring_cy"],
                muon_props["muon_ring_r"]
            ]
            muon_ring_features.append(muon_ring_feature)
    fact_path = fact.path.parse(inpath)
    night = fact_path["night"]
    run = fact_path["run"]
    filename = str(night) + "_" + str(run) + ".csv"
    outpath = os.path.join(output_dir, filename)
    header = list(["cx", "cy", "r"])
    headers = ",".join(header)
    np.savetxt(
        outpath,
        muon_ring_features,
        delimiter=",",
        comments="",
        header=headers
        )
    return muon_ring_features


if __name__=='__main__':
    try:
        arguments = docopt.docopt(__doc__)
        muon_dir = arguments['--muon_dir']
        output_dir = arguments['--output_dir']
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        jobs = create_jobs(muon_dir, output_dir)
        job_return_codes = list(scoop.futures.map(run_job, jobs))
    except docopt.DocoptExit as e:
        print(e)
