"""
Plot simulated muon events and compare them to reconstructed ones
Call with 'python'

Usage:
    create_event_files.py --simulation_file=DIR --simulationTruth_path=DIR --output_path=DIR

Options:
    --simulation_file=DIR                          Path to the simulation file
    --simulationTruth_path=DIR                     Path to the file directory
    --output_path=DIR                              Directory of output_files
"""
import numpy as np
import photon_stream as ps
from muons.detection_with_simple_ring_fit import detection_with_simple_ring_fit
import os
import pandas
import docopt


def main(
    simulation_file,
    simulationTruth_path,
    output_path
):
    run = ps.EventListReader(simulation_file)
    ringModel_event_infos = []
    medianR_event_infos = []
    knownC_event_infos = []
    simulationTruth = pandas.read_csv(simulationTruth_path)
    for i, event in enumerate(run):
        photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
        muon_features = detection_with_simple_ring_fit(event, photon_clusters)
        if muon_features["is_muon"]:
            event_id = i
            ringModel_event_info = only_ringModel(i, muon_features)
            ringModel_event_infos.append(ringModel_event_info)
            medianR_event_info = median_r(
                    event_id, muon_features, photon_clusters)
            medianR_event_infos.append(medianR_event_info)
            knownC_event_info = known_center(
                event_id, muon_features, simulationTruth, photon_clusters)
            knownC_event_infos.append(knownC_event_info)
    save_to_file(
        ringModel_event_infos, "ringModel", output_path)
    save_to_file(
        medianR_event_infos, "medianR", output_path)
    save_to_file(
        knownC_event_infos, "knownC", output_path)


def calculate_median(x_loc, y_loc, muon_ring_cx, muon_ring_cy):
    dist_x = x_loc - muon_ring_cx
    dist_y = y_loc - muon_ring_cy
    r_sq = np.square(dist_x) + np.square(dist_y)
    return np.sqrt(np.median(r_sq))


def only_ringModel(event_id, muon_features):
    muon_ring_cx = muon_features['muon_ring_cx']
    muon_ring_cy = muon_features['muon_ring_cy']
    muon_ring_r = muon_features['muon_ring_r']
    ringModel_event_info = [
        event_id,
        muon_ring_cx,
        muon_ring_cy,
        muon_ring_r
    ]
    return ringModel_event_info


def known_center(
    event_id, muon_features,
    simulationTruth, photon_clusters
):
    muon_ring_cx = float(simulationTruth.loc[
        simulationTruth["event_id"] == event_id, "casual_muon_direction0"])
    muon_ring_cy = float(simulationTruth.loc[
        simulationTruth["event_id"] == event_id, "casual_muon_direction1"])
    full_cluster_mask = photon_clusters.labels >= 0
    flat_photon_stream = photon_clusters.point_cloud
    point_cloud = flat_photon_stream[full_cluster_mask]
    x_loc = point_cloud[:, 0]
    y_loc = point_cloud[:, 1]
    r_median = calculate_median(
        x_loc, y_loc, muon_ring_cx, muon_ring_cy)
    knownC_event_info = [
        event_id,
        muon_ring_cx,
        muon_ring_cy,
        r_median
    ]
    return knownC_event_info


def median_r(event_id, muon_features, photon_clusters):
    muon_ring_cx = muon_features['muon_ring_cx']
    muon_ring_cy = muon_features['muon_ring_cy']
    full_cluster_mask = photon_clusters.labels >= 0
    flat_photon_stream = photon_clusters.point_cloud
    point_cloud = flat_photon_stream[full_cluster_mask]
    x_loc = point_cloud[:, 0]
    y_loc = point_cloud[:, 1]
    r_median = calculate_median(
        x_loc, y_loc, muon_ring_cx, muon_ring_cy)
    medianR_event_info = [
        event_id,
        muon_ring_cx,
        muon_ring_cy,
        r_median
    ]
    return medianR_event_info


def save_to_file(event_infos, method_name, output_path):
    header = list([
        "event_id",
        "muon_ring_cx",
        "muon_ring_cy",
        "muon_ring_r",
    ])
    headers = ",".join(header)
    file_name = output_path + str(method_name) + "extracted" + ".csv"
    np.savetxt(
        file_name,
        event_infos,
        delimiter=",",
        comments='',
        header=headers
    )


try:
    arguments = docopt.docopt(__doc__)
    simulation_file = arguments["--simulation_file"]
    simulationTruth_path = arguments['--simulationTruth_path']
    output_path = arguments['--output_path']
    main(simulation_file, simulationTruth_path, output_path)
except docopt.DocoptExit as e:
    print(e)