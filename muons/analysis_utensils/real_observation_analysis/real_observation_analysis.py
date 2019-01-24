import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import glob
import json
import fact
import time
from datetime import datetime
import csv
from muons.muon_ring_fuzzyness import muon_ring_fuzzyness as mrf
import subprocess


class RealObservationAnalysis:

    """ Performs the analysis of real observations 
        using all here established tools"""


    def __init__(self, observationsDir, output_dir):
        self.observationsDir = observationsDir
        self.output_dir = output_dir




    def get_reconstructed_muons_info(self, muon_props, event_id):
        muon_ring_cx = muon_props['muon_ring_cx']
        muon_ring_cy = muon_props['muon_ring_cy']
        muon_ring_r = muon_props['muon_ring_r']
        mean_arrival_time_muon_cluster = muon_props[
            'mean_arrival_time_muon_cluster'
        ]
        muon_ring_overlap_with_field_of_view = muon_props[
            'muon_ring_overlapp_with_field_of_view'
        ]
        number_of_photons = muon_props['number_of_photons']
        reconstructed_muon_event = [
            event_id,
            muon_ring_cx,
            muon_ring_cy,
            muon_ring_r,
            mean_arrival_time_muon_cluster,
            muon_ring_overlap_with_field_of_view,
            number_of_photons
        ]
        return reconstructed_muon_event


    def get_fuzziness_parameters(self, photon_clusters, muon_props):
        cx = muon_props['muon_ring_cx']
        cy = muon_props['muon_ring_cy']
        r = muon_props['muon_ring_r']
        cherenkov_cluster_mask = photon_clusters.labels>=0
        cherenkov_point_cloud = photon_clusters.point_cloud
        cherenkov_clusters = cherenkov_point_cloud[cherenkov_cluster_mask]
        point_positions = cherenkov_clusters[:,0:2]
        normed_response = mrfa.evaluate_ring(
            point_positions, cx, cy, r)
        fuzziness_stdParam = mrf.muon_ring_std_event(
            photon_clusters, muon_props)
        return normed_response, fuzziness_stdParam