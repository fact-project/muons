#!/usr/bin/python
"""
Comparison of PSF and fuzzinessand reeconstruction of muon events runwise
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: compare_psf_fuzz.py --simulation_dir=DIR --output_dir=DIR

Options:
    --simulation_dir=DIR    Directory of the simulations
    --output_dir=DIR        Directory for the output file
    --extraction=NME        Extraction method to be used. Options: ringM or hough
"""

import docopt
import scoop
from muons.muon_ring_fuzzyness import ring_fuzziness_with_amplitude as mrfa
from muons.muon_ring_fuzzyness import muon_ring_fuzzyness as mrf
from muons.detection import detection as hough
from muons.detection_with_simple_ring_fit import (
    detection_with_simple_ring_fit as ringM)
import os
import photon_stream as ps
import pandas
import glob
import numpy as np
np.warnings.filterwarnings('ignore')


def paths(simulation_dir, extraction, suffix="**/psf*.sim.phs"):
    paths = []
    wild_card_path = os.path.join(simulation_dir, suffix)
    for path in glob.glob(wild_card_path, recursive=True):
        paths.append(path)
    return paths, extraction


def run_fuzz_job(inpath, extraction):
    response_results = []
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
        if extraction == 'ringM':
            muon_props = ringM(event, photon_clusters)
        elif extraction == 'hough':
            muon_props = ringM(event, photon_clusters)
        np.random.set_state(random_state)
        if muon_props["is_muon"]:
            event_id = i
            cx = muon_props["muon_ring_cx"]
            cy = muon_props["muon_ring_cy"]
            r = muon_props["muon_ring_r"]
            reconstructed_muon_event = get_reconstructed_muons_info(
                muon_props, event_id)

            normed_response = mrfa.evaluate_ring(
                point_positions, cx, cy, r)
            response_results.append(normed_response)

            fuzziness = mrf.muon_ring_std_event(
                photon_clusters, muon_props)
            fuzz_results.append(fuzziness)

            number_muons += 1
            mu_event_ids.append(event_id)
            reconstructed_muon_events.append(reconstructed_muon_event)
    save_muon_events(reconstructed_muon_events, inpath)
    average_response = float(np.average(response_results))
    response_std = float(np.std(response_results))
    response_dict = {
        "average_response": average_response,
        "response_std":response_std
    }
    average_fuzz = float(np.average(fuzz_results))
    fuzz_std = float(np.std(fuzz_results))
    fuzz_dict = {
        "average_std": average_fuzz,
        "std_std": fuzz_std
    }
    return response_dict, std_dict, number_muons, mu_event_ids


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


def with_one_PSF(inpath, extraction):
    splitInpath = inpath.split(".")
    fileName_noSuffix = ".".join([splitInpath[0], splitInpath[1]])
    simTruthPath = "".join([fileName_noSuffix, ".simulationtruth.csv"])
    if extraction == 'both':
        response_dictR, std_dictR, detected_muonCountR, mu_event_idsR = (
            run_fuzz_job(inpath, "ringM")
        )
        response_dictH, std_dictH, detected_muonCountH, mu_event_idsH = (
            run_fuzz_job(inpath, "hough")
        )
        try:
            point_spread_function = get_simTruth(simTruthPath, mu_event_ids)
        except IndexError:
            point_spread_function = np.nan
        fuzz_std1R = std_dictR['std_std']
        fuzz_std2R = response_dictR['response_std']
        average_fuzz1R = std_dictR['average_std']
        average_fuzz2R = response_dictR['average_response']
        fuzz_std1H = std_dictH['std_std']
        fuzz_std2H = response_dictH['response_std']
        average_fuzz1H = std_dictH['average_std']
        average_fuzz2H = response_dictH['average_response']
        event_infoR = [
            point_spread_function,
            average_fuzz1R, fuzz_std1R,
            average_fuzz2R, fuzz_std2R,
            detected_muonCount
        ]
        event_infoH = [
            point_spread_function,
            average_fuzz1H, fuzz_std1H,
            average_fuzz2H, fuzz_std2H,
            detected_muonCount
        ]
        event_infos = [event_infoR, event_infoH]
    else:
        response_dict, std_dict, detected_muonCount, mu_event_ids = (
            run_fuzz_job(inpath, extraction)
        )
        try:
            point_spread_function = get_simTruth(simTruthPath, mu_event_ids)
        except IndexError:
            point_spread_function = np.nan
        fuzz_std1 = std_dict['std_std']
        fuzz_std2 = response['response_std']
        average_fuzz1 = std_dict['average_std']
        average_fuzz2 = response['average_response']
        event_info = [
            point_spread_function,
            average_fuzz1, fuzz_std1,
            average_fuzz2, fuzz_std2,
            detected_muonCount
        ]
    return event_info


def save_fuzz_file(arguments):
    simulation_dir = arguments['--simulation_dir']
    output_dir = arguments['--output_dir']
    extraction = arguments['--extraction']
    filename_std = "std_psf.csv"
    filename_response = "response_psf.csv"
    header_list = list([
        "point_spread_function",
        "average_fuzz",
        "fuzz_std",
        "detected_muonCount"
    ])
    headers = ",".join(header_list)
    jobs = paths(simulation_dir, extraction)
    events = list(
        scoop.futures.map(with_one_PSF, jobs))
    if extraction == 'both':
        ringM_events = events[0]
        hough_events = events[1]
        different_events = [ringM_events, hough_events]
        event_types = ["ringM", "hough"]
        for typeName, events in zip(event_types, different_events):
            events = sorted(events)
            events_std = [
                events[0], events[1], events[2], events[5]]
            events_response = [
                events[0], events[3], events[4], events[5]]
            iter_event_list = [events_std, events_response]
            filenames = [filename_std, filename_response]
            for filename, event_info in zip(filenames, iter_event_list):
                file_out = os.path.join(output_dir, typeName, filename)
                np.savetxt(
                    file_out,
                    events,
                    delimiter=",",
                    comments='',
                    header=headers
                    )
    else:
        events = sorted(events)
        events_std = [
            events[0], events[1], events[2], events[5]]
        events_response = [
            events[0], events[3], events[4], events[5]]
        iter_event_list = [events_std, events_response]
        filenames = [filename_std, filename_response]
        for filename, event_info in zip(filenames, iter_event_list):
            file_out = os.path.join(output_dir, filename)
            np.savetxt(
                file_out,
                events,
                delimiter=",",
                comments='',
                header=headers
                )


def main():
    try:
        arguments = docopt.docopt(__doc__)
        save_fuzz_file(arguments)
        filename = "psf_fuzz.csv" #### change in analysis file also
    except docopt.DocoptExit as e:
        print(e)


if __name__ == "__main__":
    main()
