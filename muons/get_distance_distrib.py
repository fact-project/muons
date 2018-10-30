import numpy as np
import photon_stream as ps
from .detection import detection
import os


def extract_muons_from_run(
    input_path,
    output_path
):
    run = ps.EventListReader(input_path)
    event_infos = []
    for i, event in enumerate(run):
        photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
        muon_features = detection(event, photon_clusters)
        if muon_features["is_muon"]:
            event_id = i
            muon_ring_cx = muon_features['muon_ring_cx']
            muon_ring_cy = muon_features['muon_ring_cy']
            muon_ring_r = muon_features['muon_ring_r']
            mean_arrival_time_muon_cluster = muon_features[
                'mean_arrival_time_muon_cluster'
            ]
            muon_ring_overlapp_with_field_of_view = muon_features[
                'muon_ring_overlapp_with_field_of_view'
            ]
            number_of_photons = muon_features['number_of_photons']
            event_info = [
                event_id,
                muon_ring_cx,
                muon_ring_cy,
                muon_ring_r,
                mean_arrival_time_muon_cluster,
                muon_ring_overlapp_with_field_of_view,
                number_of_photons
            ]
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
            event_infos.append(event_info)
    np.savetxt(
        output_path+".temp",
        event_infos,
        delimiter=",",
        header=headers
    )
    os.rename(output_path+".temp", output_path)

