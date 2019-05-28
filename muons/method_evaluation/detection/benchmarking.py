import photon_stream as ps
import numpy as np
import muons
import glob
import os
import re


def true_false_decisions(
    all_photons_run,
    pure_cherenkov_run_photons,
    nsb_run_found_photons
):
    precisions = []
    sensitivities = []
    for muon in range(len(all_photons_run)):
        true_positives = 0
        nsb_run_photons = len(nsb_run_found_photons[muon])
        pure_run_photons = len(pure_cherenkov_run_photons[muon])
        all_photons = len(all_photons_run[muon])
        for nsb_photon in nsb_run_found_photons[muon]:
            for pure_photon in pure_cherenkov_run_photons[muon]:
                if np.isclose(nsb_photon,pure_photon, rtol=0,atol=1e-7).all():
                    true_positives += 1
                    break
        if true_positives > pure_run_photons:
            true_positives = pure_run_photons
        false_positives = nsb_run_photons - true_positives
        false_negatives = pure_run_photons - true_positives
        true_negatives = (
            all_photons - true_positives
            - false_positives - false_negatives)
        try:
            precision = true_positives / (
                true_positives + false_positives)
            sensitivity = true_positives / (
                true_positives + false_negatives)
        except ZeroDivisionError:
            sensitivity = 0
            precision = 0
        precisions.append(precision)
        sensitivities.append(sensitivity)
    mask = np.array(precisions) != 0
    number_muons = mask.sum()
    precisions = np.array(precisions)[mask]
    sensitivities = np.array(sensitivities)[mask]
    std_precision = np.multiply(np.std(precisions), 100)
    std_sensitivity = np.multiply(np.std(sensitivities), 100)
    event = {
        "number_muons": number_muons,
        "avg_precision": np.multiply(np.average(precisions), 100),
        "std_precision": std_precision,
        "precision_SE": np.divide(std_precision, np.sqrt(number_muons)),
        "avg_sensitivity": np.multiply(np.average(sensitivities), 100),
        "std_sensitivity": std_sensitivity,
        "sensitivity_SE": np.divide(std_sensitivity, np.sqrt(number_muons))

    }
    return event


def cluster_single_run(dir_name, clustering=ps.PhotonStreamCluster):
    nsb_run_photons = []
    pure_run_photons = []
    all_run_photons = []
    pure_run_path = os.path.join(dir_name, "pure", "psf_0.sim.phs")
    nsb_run_path = os.path.join(dir_name, "NSB", "psf_0.sim.phs")
    nsb_run = ps.EventListReader(nsb_run_path)
    pure_run = ps.EventListReader(pure_run_path)
    for event in nsb_run:
        photon_clusters = clustering(event.photon_stream)
        cherenkov_cluster_mask = photon_clusters.labels >= 0
        nsb_cherenkov_photon_stream = photon_clusters.point_cloud
        nsb_cherenkov_ps = nsb_cherenkov_photon_stream[
            cherenkov_cluster_mask]
        nsb_run_photons.append(nsb_cherenkov_ps[:, 0:3])
        all_photons = event.photon_stream.point_cloud
        all_run_photons.append(all_photons)
    for muon in pure_run:
        pure_photon_stream = muon.photon_stream.point_cloud
        pure_run_photons.append(pure_photon_stream)
    return (
        all_run_photons,
        pure_run_photons,
        nsb_run_photons
        )


def single_run_analysis(dir_name, clustering=ps.PhotonStreamCluster):
    photons = cluster_single_run(dir_name, clustering=ps.PhotonStreamCluster)
    nsb_info = true_false_decisions(
        photons[0], photons[1], photons[2])
    nsb_rate = re.split("/", dir_name)[-1]
    nsb_info["nsb_rate"] = nsb_rate
    return nsb_info


def different_nsb_rates(resource_path):
    nsb_infos = {
        "number_muons": [],
        "avg_precision": [],
        "std_precision": [],
        "precision_SE": [],
        "avg_sensitivity": [],
        "std_sensitivity": [],
        "sensitivity_SE": [],
        "nsb_rate": []
    }
    wild_card_path = os.path.join(resource_path, "*")
    for path in glob.glob(wild_card_path):
        nsb_info = single_run_analysis(path, clustering=ps.PhotonStreamCluster)
        for key, value in nsb_info.items():
            nsb_infos[key].append(value)
    return nsb_infos

