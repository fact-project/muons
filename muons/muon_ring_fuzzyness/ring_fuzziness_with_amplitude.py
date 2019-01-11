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


def evaluate_ring(
    point_positions,
    cx,
    cy,
    r,
    hough_epsilon=np.deg2rad(0.5*0.1111)
):
    total_amplitude = 0
    point_positions_max = point_positions.shape[0]
    for i_point in range(point_positions_max):
        point_x = point_positions[i_point, 0]
        point_y = point_positions[i_point, 1]
        r_point = calculate_point_distance(
            ring_cx=cx, ring_cy=cy,
            point_x=point_x, point_y=point_y)
        point_contribution = apply_triangular_evaluation(
            ring_radius=r, amplitude=1,
            r_point=r_point, hough_epsilon=hough_epsilon)
        total_amplitude += point_contribution
        normed_amplitude = total_amplitude/point_positions_max
    return normed_amplitude


def calculate_point_distance(
    ring_cx,
    ring_cy,
    point_x,
    point_y
):
    x_pos = point_x - ring_cx
    y_pos = point_y - ring_cy
    r_point = np.sqrt(x_pos**2 + y_pos**2)
    return r_point


def apply_triangular_evaluation(
    r_point,
    hough_epsilon,
    ring_radius,
    amplitude
):
    if (
        r_point > ring_radius-hough_epsilon and
        r_point < ring_radius+hough_epsilon
    ):
        abs_loc = abs(r_point-ring_radius)
        point_contribution = amplitude*(
            hough_epsilon-abs_loc)/(hough_epsilon)
    else:
        point_contribution = 0
    return point_contribution


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
        photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
        cherenkov_cluster_mask = photon_clusters.labels>=0
        cherenkov_point_cloud = photon_clusters.point_cloud
        cherenkov_clusters = cherenkov_point_cloud[cherenkov_cluster_mask]
        point_positions = cherenkov_clusters[:,0:2]
        random_state = np.random.get_state()
        np.random.seed(event.photon_stream.number_photons)
        if not callable(method):
            muon_props = extraction.detection(event, photon_clusters)
        else:
            muon_props = method(event, photon_clusters)
        muon_props = extraction.detection(event, photon_clusters)
        np.random.set_state(random_state)
        if muon_props["is_muon"]:
            cx = muon_props["muon_ring_cx"]
            cy = muon_props["muon_ring_cy"]
            r = muon_props["muon_ring_r"]
            total_amplitude = evaluate_ring(
                point_positions, cx, cy, r)
            results.append(total_amplitude)
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