import numpy as np
import photon_stream as ps
from muons.detection_with_simple_ring_fit import (
    detection_with_simple_ring_fit as dwsrf)
from muons.detection import detection
import os
import pandas
import docopt
import sys
filePath = os.path.normpath(os.path.abspath(__file__))
parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
scriptDir = os.path.normpath(os.path.join(parentDir, os.pardir))
sys.path.insert(0, scriptDir)
import plot_single_simulation as pss


class ExtractionMethod_Evaluation:

    """ Evaluate different tested extraction metods: ringM, knownC,
        medianR and hough"""

    def __init__(
        self, simulationFile, simulationTruth_path, output_dir
    ):
        self.simulationFile = simulationFile
        self.simulationTruth_path = simulationTruth_path
        self.output_dir = output_dir
        self.check_for_correct_input()


    def check_for_correct_input(self):
        if not os.path.exists(self.simulationFile):
            raise ValueError(
                "Entered path to simulation file does not exist")
        if ".sim.phs" not in self.simulationFile:
            raise ValueError(
                "Entered path to simulation file is not '.sim.phs' file")
        if "simulationtruth.csv" not in self.simulationTruth_path:
            raise ValueError(
                "Simulationtruth file not ending with 'simulationtruth.csv'")
        if not os.path.exists(self.simulationTruth_path):
            raise ValueError(
                "Entered path to simulationtruth file does not exist")
        if not type(self.output_dir) == str:
            raise ValueError(
                "Entered output_dir path needs to be a string")


    """ ########### Analyse ########### """

    def create_output_dir(self):
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)


    def calculate_median_radius(
        self, x_loc, y_loc, muon_ring_cx, muon_ring_cy
    ):
        dist_x = x_loc - muon_ring_cx
        dist_y = y_loc - muon_ring_cy
        r_sq = np.square(dist_x) + np.square(dist_y)
        return np.sqrt(np.median(r_sq))


    def get_point_cloud(self, photon_clusters):
        full_cluster_mask = photon_clusters.labels >= 0
        flat_photon_stream = photon_clusters.point_cloud
        point_cloud = flat_photon_stream[full_cluster_mask]
        return point_cloud


    def medianR_extraction(
        self,
        muon_features,
        photon_clusters,
        event_id
    ):
        muon_ring_cx = muon_features['muon_ring_cx']
        muon_ring_cy = muon_features['muon_ring_cy']
        point_cloud = self.get_point_cloud(photon_clusters)
        x_loc = point_cloud[:, 0]
        y_loc = point_cloud[:, 1]
        r_median = self.calculate_median_radius(
            x_loc, y_loc, muon_ring_cx, muon_ring_cy)
        medianR_event_info = [
            event_id,
            muon_ring_cx,
            muon_ring_cy,
            r_median
        ]
        return medianR_event_info


    def save_to_file(self, event_infos, method_name):
        header = list([
            "event_id",
            "muon_ring_cx",
            "muon_ring_cy",
            "muon_ring_r",
        ])
        headers = ",".join(header)
        output_path = os.path.join(self.output_dir, "extractionFiles")
        if not os.path.isdir(output_path):
            os.makedirs(output_path)
        fileName = method_name + "_extracted" + ".csv"
        fOut = os.path.join(output_path, fileName)
        np.savetxt(
            fOut,
            event_infos,
            delimiter=",",
            comments='',
            header=headers
        )


    def read_cx_cy_from_simulationTruth(self, eventId):
        simulationTruth = pandas.read_csv(self.simulationTruth_path)
        muon_ring_cx = float(simulationTruth.loc[
            simulationTruth["event_id"] == eventId, "casual_muon_direction0"])
        muon_ring_cy = float(simulationTruth.loc[
            simulationTruth["event_id"] == eventId, "casual_muon_direction1"])
        return muon_ring_cx, muon_ring_cy



    def known_center(
        self, event_id, photon_clusters
    ):
        muon_ring_cx, muon_ring_cy = self.read_cx_cy_from_simulationTruth(
            event_id)
        point_cloud = self.get_point_cloud(photon_clusters)
        x_loc = point_cloud[:, 0]
        y_loc = point_cloud[:, 1]
        r_median = self.calculate_median_radius(
            x_loc, y_loc, muon_ring_cx, muon_ring_cy)
        knownC_event_info = [
            event_id,
            muon_ring_cx,
            muon_ring_cy,
            r_median
        ]
        return knownC_event_info


    def only_ringModel(self, event_id, muon_features):
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


    def extract_with_hough(self, event_id, muon_features):
        muon_ring_cx = muon_features['muon_ring_cx']
        muon_ring_cy = muon_features['muon_ring_cy']
        muon_ring_r = muon_features['muon_ring_r']
        hough_event_info = [
            event_id,
            muon_ring_cx,
            muon_ring_cy,
            muon_ring_r
        ]
        return hough_event_info


    def analysis_main(self):
        run = ps.EventListReader(self.simulationFile)
        ringModel_event_infos = []
        medianR_event_infos = []
        knownC_event_infos = []
        hough_event_infos = []
        for event_id, event in enumerate(run):
            photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
            hough_muonFeatures = detection(event, photon_clusters)
            ringM_muonFeatures = dwsrf(event, photon_clusters)
            if hough_muonFeatures["is_muon"]:
                hough_event_info = self.extract_with_hough(
                    event_id, hough_muonFeatures)
                hough_event_infos.append(hough_event_info)
            if ringM_muonFeatures["is_muon"]:
                ringModel_event_info = self.only_ringModel(
                    event_id, ringM_muonFeatures)
                ringModel_event_infos.append(ringModel_event_info)
                medianR_event_info = self.medianR_extraction(
                        ringM_muonFeatures, photon_clusters, event_id)
                medianR_event_infos.append(medianR_event_info)
                knownC_event_info = self.known_center(
                    event_id, photon_clusters)
                knownC_event_infos.append(knownC_event_info)
        data_to_be_saved = [
            ringModel_event_infos,
            medianR_event_infos,
            knownC_event_infos,
            hough_event_infos
        ]
        methods = ["ringM", "medianR", "knownC", "hough"]
        for method, data in zip(methods, data_to_be_saved):
            self.save_to_file(data, method)


    """ ################## Plotting ################ """

    def do_plotting(self):
        methods = ["ringM", "medianR", "knownC", "hough"]
        for method in methods:
            fileName = method + "_extracted" + ".csv"
            reconstructed_muons_path = os.path.join(
                self.output_dir, "extractionFiles", fileName)
            plot_out = os.path.join(self.output_dir, "Plots", method)
            Plotting = pss.SingleSimulatonPlotting(
                reconstructed_muons_path,
                self.simulationTruth_path, plot_out)
            Plotting.create_all_singleSimulation_plots()


    """ ################# Main call ################ """

    def evaluate_methods(self):
        self.analysis_main()
        self.do_plotting()