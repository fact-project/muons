import pandas
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import docopt
import os
import sys
import csv



class SingleSimulatonPlotting:

    """ Produce all plots for single simulation """

    def __init__(
        self, reconstructed_muons_path, simulationTruth_path, plot_out
    ):
        self.reconstructed_muons_path = reconstructed_muons_path
        self.simulationTruth_path = simulationTruth_path
        self.plot_out = plot_out
        self.check_inputValidity()
        self.simulation_truth, self.extracted_muons = self.read_dataframes()
        self.create_outputDir()
        self.muevents = self.choose_muon_events()


    def check_inputValidity(self):
        if not os.path.exists(self.reconstructed_muons_path):
            raise ValueError(
                "Invalid path for reconstructed muons")
        if not os.path.exists(self.simulationTruth_path):
            raise ValueError(
                "Invalid path for the simulationTruth_path")
        if not type(self.plot_out) == str:
            raise ValueError(
                "Plot out directory needs to be a string")


    """ ############### Plotting tools ################### """

    def create_outputDir(self):
        if not os.path.isdir(self.plot_out):
            os.makedirs(self.plot_out)


    def create_bins(self, input_data):
        bin_edges = np.histogram_bin_edges(input_data, bins='sqrt')
        return bin_edges


    def read_dataframes(self):
        simulation_truth = pandas.read_csv(self.simulationTruth_path)
        extracted_muons = pandas.read_csv(self.reconstructed_muons_path)
        return simulation_truth, extracted_muons


    def choose_muon_events(self):
        muEvent_ids = self.extracted_muons["event_id"]
        muEvents = pandas.to_numeric(muEvent_ids, downcast='signed')
        return muEvents


    def create_axis(self, ax_start=0.1, ax_end=0.8):
        fig = plt.figure(figsize=(6, 4))
        ax = fig.add_axes([ax_start, ax_start, ax_end, ax_end])
        return fig, ax


    def create_step_histogram(self, data, color, bin_edges, type):
        plt.hist(
            data, label=str(type) + " muons", histtype="step",
            bins=bin_edges, alpha=1, color=color
        )


    """ #################### Plotting ################# """


    def plot_gaussDistribution_for_R_width(self):
        oa_detected = self.simulation_truth.loc[
            self.muevents, "opening_angle"]
        oa_extracted = self.extracted_muons["muon_ring_r"]
        difference = -np.asarray(oa_detected) + np.asarray(oa_extracted)
        difference = np.rad2deg(difference)
        # print(np.std(difference))
        plt.hist(
            difference, color = 'k', histtype='step', bins=100,
            label='reconstructed minus true'
            )
        plt.xlabel("Difference /deg")
        plt.ylabel("Muon count /1")
        plt.legend(loc="upper right", fontsize='small')
        figName = "r_difference_gauss.png"
        fig_path = os.path.join(self.plot_out, figName)
        plt.savefig(fig_path, bbox_inches="tight")
        plt.close("all")


    def calculate_r_sq(self):
        x_detected = self.simulation_truth.loc[
            self.muevents, "muon_support_ground0"]
        y_detected = self.simulation_truth.loc[
            self.muevents, "muon_support_ground1"]
        r_d_sq = np.square(x_detected) + np.square(y_detected)
        x_thrown = self.simulation_truth["muon_support_ground0"]
        y_thrown = self.simulation_truth["muon_support_ground1"]
        r_t_sq = np.square(x_thrown) + np.square(y_thrown)
        return r_d_sq, r_t_sq


    def plot_impact_r_sq(self):
        r_d_sq, r_t_sq = self.calculate_r_sq()
        bin_edges = self.create_bins(r_t_sq)
        self.create_step_histogram(r_t_sq, "blue", bin_edges, "thrown")
        self.create_step_histogram(r_d_sq, "red", bin_edges, "detected")
        plt.legend(loc="upper right")
        plt.xlabel("muon impact radius / $m^2$")
        plt.ylabel("number of muons / 1")
        outpath = os.path.join(self.plot_out, "impact_r_sq.png")
        plt.savefig(outpath, bbox_inches="tight")
        plt.close("all")


    def extract_cx_cy(self):
        thrown_cx = self.simulation_truth["casual_muon_direction0"]
        thrown_cy = self.simulation_truth["casual_muon_direction1"]
        thrown_r_sq = np.square(thrown_cx) + np.square(thrown_cy)
        detected_mu_cx = self.simulation_truth.loc[
            self.muevents, "casual_muon_direction0"]
        detected_mu_cy = self.simulation_truth.loc[
            self.muevents, "casual_muon_direction1"]
        detected_r_sq = np.square(detected_mu_cx) + np.square(detected_mu_cy)
        reconstructed_cx = self.extracted_muons["muon_ring_cx"]
        reconstructed_cy = self.extracted_muons["muon_ring_cy"]
        return (
            thrown_r_sq, detected_r_sq, detected_mu_cx,
            detected_mu_cy, reconstructed_cx, reconstructed_cy
        )


    def add_matrix_to_ax(
        self, matrix, bin_edges_axis0, bin_edges_axis1, ax
    ):
        return ax.imshow(
            matrix.transpose()[::-1],
            extent=[
                bin_edges_axis1.min(),
                bin_edges_axis1.max(),
                bin_edges_axis0.min(),
                bin_edges_axis0.max()
            ],
            interpolation="none"
        )


    def plot_cxcy_sq(self):
        thrown_r_sq = self.extract_cx_cy()[0]
        detected_r_sq = self.extract_cx_cy()[1]
        bin_edges = np.rad2deg(self.create_bins(thrown_r_sq))
        self.create_step_histogram(
            np.rad2deg(thrown_r_sq), "blue", bin_edges, "thrown")
        self.create_step_histogram(
            np.rad2deg(detected_r_sq), "red", bin_edges, "detected")
        plt.legend(loc="upper right")
        plt.xlabel("muon $cx^2 + cy^2$ /$deg^2$")
        plt.ylabel("number of muons / 1")
        plotPath = os.path.join(self.plot_out, "cxcy_squared.png")
        plt.savefig(plotPath, bbox_inches="tight")
        plt.close("all")


    def plot_cx_reconstructed_and_thrown(self):
        reconstructed_cx = self.extract_cx_cy()[4]
        thrown_cx = self.extract_cx_cy()[2]
        bin_edges = np.linspace(-4.5, 4.5, num=100)
        bin_counts = np.histogram2d(
            np.rad2deg(reconstructed_cx),
            np.rad2deg(thrown_cx),
            bins=[bin_edges, bin_edges])[0]
        fig_cx, ax_cx = self.create_axis()
        im = self.add_matrix_to_ax(
            matrix=bin_counts,
            bin_edges_axis0=bin_edges,
            bin_edges_axis1=bin_edges,
            ax=ax_cx)
        fig_cx.colorbar(im, ax=ax_cx)
        ax_cx.set_xlabel("reconstructed muons cx /deg")
        ax_cx.set_ylabel("true muons cx /deg")
        plotPath = os.path.join(self.plot_out, "confusionMatrix_cx.png")
        fig_cx.savefig(plotPath, bbox_inches="tight")
        plt.close("all")


    def plot_cy_reconstructed_and_thrown(self):
        reconstructed_cy = self.extract_cx_cy()[5]
        thrown_cy = self.extract_cx_cy()[3]
        bin_edges = np.linspace(-4.5, 4.5, num=100)
        bin_counts = np.histogram2d(
            np.rad2deg(reconstructed_cy),
            np.rad2deg(thrown_cy),
            bins=[bin_edges, bin_edges])[0]
        fig_cy, ax_cy = self.create_axis()
        im = self.add_matrix_to_ax(
            matrix=bin_counts,
            bin_edges_axis0=bin_edges,
            bin_edges_axis1=bin_edges,
            ax=ax_cy)
        fig_cy.colorbar(im, ax=ax_cy)
        ax_cy.set_xlabel("reconstructed muons cy /deg")
        ax_cy.set_ylabel("true muons cy /deg")
        plotPath = os.path.join(self.plot_out, "confusionMatrix_cy.png")
        fig_cy.savefig(plotPath, bbox_inches="tight")
        plt.close("all")


    def confusionMatrix_opening_angle(self):
        thrown_opening_angle = np.rad2deg(
            self.simulation_truth.loc[self.muevents, "opening_angle"])
        reconstructed_opening_angle = np.rad2deg(
            self.extracted_muons["muon_ring_r"])
        bin_edges = np.linspace(0, 1.6, num=100)
        bin_counts = np.histogram2d(
            reconstructed_opening_angle, thrown_opening_angle, bins=[
                bin_edges, bin_edges])[0]
        fig_oa, ax_oa = self.create_axis()
        im = self.add_matrix_to_ax(
            matrix=bin_counts,
            bin_edges_axis0=bin_edges,
            bin_edges_axis1=bin_edges,
            ax=ax_oa)
        fig_oa.colorbar(im, ax=ax_oa)
        ax_oa.set_xlabel(r"reconstructed muons oa /deg")
        ax_oa.set_ylabel(r"true muons oa /deg")
        plotPath = os.path.join(self.plot_out, "confusionMatrix_oa.png")
        fig_oa.savefig(plotPath, bbox_inches="tight")
        plt.close("all")


    def compare_thrown_muon_opening_angle_with_detected(self):
        thrown_opening_angle = self.simulation_truth["opening_angle"]
        detected_opening_angle = self.extracted_muons["muon_ring_r"]
        bin_edges = self.create_bins(thrown_opening_angle)
        self.create_step_histogram(
            np.rad2deg(detected_opening_angle),
            "red", np.rad2deg(bin_edges), "reconstructed")
        self.create_step_histogram(
            np.rad2deg(thrown_opening_angle),
            "blue", np.rad2deg(bin_edges), "true")
        plt.legend(loc="upper right")
        plt.xlabel(r"muon Cherenkov cone opening angle /deg")
        plt.ylabel(r"number of muons / 1")
        plotPath = os.path.join(self.plot_out, "opening_angle.png")
        plt.savefig(plotPath, bbox_inches="tight")
        plt.close("all")


    """ ############# Main call ################# """

    def create_all_singleSimulation_plots(self):
        self.plot_gaussDistribution_for_R_width()
        self.plot_impact_r_sq()
        self.plot_cxcy_sq()
        self.plot_cx_reconstructed_and_thrown()
        self.plot_cy_reconstructed_and_thrown()
        self.confusionMatrix_opening_angle()
        self.compare_thrown_muon_opening_angle_with_detected()
