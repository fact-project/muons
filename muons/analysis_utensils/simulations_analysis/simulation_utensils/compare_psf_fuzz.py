#!/usr/bin/python
"""
Comparison of PSF and fuzzinessand reeconstruction of muon events runwise
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: compare_psf_fuzz.py --simulation_dir=DIR --output_dir=DIR

Options:
    --simulation_dir=DIR    Directory of the simulations
    --output_dir=DIR        Directory for the output file
"""

import docopt
import scoop
from muons.muon_ring_fuzzyness import ring_fuzziness_with_amplitude as mrfa
from muons.muon_ring_fuzzyness import muon_ring_fuzzyness as mrf
from muons.detection import detection
import os
import photon_stream as ps
import pandas
import glob
import numpy as np
np.warnings.filterwarnings('ignore')


def paths(simulation_dir, suffix="**/psf*.sim.phs"):
    paths = []
    wild_card_path = os.path.join(simulation_dir, suffix)
    for path in glob.glob(wild_card_path, recursive=True):
        paths.append(path)
    return paths


def run_fuzz_job(inpath):
    amplitude_results = []
    fuzz_results = []
    run = ps.EventListReader(inpath)
    number_muons = 0
    mu_event_ids = []
    reconstructed_muon_events = []
    for i, event in enumerate(run):
        photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
        cherenkov_cluster_mask = photon_clusters.labels>=0
        cherenkov_point_cloud = photon_clusters.point_cloud
        cherenkov_clusters = cherenkov_point_cloud[cherenkov_cluster_mask]
        point_positions = cherenkov_clusters[:,0:2]
        random_state = np.random.get_state()
        np.random.seed(event.photon_stream.number_photons)
        muon_props = detection(event, photon_clusters)
        np.random.set_state(random_state)
        if muon_props["is_muon"]:
            event_id = i
            cx = muon_props["muon_ring_cx"]
            cy = muon_props["muon_ring_cy"]
            r = muon_props["muon_ring_r"]
            reconstructed_muon_event = get_reconstructed_muons_info(
                muon_props, event_id)

            normed_amplitude = mrfa.evaluate_ring(
                point_positions, cx, cy, r)
            amplitude_results.append(normed_amplitude)

            fuzziness = mrf.muon_ring_std_event(
                clusters, muon_props)
            fuzz_results.append(fuzziness)

            number_muons += 1
            mu_event_ids.append(event_id)
            reconstructed_muon_events.append(reconstructed_muon_event)
    save_muon_events(reconstructed_muon_events, inpath)
    average_amplitude = float(np.average(amplitude_results))
    amplitude_std = float(np.std(amplitude_results))
    amplitude_dict = {}
    average_fuzz = float(np.average(fuzz_results))
    fuzz_std = float(np.std(fuzz_results))
    fuzz_dict = {}
    return average_fuzz, std_fuzz, number_muons, mu_event_ids


def save_muon_events(reconstructed_muon_events, inpath):
    directory_path = os.path.dirname(os.path.realpath(inpath))
    output_path = os.path.join(
        directory_path, "reconstructed_muon_events.csv")
    header = list([
        "event_id",
        "muon_ring_cx",
        "muon_ring_cy",
        "muon_ring_r",
        "mean_arrival_time_muon_cluster",
        "muon_ring_overlapp_with_field_of_view",
        "number_of_photons"
    ])
    headers = ",".join(header)
    np.savetxt(
        output_path+".temp",
        reconstructed_muon_events,
        delimiter=",",
        comments='',
        header=headers
    )
    os.rename(output_path+".temp", output_path)


def get_reconstructed_muons_info(muon_props, event_id):
    muon_ring_cx = muon_props['muon_ring_cx']
    muon_ring_cy = muon_props['muon_ring_cy']
    muon_ring_r = muon_props['muon_ring_r']
    mean_arrival_time_muon_cluster = muon_props[
        'mean_arrival_time_muon_cluster'
    ]
    muon_ring_overlapp_with_field_of_view = muon_props[
        'muon_ring_overlapp_with_field_of_view'
    ]
    number_of_photons = muon_props['number_of_photons']
    reconstructed_muon_event = [
        event_id,
        muon_ring_cx,
        muon_ring_cy,
        muon_ring_r,
        mean_arrival_time_muon_cluster,
        muon_ring_overlapp_with_field_of_view,
        number_of_photons
    ]
    return reconstructed_muon_event


def get_simTruth(simTruthPath, mu_event_ids):
    simulation_truth = pandas.read_csv(simTruthPath)
    point_spread_function = simulation_truth["point_spread_function_std"][0]
    return point_spread_function


def with_one_PSF(inpath):
    splitInpath = inpath.split(".")
    fileName_noSuffix = ".".join([splitInpath[0], splitInpath[1]])
    simTruthPath = "".join([fileName_noSuffix, ".simulationtruth.csv"])
    average_fuzz, std_fuzz, detected_muonCount, mu_event_ids = (
        run_fuzz_job(inpath)
    )
    try:
        point_spread_function = get_simTruth(simTruthPath, mu_event_ids)
    except IndexError:
        point_spread_function = np.nan
    event_info = [
        point_spread_function,
        average_fuzz, std_fuzz, detected_muonCount
    ]
    return event_info


def main():
    try:
        arguments = docopt.docopt(__doc__)
        simulation_dir = arguments['--simulation_dir']
        output_dir = arguments['--output_dir']
        filename = "psf_fuzz.csv"
        jobs = paths(simulation_dir)
        events = list(scoop.futures.map(
            with_one_PSF,
            jobs
        )
        )
        header_list = list([
            "point_spread_function",
            "average_fuzz",
            "fuzz_std",
            "detected_muonCount"
        ])
        headers = ",".join(header_list)
        events = sorted(events)
        file_out = os.path.join(output_dir, filename)
        np.savetxt(
            file_out,
            events,
            delimiter=",",
            comments='',
            header=headers
        )
    except docopt.DocoptExit as e:
        print(e)


if __name__ == "__main__":
    main()
