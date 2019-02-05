import matplotlib
matplotlib.use('agg')
import photon_stream as ps
import numpy as np
import os
import subprocess
import docopt
import pandas
from statistics import mean
import matplotlib.pyplot as plt
import glob
from numbers import Number
from muons import muon_ring_simulation as mrs


class DetectionMethodEvaluation:

    """ Evaluate detection method """

    def __init__(
        self, output_dir, number_of_muons, steps, step_size, scoop_hosts
    ):
        self.output_dir = output_dir
        self.number_of_muons = number_of_muons
        self.steps = steps
        self.step_size = step_size
        self.scoop_hosts = scoop_hosts
        self.check_input_correctness()
        self.scoop_simulateFile = self.get_scoop_simulate_muon_rings_path()
        self.simulation_dir = os.path.join(self.output_dir, "simulations")
        self.pure_cherenkov_dir = os.path.join(
            self.simulation_dir, "pure")
        self.nsb_dir = os.path.join(
            self.simulation_dir, "NSB")
        self.create_outputDir()


    def check_input_correctness(self):
        if not type(self.output_dir) == str:
            raise ValueError(
                "Entered output_dir needs to be a string")
        if not type(self.number_of_muons) == int:
            raise ValueError(
                "Number of muons needs to be an integer")
        if not type(self.steps) == int:
            raise ValueError(
                "Number of 'steps' needs to be an integer")
        if not isinstance(self.step_size, Number):
            raise ValueError(
                "Stepsize needs to be a number")
        if not os.path.exists(self.scoop_hosts):
            raise ValueError(
                "Scoop hosts file needs to exist!")



    """ #################### Simulations #######################"""


    def get_scoop_simulate_muon_rings_path(self):
        ring_simulation_filePath = os.path.normpath(
            os.path.abspath(mrs.__file__))
        muon_ring_simulation_directory = os.path.normpath(
            os.path.join(ring_simulation_filePath, os.pardir))
        path_to_scoop_simulate = os.path.join(
            muon_ring_simulation_directory,"scoop_simulate_muon_rings.py")
        return path_to_scoop_simulate


    def create_outputDir(self):
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)


    def run_simulation(self, simulation_dir, nsb_rate=35e6):
        scoopList = [
            "python", "-m", "scoop", "--hostfile",
            self.scoop_hosts, self.scoop_simulateFile, "--output_dir",
            str(simulation_dir), "--number_of_muons",
            str(self.number_of_muons), "--max_inclination", str(4.5),
            "--max_aperture_radius", str(4), "--test_detection", str(True),
            "--nsb_rate_per_pixel", str(nsb_rate)
        ]
        subprocess.call(scoopList)


    def cut_hist(self, nsb_cherenkov_photon_stream):
        cherenkov_photons = []
        r = np.sqrt(
            nsb_cherenkov_photon_stream[:,0]**2
            + nsb_cherenkov_photon_stream[:,1]**2
        )
        r_stedev = np.std(r)
        r_average = np.average(r)
        t_stdev = np.std(nsb_cherenkov_photon_stream[:,2])
        t_average = np.average(nsb_cherenkov_photon_stream[:,2])
        for photon in nsb_cherenkov_photon_stream:
            photon_r = np.sqrt(photon[0]**2 + photon[1]**2)
            if not (photon_r > r_average + 1.95*r_stedev) and not (
                photon_r < r_average - 1.95*r_stedev
            ):
                if not (photon[2] > t_average + 1.95*t_stdev) and not (
                    photon[2] < t_average - 1.95*t_stdev
                ):
                    cherenkov_photons.append(photon)
        return cherenkov_photons


    def do_clustering(
        self,
        pure_cherenkov_events_path,
        events_with_nsb_path
    ):
        pure_cherenkov_run = ps.EventListReader(
            pure_cherenkov_events_path)
        nsb_run = ps.EventListReader(events_with_nsb_path)
        nsb_run_found_photons = []
        pure_cherenkov_run_photons = []
        cut_cherenkov = []
        all_photons_run = []
        for event in nsb_run:
            photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
            cherenkov_cluster_mask = photon_clusters.labels >= 0
            nsb_cherenkov_photon_stream = photon_clusters.point_cloud
            nsb_cherenkov_ps = nsb_cherenkov_photon_stream[
            cherenkov_cluster_mask]
            cherenkov_photons = self.cut_hist(nsb_cherenkov_ps)
            cut_cherenkov.append(cherenkov_photons)
            nsb_run_found_photons.append(nsb_cherenkov_ps[:, 0:3])
            all_photons = event.photon_stream.point_cloud
            all_photons_run.append(all_photons)
        for muon in pure_cherenkov_run:
            pure_photon_stream = muon.photon_stream.point_cloud
            pure_cherenkov_run_photons.append(pure_photon_stream)
        return (
            all_photons_run,
            pure_cherenkov_run_photons,
            nsb_run_found_photons,
            cut_cherenkov
        )


    def true_false_decisions(
        self,
        all_photons_run,
        pure_cherenkov_run_photons,
        nsb_run_found_photons
    ):
        events = []
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
            event = [
                len(nsb_run_found_photons[muon]),
                len(pure_cherenkov_run_photons[muon]),
                true_positives,
                false_positives,
                false_negatives,
                true_negatives,
                np.multiply(precision, 100),
                np.multiply(sensitivity,100)
            ]
            events.append(event)
        return events


    def save_to_file(self, file_out, events):
        np.set_printoptions(suppress=True)
        header = list([
            "events_with_nsb",
            "pure_events",
            "true_positives",
            "false_positives",
            "false_negatives",
            "true_negatives",
            "precision",
            "sensitivity"
        ])
        headers = ",".join(header)
        np.savetxt(
            file_out,
            events,
            fmt='%.5f',
            delimiter=",",
            comments='',
            header=headers
        )


    def analyze(self, file_out):
        dataFrame = pandas.read_csv(file_out)
        non_zero = dataFrame.loc[dataFrame['precision']!=0]
        precisions = non_zero['precision']
        sensitivities = non_zero['sensitivity']
        avg_precision = mean(precisions)
        std_precision = np.std(precisions)
        avg_sensitivity = mean(sensitivities)
        std_sensitivity = np.std(sensitivities)
        return {
            "avg_precision": avg_precision,
            "std_precision": std_precision,
            "avg_sensitivity": avg_sensitivity,
            "std_sensitivity": std_sensitivity,
            "precisions": precisions,
            "sensitivities": sensitivities
        }


    def one_nsb_rate(
        self, output_dir, nsb_rate
    ):
        simulation_dir = os.path.join(output_dir, "simulation")
        if not os.path.isdir(simulation_dir):
            os.makedirs(simulation_dir)
        self.run_simulation(simulation_dir, nsb_rate)
        pure_cherenkov_events_path = os.path.join(
            simulation_dir, "pure", "psf_0.sim.phs")
        events_with_nsb_path = os.path.join(
            simulation_dir, "NSB", "psf_0.sim.phs")
        clustering_results = self.do_clustering(
            pure_cherenkov_events_path, events_with_nsb_path)
        events = self.true_false_decisions(
            clustering_results[0],
            clustering_results[1],
            clustering_results[2])
        events_cut = self.true_false_decisions(
            clustering_results[0],
            clustering_results[1],
            clustering_results[3])
        filename_cut = "cut_precision_results.csv"
        filename = "precision_results.csv"
        file_out = os.path.join(output_dir, filename)
        file_out_cut = os.path.join(output_dir, filename_cut)
        self.save_to_file(file_out, events)
        self.save_to_file(file_out_cut, events_cut)
        results = self.analyze(file_out)
        results_cut = self.analyze(file_out_cut)
        self.plot_sensitivity_precision(results, output_dir, "noCut")
        self.plot_sensitivity_precision(results_cut, output_dir, "cut")
        return results, results_cut


    def multiple_nsb_rates(self):
        dark_night_nsb_rate = 35e6
        sensitivities = []
        precisions = []
        nsb_rates = []
        sensitivities_cut = []
        precisions_cut = []
        muonCounts = []
        for i in range(self.steps):
            nsb_rate = dark_night_nsb_rate * self.step_size**i
            outDir = os.path.join(self.output_dir, '{:.2e}'.format(nsb_rate))
            if not os.path.isdir(outDir):
                os.makedirs(outDir)
            results, results_cut = self.one_nsb_rate(outDir, nsb_rate)
            sensitivities.append(results['avg_sensitivity'])
            precisions.append(results['avg_precision'])
            sensitivities_cut.append(results_cut['avg_sensitivity'])
            precisions_cut.append(results_cut['avg_precision'])
            nsb_rates.append(nsb_rate)
            muonCount = len(results['precisions'])
            muonCounts.append(muonCount)
        self.plot_different_NSB(
            nsb_rates, precisions_cut, sensitivities_cut, muonCounts, "cut")
        self.plot_different_NSB(
            nsb_rates, precisions, sensitivities, muonCounts, "noCut")
        self.plot_different_NSB_sens_prec(nsb_rates, precisions, sensitivities, 
            precisions_cut, sensitivities_cut, muonCounts
        )


    """ ################ Plotting ##########################"""

    def plot_sensitivity_precision(
        self, results, output_dir, method
    ):
        output_dirP = os.path.join(output_dir, method)
        if not os.path.isdir(output_dirP):
            os.makedirs(output_dirP)
        nr_events = len(results['sensitivities'])
        sens_max = results['avg_sensitivity'] + results['std_sensitivity']
        sens_min = results['avg_sensitivity'] - results['std_sensitivity']
        prec_max = results['avg_precision'] + results['std_precision']
        prec_min = results['avg_precision'] - results['std_precision']
        plt.scatter(
            np.arange(nr_events), results['precisions'], s=8, color = 'red')
        plt.axhline(
            results['avg_precision'], label=r"average precision", color='k')
        plt.fill_between(
            x=np.arange(nr_events), y1=prec_min,
            y2=prec_max, alpha=0.3, color='gray')
        plt.xlabel(r"event id")
        plt.ylabel(r"percentage / \%")
        plt.ylim([0, 101])
        plt.xlim([0, nr_events])
        plt.legend(fancybox= True, loc='lower right')
        plot_out = os.path.join(output_dirP, "precision.png")
        plt.savefig(plot_out, bbox_inches='tight')
        plt.close("all")
        plt.scatter(
            np.arange(nr_events),
            results['sensitivities'], s=8, color = 'red')
        plt.axhline(
            results['avg_sensitivity'],
            label=r"average sensitivity", color='k')
        plt.fill_between(
            x=np.arange(nr_events), y1=sens_min,
            y2=sens_max, alpha=0.3, color='gray')
        plt.xlabel(r"event id")
        plt.ylabel(r"percentage / \%")
        plt.ylim([0, 101])
        plt.xlim([0, nr_events])
        plt.legend(fancybox= True, loc='lower right')
        plot_out = os.path.join(output_dirP, "sensitivity.png")
        plt.savefig(plot_out, bbox_inches='tight')
        plt.close("all")


    def plot_different_NSB(
        self, NSB_rates, precisions, sensitivities, muonCounts, method
    ):
        plt.errorbar(
            NSB_rates, precisions, yerr=precisions/np.sqrt(muonCounts),
            color = "k", label=r"average precision", fmt=".")
        plt.xlabel(r"NSB rate /Hz/pixel")
        plt.ylabel(r"precision /\%")
        plt.legend(fancybox= True, loc='lower right')
        plt.ylim([0,110])
        plt.savefig(
            os.path.join(self.output_dir, method+"_NSB_precision.png"),
            bbox_inches='tight')
        plt.close("all")
        plt.errorbar(
            NSB_rates, sensitivities, yerr=sensitivities/np.sqrt(muonCounts),
            color = "k", label=r"average sensitivity", fmt=".")
        plt.xlabel(r"NSB rate /Hz/pixel")
        plt.ylim([0,110])
        plt.ylabel(r"sensitivity /\%")
        plt.legend(fancybox= True, loc='lower right')
        filename = "_".join([method, "NSB_sensitivity.png"])
        plotPath = os.path.join(self.output_dir, filename)
        plt.savefig(plotPath, bbox_inches='tight')
        plt.close("all")


    def plot_different_NSB_sens_prec(
        self, NSB_rates,
        precisions, sensitivities,
        precisions_cut, sensitivities_cut,
        muonCounts
    ):
        plt.errorbar(
            NSB_rates, precisions, yerr=precisions/np.sqrt(muonCounts),
            label=r"average precision", fmt=".", alpha=0.5)
        plt.errorbar(
            NSB_rates, precisions_cut, yerr=precisions_cut/np.sqrt(muonCounts),
            label=r"average precision", fmt=".", alpha=0.5)
        plt.xlabel(r"NSB rate /Hz/pixel")
        plt.ylabel(r"precision /\%")
        plt.legend(fancybox= True, loc='lower right')
        plt.ylim([0,110])
        plt.savefig(
            os.path.join(self.output_dir, "both_NSB_precision.png"),
            bbox_inches='tight')
        plt.close("all")
        plt.errorbar(
            NSB_rates, sensitivities, yerr=sensitivities/np.sqrt(muonCounts),
            label=r"average sensitivity", fmt=".", alpha=0.5)
        plt.errorbar(
            NSB_rates, sensitivities_cut, yerr=sensitivities_cut/np.sqrt(muonCounts),
            label=r"average sensitivity", fmt=".", alpha=0.5)
        plt.xlabel(r"NSB rate /Hz/pixel")
        plt.ylim([0,110])
        plt.ylabel(r"sensitivity /\%")
        plt.legend(fancybox= True, loc='lower right')
        filename = "both_NSB_sensitivity.png"
        plotPath = os.path.join(self.output_dir, filename)
        plt.savefig(plotPath, bbox_inches='tight')
        plt.close("all")