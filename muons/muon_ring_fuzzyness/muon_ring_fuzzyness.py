import photon_stream as ps
import numpy as np
import os
import json
from pathlib import Path
import glob
import fact
from .. import extraction
import warnings
import muons
warnings.filterwarnings("ignore")


def standard_deviation(point_cloud, muon_props):
    x_loc = point_cloud[:, 0]
    y_loc = point_cloud[:, 1]
    difference = [x_loc - muon_props["muon_ring_cx"],
                  y_loc - muon_props["muon_ring_cy"]]
    deviation_from_fit = (np.sqrt(np.square(difference[0])
                          + np.square(difference[1]))
                          - muon_props["muon_ring_r"])
    real_std = np.std(deviation_from_fit)
    return real_std


def muon_ring_std_event(clusters, muon_props):
    full_cluster_mask = clusters.labels >= 0
    number_of_photons = full_cluster_mask.sum()
    flat_photon_stream = clusters.point_cloud
    point_cloud = flat_photon_stream[full_cluster_mask]
    real_std = standard_deviation(point_cloud, muon_props)
    return real_std


def create_jobs(muon_dir, output_dir, method, suffix=".phs.jsonl.gz"):
    jobs = []
    wild_card_path = os.path.join(muon_dir, "*", "*", "*", "*"+suffix)
    for path in glob.glob(wild_card_path):
        job = {}
        job["input_path"] = path
        fact_path = fact.path.parse(path)
        job["output_path"] = fact.path.tree_path(
            night=fact_path["night"],
            run=fact_path["run"],
            suffix=".muon.fuzz.jsonl",
            prefix=output_dir)
        job["method"] = method
        jobs.append(job)
    return jobs


def run_job(inpath, outpath, method=False):
    results = []
    run = ps.EventListReader(inpath)
    number_muons = 0
    for event in run:
        clusters = ps.PhotonStreamCluster(event.photon_stream)
        random_state = np.random.get_state()
        np.random.seed(event.photon_stream.number_photons)
        if not callable(method):
            muon_props = extraction.detection(event, clusters)
        else:
            muon_props = method(event, clusters)
        np.random.set_state(random_state)
        if muon_props["is_muon"]:
            std_photons_on_ring = muon_ring_std_event(clusters, muon_props)
            results.append(std_photons_on_ring)
            number_muons += 1
    outdir = os.path.dirname(outpath)
    os.makedirs(outdir, exist_ok=True)
    with open(outpath + ".temp", "wt") as fout:
        out = {
            "average_fuzz": float(np.average(results)),
            "std_fuzz": float(np.std(results)),
            "number_muons": number_muons,
        }
        fout.write(json.dumps(out))
    os.rename(outpath + ".temp", outpath)
