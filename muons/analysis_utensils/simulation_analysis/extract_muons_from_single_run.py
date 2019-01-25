import numpy as np
import photon_stream as ps
from muons.detection import detection
import sys
import os
import shutil
import glob
filePath = os.path.normpath(os.path.abspath(__file__))
parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
scriptDir = os.path.normpath(os.path.join(parentDir, os.pardir))
sys.path.insert(0, scriptDir)
import plot_single_simulation as pss
import matplotlib
matplotlib.use('Agg')



class SingleRunAnalysis:

    """ Analyse single run using currently best detection and extraction methods """

    def __init__(self, simulationFile, simulationTruth, output_dir):
        self.simulationFile = simulationFile
        self.simulationTruth = simulationTruth
        self.output_dir = output_dir
        self.plotting_dir = os.path.join(output_dir, "Plots")
        self.check_inputValidity()
        self.create_output_dir()
        self.extracted_muons = os.path.join(
            self.output_dir, "extracted_muons.csv")


    def check_inputValidity(self):
        if not os.path.exists(self.simulationFile):
            raise ValueError(
                "Simulation file (.phs) needs to exist")
        if not os.path.exists(self.simulationTruth):
            raise ValueError(
                "Simulation truth (.simulationtruth.csv) file needs to exist")
        if not type(self.output_dir) == str:
            raise ValueError(
                "Output directory needs to be given as a string")


    def create_output_dir(self):
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)


    """ ################ Amalysis ################## """


    def extract_muons_from_run(self):
        run = ps.EventListReader(self.simulationFile)
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
            self.extracted_muons,
            event_infos,
            delimiter=",",
            comments='',
            header=headers
        )


    """ ############## Plotting ################### """

    def do_plotting(self):
        Plotting = pss.SingleSimulatonPlotting(
            self.extracted_muons, self.simulationTruth, self.plotting_dir)
        Plotting.create_all_singleSimulation_plots()


    """ ############## Main ##################### """

    def analysis_main(self):
        self.extract_muons_from_run()
        self.do_plotting()
