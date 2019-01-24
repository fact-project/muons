import subprocess
import numpy as np
import os
from shutil import copy
from muons.muon_ring_simulation import many_simulations as ms
from numbers import Number
import pandas
from muons.muon_ring_fuzzyness import ring_fuzziness_with_amplitude as mrfa
from muons.muon_ring_fuzzyness import muon_ring_fuzzyness as mrf
from muons.detection import detection as hough
from muons.detection_with_simple_ring_fit import (
    detection_with_simple_ring_fit as ringM)
import photon_stream as ps
import glob
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


class PSF_FuzzAnalysis:

    """ Analyze fuzz parameter dependency on true Point Spread Function """

    def __init__(
        self, preferencesFile_path, maximum_PSF,
        steps, scoop_hosts, output_dir
    ):
        self.preferencesFile_path = preferencesFile_path
        self.maximum_PSF = maximum_PSF
        self.steps = steps
        self.scoop_hosts = scoop_hosts
        self.output_dir = output_dir
        self.checkInputValidity()
        self.preferences = self.readPreferences()
        self.scoop_simulatePath = self.get_scoop_simulation_scriptPath()
        self.simulation_dir = os.path.join(output_dir, "simulations")
        self.fuzz_resultDir = os.path.join(output_dir, "fuzzResults")


    def checkInputValidity(self):
        if not os.path.exists(self.preferencesFile_path):
            raise ValueError(
                "Entered path for preferences_file is invalid")
        if not isinstance(self.maximum_PSF, Number):
            raise ValueError(
                "Value for maximum PSF needs to be a number")
        if not type(self.steps) == int:
            raise ValueError(
                "Number of steps needs to be an integer")
        if not os.path.exists(self.scoop_hosts):
            raise ValueError(
                "Entered path for scoop_hosts is invalid")
        if not type(self.output_dir) == str:
            raise ValueError(
                "Output directory needs to be a string")


    """ ############### Simulations ############### """

    def calculate_stepSize(self):
        stepsize = self.maximum_PSF/self.steps
        return stepsize


    def readPreferences(self):
        preferences = {}
        with open(self.preferencesFile_path, "r") as fIn:
            for line in fIn:
                line = line.strip("\n")
                (key, value) = line.split("= ")
                preferences[key] = value
        return preferences


    def get_scoop_simulation_scriptPath(self):
        filePath = os.path.normpath(os.path.abspath(ms.__file__))
        parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
        simulation_scriptPath = os.path.join(
            parentDir, "scoop_simulate_muon_rings.py")
        return simulation_scriptPath


    def call_scoop_once(self, step_number):
        stepsize = self.calculate_stepSize()
        scoop_script_path = self.get_scoop_simulation_scriptPath()
        scoopList = [
            "python", "-m", "scoop", "--hostfile",
            self.scoop_hosts, scoop_script_path
        ]
        dirname = "_".join(["iterStep", str(step_number)])
        stepDir = os.path.join(self.simulation_dir, dirname)
        self.preferences["--output_dir"] = stepDir
        self.preferences["--point_spread_function"] = (
            str((np.multiply(stepsize, step_number))))
        for key in self.preferences.keys():
            scoopList.append(key)
            scoopList.append(self.preferences[key])
        subprocess.call(scoopList)


    def multiple_scoop_calls(self):
        for i in range(self.steps):
            self.call_scoop_once(i)


    """ ############### Analyse simulations ################# """

    def find_all_simulation_files(self, suffix="**/psf*.sim.phs"):
        paths = []
        wild_card_path = os.path.join(self.simulation_dir, suffix)
        for path in glob.glob(wild_card_path, recursive=True):
            paths.append(path)
        return paths


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


    def save_muon_events(
        self, reconstructed_muon_events, simFile_path, method
    ):
        directory_path = os.path.dirname(os.path.realpath(simFile_path))
        filename = "_".join([method, "reconstructed_muon_events.csv"])
        output_path = os.path.join(directory_path, filename)
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
            output_path,
            reconstructed_muon_events,
            delimiter=",",
            comments='',
            header=headers
        )


    def using_hough_extraction(self, muon_propsH, photon_clusters, event_id):
        normed_responseH, fuzziness_stdParamH = (
            self.get_fuzziness_parameters(photon_clusters, muon_propsH))
        reconstructed_muon_eventH = self.get_reconstructed_muons_info(
            muon_propsH, event_id)
        return (
            normed_responseH,
            fuzziness_stdParamH,
            reconstructed_muon_eventH
        )


    def using_ringM_extraction(self, muon_propsR, photon_clusters, event_id):
        normed_responseR, fuzziness_stdParamR = (
            self.get_fuzziness_parameters(photon_clusters, muon_propsR))
        reconstructed_muon_eventR = self.get_reconstructed_muons_info(
            muon_propsR, event_id)
        return (
            normed_responseR,
            fuzziness_stdParamR,
            reconstructed_muon_eventR
        )


    def get_point_spread_function(self, simFile_path):
        splitInpath = simFile_path.split(".")
        fileName_noSuffix = ".".join([splitInpath[0], splitInpath[1]])
        simTruthPath = "".join([fileName_noSuffix, ".simulationtruth.csv"])
        simulation_truth = pandas.read_csv(simTruthPath)
        point_spread_function = simulation_truth[
            "point_spread_function_std"][0]
        return point_spread_function


    def save_fuzz_info(
        self, psf, extractionMethod, fuzzParameter,
        muonCount, average_fuzz, fuzz_stdev
    ):
        fuzz_info = np.asmatrix([
            psf, average_fuzz, fuzz_stdev, muonCount]).transpose()
        filename = "_".join([fuzzParameter, "fuzzResults.csv"])
        output_dir = os.path.join(
            self.fuzz_resultDir, extractionMethod)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, filename)
        header_list = list([
            "point_spread_function",
            "average_fuzz",
            "fuzz_std",
            "detected_muonCount"
        ])
        headers = ",".join(header_list)
        np.savetxt(
            output_path,
            fuzz_info,
            delimiter=",",
            comments='',
            header=headers
        )


    def calculate_average_and_stdev(self, fuzz):
        average_fuzz = float(np.average(fuzz))
        fuzz_stdev = float(np.std(fuzz))
        return average_fuzz, fuzz_stdev


    def extract_fuzzParam_from_single_run(self, inpath):
        response_resultsR = []
        response_resultsH = []
        fuzz_resultsR = []
        fuzz_resultsH = []
        number_muonsH = 0
        number_muonsR = 0
        mu_event_ids = []
        reconstructed_muon_eventsH = []
        reconstructed_muon_eventsR = []
        run = ps.EventListReader(inpath)
        for event_id, event in enumerate(run):
            photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
            muon_propsR = ringM(event, photon_clusters)
            muon_propsH = hough(event, photon_clusters)
            if muon_propsH['is_muon']:
                houghResults = self.using_hough_extraction(
                    muon_propsH, photon_clusters, event_id)
                reconstructed_muon_eventsH.append(houghResults[2])
                response_resultsH.append(houghResults[0])
                fuzz_resultsH.append(houghResults[1])
                number_muonsH += 1
            if muon_propsR['is_muon']:
                ringM_results = self.using_ringM_extraction(
                    muon_propsR, photon_clusters, event_id)
                reconstructed_muon_eventsR.append(ringM_results[2])
                response_resultsR.append(ringM_results[0])
                fuzz_resultsR.append(ringM_results[1])
                number_muonsR += 1
        psf = self.get_point_spread_function(inpath)
        responseR_avg, responseR_stdev = self.calculate_average_and_stdev(
            response_resultsR)
        fuzzR_avg, fuzzR_stdev = self.calculate_average_and_stdev(fuzz_resultsR)
        responseH_avg, responseH_stdev = self.calculate_average_and_stdev(
            response_resultsH)
        fuzzH_avg, fuzzH_stdev = self.calculate_average_and_stdev(fuzz_resultsH)
        runInfo = {
            "reconstructed_muon_eventsH": reconstructed_muon_eventsH,
            "responseR_avg": responseR_avg,
            "responseR_stdev": responseR_stdev,
            "fuzzR_avg": fuzzR_avg,
            "fuzzR_stdev": fuzzR_stdev,
            "number_muonsH": number_muonsH,
            "reconstructed_muon_eventsR": reconstructed_muon_eventsR,
            "responseH_avg": responseH_avg,
            "responseH_stdev": responseH_stdev,
            "fuzzH_avg": fuzzH_avg,
            "fuzzH_stdev": fuzzH_stdev,
            "number_muonsR": number_muonsR,
            "point_spread_function": psf,
            "inpath": inpath
        }
        return runInfo


    def call_scoop_for_all(self):
        filePath = os.path.normpath(os.path.abspath(__file__))
        parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
        path_to_scoopScript = os.path.join(parentDir, "scoop_compare_psf_fuzz.py")
        scoopCall = [
            "python", "-m", "scoop", "--hostfile", self.scoop_hosts,
            path_to_scoopScript,"--simulation_dir", self.simulation_dir,
            "--preferencesFile_path", self.preferencesFile_path,
            "--maximum_PSF", str(self.maximum_PSF),
            "--steps", str(self.steps), "--output_dir", self.output_dir,
            "--scoop_hosts", self.scoop_hosts
        ]
        subprocess.call(scoopCall)



    """ ##################### Plotting ####################### """


    def plot_psf_fuzz(
        self, psf_fuzz_csv_path, fuzz_parameter, extractionMethod
    ):
        psf_fuzz_df = pandas.read_csv(psf_fuzz_csv_path)
        fuzz = np.rad2deg(psf_fuzz_df["average_fuzz"])
        psf = np.rad2deg(psf_fuzz_df["point_spread_function"])
        std_fuzz = np.rad2deg(psf_fuzz_df["fuzz_std"])
        number_muons = psf_fuzz_df['detected_muonCount']
        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.errorbar(
            psf, fuzz, yerr=std_fuzz/np.sqrt(number_muons),
            fmt=".", color="k")
        ax.set_xlim(psf.min()-0.01, psf.max()+0.01)
        plt.grid()
        ax.set_xlabel("true point spread function /deg")
        if fuzz_parameter == "stdev":
            ax.set_ylabel(r"fuzziness /deg")
            ax.set_ylim(0.10,0.22)
            filename = "stdev_vs_psf.png"
            plot_outDir = os.path.join(
                self.output_dir, "Plots",  extractionMethod)
            plot_outPath = os.path.join(plot_outDir, filename)
            if not os.path.isdir(plot_outDir):
                os.makedirs(plot_outDir)
            fig.savefig(plot_outPath, bbox_inches="tight")
            plt.close("all")
        elif fuzz_parameter == "response":
            ax.set_ylabel(r"response /$\%$")
            filename = "response_vs_psf.png"
            plot_outDir = os.path.join(
                self.output_dir, "Plots",  extractionMethod)
            plot_outPath = os.path.join(plot_outDir, filename)
            if not os.path.isdir(plot_outDir):
                os.makedirs(plot_outDir)
            fig.savefig(plot_outPath, bbox_inches="tight")
            plt.close("all")


    def plot_absolute_detected_muons(
        self,
        psf_fuzz_csv_path,
        extractionMethod
    ):
        simulated_muonCount = self.preferences['--number_of_muons']
        psf_fuzz_df = pandas.read_csv(psf_fuzz_csv_path)
        detected_muonCount = psf_fuzz_df['detected_muonCount']
        psf = np.rad2deg(psf_fuzz_df["point_spread_function"])
        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.set_xlabel(r"true point spread function /deg")
        ax.set_ylabel(r"number of muons /1")
        ax.set_xlim(psf.min()-0.01, psf.max()+0.01)
        ax.axhline(
            simulated_muonCount, color="red",
            label=r"number of simulated muons")
        ax.errorbar(
            psf, detected_muonCount, fmt=".",
            yerr=np.sqrt(detected_muonCount),
            label=r"number of detected muons")
        plt.legend(loc="upper right")
        ax.set_yscale('log')
        plt.grid()
        filename = "_".join([extractionMethod, "absolute_detected_muons.png"])
        plot_outDir = os.path.join(
            self.output_dir, "Plots")
        if not os.path.isdir(plot_outDir):
            os.makedirs(plot_outDir)
        plot_out = os.path.join(plot_outDir, filename)
        plt.savefig(plot_out, bbox_inches="tight")
        plt.close("all")


    def plot_effective_area_vs_psf(
        self,
        psf_fuzz_csv_path,
        extractionMethod
    ):
        psf_fuzz_df = pandas.read_csv(psf_fuzz_csv_path)
        stepSize = self.calculate_stepSize()
        preferences_dataFrame = pandas.read_csv(
            self.preferencesFile_path, delimiter="= ",
            header=None, engine='python')
        simulated_muonCount = int(preferences_dataFrame[1][0])
        detected_muonCount = np.array(psf_fuzz_df.detected_muonCount)
        psf = np.rad2deg(psf_fuzz_df["point_spread_function"])
        aperture_radius = float(preferences_dataFrame[1][3])
        area = np.pi * np.square(aperture_radius)
        effective_area = np.divide(detected_muonCount, simulated_muonCount) * area
        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.errorbar(
            psf, effective_area, xerr=stepSize/2,
            yerr=effective_area/np.sqrt(detected_muonCount),
            fmt=".", color="k"
        )
        ax.set_yscale('log')
        ax.set_xlabel(r"true point spread function /deg")
        ax.set_ylabel(r"effective area /$m^2$")
        ax.set_xlim(psf.min()-0.01, psf.max()+0.01)
        filename = "effective_area_vs_psf.png"
        plotDir = os.path.join(self.output_dir, "Plots", extractionMethod)
        if not os.path.isdir(plotDir):
            os.makedirs(plotDir)
        plot_out = os.path.join(plotDir, filename)
        plt.grid()
        fig.savefig(plot_out, bbox_inches="tight")
        plt.close("all")


    def plot_psf_fuzz_hough_ringM_comparison(
        self,
        ringM_psf_fuzz_csv_path,
        hough_psf_fuzz_csv_path,
        fuzz_parameter
    ):
        ring_df = pandas.read_csv(ringM_psf_fuzz_csv_path)
        hough_df = pandas.read_csv(hough_psf_fuzz_csv_path)

        fuzz_ringM = np.rad2deg(ring_df["average_fuzz"])
        psf_ringM = np.rad2deg(ring_df["point_spread_function"])
        std_fuzz_ringM = np.rad2deg(ring_df["fuzz_std"])
        muonCount_ringM = ring_df['detected_muonCount']

        fuzz_hough = np.rad2deg(hough_df["average_fuzz"])
        psf_hough = np.rad2deg(hough_df["point_spread_function"])
        std_fuzz_hough = np.rad2deg(hough_df["fuzz_std"])
        muonCount_hough = hough_df['detected_muonCount']

        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.errorbar(
            psf_hough, fuzz_hough,
            yerr=std_fuzz_hough/np.sqrt(muonCount_hough),
            fmt=".", alpha=0.4, label=r"Hough")
        ax.errorbar(
            psf_ringM, fuzz_ringM,
            yerr=std_fuzz_ringM/np.sqrt(muonCount_ringM),
            fmt=".", alpha=0.4, label=r"ringModel")
        ax.set_xlabel(r"true point spread function /deg")
        ax.set_ylabel(r"fuzziness /deg")
        ax.set_xlim(psf_ringM.min()-0.01, psf_ringM.max()+0.01)
        if fuzz_parameter == "stdev":
            ax.set_ylim(0.10,0.22)
        plt.legend(loc="upper right")
        plt.grid()
        fileName = "_".join([
            "hough_ringM_psf",fuzz_parameter, "comparison.png"])
        outDir = os.path.join(self.output_dir, "Plots")
        output_path = os.path.join(outDir, fileName)
        if not os.path.isdir(outDir):
            os.makedirs(outDir)
        plt.savefig(
            output_path,
            bbox_inches="tight")
        plt.close("all")


    def plot_all(self):
        paths = []
        wild_card_path = os.path.join(self.fuzz_resultDir, "*", "*")
        for path in glob.glob(wild_card_path):
            splitPath = path.split("/")
            extractionMethod = splitPath[-2]
            fuzzParameter = splitPath[-1].split("_")[0]
            self.plot_psf_fuzz(path, fuzzParameter, extractionMethod)
            self.plot_absolute_detected_muons(
                path, extractionMethod)
            self.plot_effective_area_vs_psf(path, extractionMethod)
            Fitting = CurveFitting(
                path, fuzzParameter, extractionMethod, self.output_dir)
            Fitting.plot_curve_fit()
        wild_card_path2 = os.path.join(self.fuzz_resultDir, "hough", "*")
        for path in glob.glob(wild_card_path2):
            splitPath = path.split("/")
            fileName = splitPath[-1]
            corresponding_ringM_path = os.path.join(
                self.fuzz_resultDir, "ringM", fileName)
            if "stdev" in path:
                fuzz_parameter = "stdev"
            elif "response" in path:
                fuzz_parameter = "response"
            self.plot_psf_fuzz_hough_ringM_comparison(
                corresponding_ringM_path, path, fuzz_parameter)




    """ ############### Main call ###################### """


    def call_all(self):
        self.multiple_scoop_calls()
        self.call_scoop_for_all()
        self.plot_all()



    """ ##################### Curve fitting ################## """

class CurveFitting:

    """ Fit curve for psf fuzz plot """

    def __init__(
        self, psf_fuzz_csv_path, fuzzParameter, extractionMethod, output_dir
    ):
        self.psf_fuzz_csv_path = psf_fuzz_csv_path
        self.fuzzParameter = fuzzParameter
        self.extractionMethod = extractionMethod
        self.output_dir = output_dir
        self.psf, self.fuzz = self.read_dataFrame()
        self.psfN, self.fuzzN = self.only_some_psf(self.psf, self.fuzz)
        self.popt, self.pcov = curve_fit(self.func, self.psfN, self.fuzzN)
        self.plot_curve_fit()
        self.save_function()

    def read_dataFrame(self):
        dataFrame = pandas.read_csv(self.psf_fuzz_csv_path)
        psf = np.rad2deg(dataFrame['point_spread_function'])
        fuzz = np.rad2deg(dataFrame['average_fuzz'])
        return psf, fuzz


    def only_some_psf(self, psf, fuzz):
        mask = psf < 0.125
        psf = psf[mask]
        fuzz = fuzz[mask]
        return psf, fuzz


    def func(self, x, a, b, c, d):
        return (a*(x**3) + b*(x**2) + c*x + d)


    def f(self, x):
        a = self.popt[0]
        b = self.popt[1]
        c = self.popt[2]
        d = self.popt[3]
        return (a*(x**3) + b*(x**2) + c*x + d)


    def plot_curve_fit(self):
        rr = np.arange(0.0, 0.125, 0.01)
        plt.plot(rr, self.f(rr), linewidth=0.75, label="curveFit")
        plt.scatter(self.psf, self.fuzz, label="dataPoints")
        plt.xlim(-0.01, 0.125)
        plt.xlabel(r"true point spread function /deg")
        if self.fuzzParameter == "stdev":
            plt.ylabel(r"observed standard deviation /deg")
        elif self.fuzzParameter == "response":
            plt.ylabel(r"response /$\%$")
        plt.grid()
        plot_outDir = os.path.join(
            self.output_dir, "Plots",  self.extractionMethod)
        if not os.path.isdir(plot_outDir):
            os.makedirs(plot_outDir)
        fileName = "_".join([self.fuzzParameter, "curve_fit.png"])
        plot_outPath = os.path.join(plot_outDir, fileName)
        plt.legend(loc=1)
        plt.savefig(plot_outPath, bbox_inches="tight")
        plt.close("all")


    def save_function(self):
        a = self.popt[0]
        b = self.popt[1]
        c = self.popt[2]
        d = self.popt[3]
        filename = "_".join([self.fuzzParameter, "function_fit.csv"])
        fOut = os.path.join(
            self.output_dir, "Plots", self.extractionMethod, filename)
        header = list(["x^3", "x^2", "x", "const"])
        values = [a, b, c, d]
        headers = ",".join(header)
        np.savetxt(
            fOut,
            values,
            delimiter=",",
            comments='',
            header=headers
        )