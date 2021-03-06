import os
import numpy as np
import matplotlib
# matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas
import glob
import json
import fact
import time
from datetime import datetime
import csv
from muons.analysis_utensils.muon_ring_fuzzyness import muon_ring_fuzzyness as mrf
from muons.analysis_utensils.muon_ring_fuzzyness import ring_fuzziness_with_amplitude as mrfa
import subprocess
import photon_stream as ps
from muons.detection_with_simple_ring_fit import (
    detection_with_simple_ring_fit as ringM_detection)
from muons.detection import detection
from scipy.optimize import curve_fit



class RealObservationAnalysis:

    """ Performs the analysis of real observations 
        using all here established tools"""


    def __init__(
        self, muon_dir, output_dir,
        epochFile, scoop_hosts,
        fitDir
    ):
        self.muon_dir = muon_dir
        self.output_dir = output_dir
        self.epochFile = epochFile
        self.scoop_hosts = scoop_hosts
        self.fitDir = fitDir
        self.check_inputValidity()
        self.plot_dir = os.path.join(output_dir, "Plots")


    def check_inputValidity(self):
        if not os.path.isdir(self.muon_dir):
            raise ValueError(
                "Muon directory needs to exist")
        if not type(self.output_dir) == str:
            raise ValueError(
                "Output directory needs to be a string")
        if not os.path.exists(self.epochFile):
            raise ValueError(
                "Epoch file is missing!")
        if not os.path.exists(self.scoop_hosts):
            raise ValueError(
                "Scoop hosts file missing")
        if not os.path.isdir(self.fitDir):
            raise ValueError(
                "Directory for fit does not exist")


    def create_jobs(self):
        jobs = []
        wild_card_path = os.path.join(
            self.muon_dir, "*", "*", "*", "*.phs.jsonl.gz")
        for inpath in glob.glob(wild_card_path):
            job = {}
            job["inpath"] = inpath
            fact_path = fact.path.parse(inpath)
            job["output_path_stdevH"] = fact.path.tree_path(
                night=fact_path["night"],
                run=fact_path["run"],
                suffix="stdev.muon.fuzz.jsonl",
                prefix=os.path.join(self.output_dir, "hough"))
            job["output_path_stdevR"] = fact.path.tree_path(
                night=fact_path["night"],
                run=fact_path["run"],
                suffix="stdev.muon.fuzz.jsonl",
                prefix=os.path.join(self.output_dir, "ringM"))
            job["output_path_responseR"] = fact.path.tree_path(
                night=fact_path["night"],
                run=fact_path["run"],
                suffix="rsp.muon.fuzz.jsonl",
                prefix=os.path.join(self.output_dir, "ringM"))
            job["output_path_responseH"] = fact.path.tree_path(
                night=fact_path["night"],
                run=fact_path["run"],
                suffix="rsp.muon.fuzz.jsonl",
                prefix=os.path.join(self.output_dir, "hough"))
            jobs.append(job)
            jobs.append(job)
            jobs.append(job)
        return jobs


    def run_job(self, job):
        results = []
        inpath = job["inpath"]
        output_path_responseH = job["output_path_responseH"]
        output_path_stdevR = job["output_path_stdevR"]
        output_path_responseR = job["output_path_responseR"]
        output_path_stdevH = job["output_path_stdevH"]
        muonCountH = 0
        muonCountR = 0
        run = ps.EventListReader(inpath)
        muon_ring_featuresR = []
        muon_ring_featuresH = []
        fuzziness_stdParamRs = []
        fuzziness_stdParamHs = []
        normed_responseRs = []
        normed_responseHs = []
        fuzz_paramsH = []
        for event_id, event in enumerate(run):
            photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
            muon_propsR = ringM_detection(event, photon_clusters)
            muon_propsH = detection(event, photon_clusters)
            if muon_propsH["is_muon"]:
                muonCountH += 1
                normed_responseH, fuzziness_stdParamH = (
                    self.get_fuzziness_parameters(
                        photon_clusters, muon_propsH))
                muon_ring_featureH = [
                    muon_propsH["muon_ring_cx"],
                    muon_propsH["muon_ring_cy"],
                    muon_propsH["muon_ring_r"]
                ]
                muon_ring_featuresH.append(muon_ring_featureH)
                fuzziness_stdParamHs.append(fuzziness_stdParamH)
                normed_responseHs.append(normed_responseH)
            if muon_propsR["is_muon"]:
                muonCountR += 1
                normed_responseR, fuzziness_stdParamR = (
                    self.get_fuzziness_parameters(
                        photon_clusters, muon_propsR))
                muon_ring_featureR = [
                    muon_propsR["muon_ring_cx"],
                    muon_propsR["muon_ring_cy"],
                    muon_propsR["muon_ring_r"]
                ]
                fuzziness_stdParamRs.append(fuzziness_stdParamR)
                normed_responseRs.append(normed_responseR)
                muon_ring_featuresR.append(muon_ring_featureR)
        fact_path = fact.path.parse(inpath)
        night = fact_path["night"]
        run = fact_path["run"]
        filename = str(night) + "_" + str(run) + ".csv"
        output_dirR = os.path.dirname(output_path_stdevR)
        output_dirH = os.path.dirname(output_path_stdevH)
        if not os.path.isdir(output_dirR):
            os.makedirs(output_dirR, exist_ok=True)
        if not os.path.isdir(output_dirH):
            os.makedirs(output_dirH, exist_ok=True)
        self.save_to_file("ringM", output_dirR, filename, muon_ring_featuresR)
        self.save_to_file("hough", output_dirH, filename, muon_ring_featuresH)
        self.save_fuzz_param(output_path_stdevR, fuzziness_stdParamRs, muonCountR)
        self.save_fuzz_param(output_path_responseR, normed_responseRs, muonCountR)
        self.save_fuzz_param(output_path_stdevH, fuzziness_stdParamHs, muonCountH)
        self.save_fuzz_param(output_path_responseH, normed_responseHs, muonCountH)
        return 0


    def save_to_file(self, method, output_dir, filename, muon_ring_features):
        outpath = os.path.join(output_dir,  filename)
        header = list(["cx", "cy", "r"])
        headers = ",".join(header)
        np.savetxt(
            outpath,
            muon_ring_features,
            delimiter=",",
            comments="",
            header=headers
            )


    def save_fuzz_param(self, outpath, fuzz, number_muons):
        with open(outpath, "wt") as fout:
            out = {
                "average_fuzz": float(np.average(fuzz)),
                "std_fuzz": float(np.std(fuzz)),
                "number_muons": number_muons,
            }
            fout.write(json.dumps(out))


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


    def get_scoopScript_path(self):
        # filePath = os.path.normpath(os.path.abspath(__file__))
        # parentDir = os.path.normpath(os.path.join(
        #     filePath, os.pardir))
        # scriptDir = os.path.join(parentDir, "real_observation_analysis")
        scoopScriptPath = os.path.join(
            os.getcwd(), "scoop_real_distributions.py")
        return scoopScriptPath


    def run_scoop_analysis(self):
        scriptPath = self.get_scoopScript_path()
        scoopCommand = [
            "python", "-m", "scoop", "--hostfile", self.scoop_hosts,
            scriptPath, "--muon_dir", self.muon_dir, "--output_dir",
            self.output_dir, "--epochFile", self.epochFile, "--scoop_hosts",
            self.scoop_hosts, "--fitDir", self.fitDir
        ]
        subprocess.call(scoopCommand)

    """ ################## Analyze fuzz #################### """



    def reduce_unsorted(self, muon_fuzz_dir, suffix):
        nights = []
        runs = []
        average_fuzzs = []
        std_fuzzs = []
        number_muons = []
        wCardPath = os.path.join(muon_fuzz_dir, "*", "*", "*", "*"+suffix)
        for path in glob.glob(wCardPath):
            fPath = fact.path.parse(path)
            night = fPath["night"]
            run = fPath["run"]
            try:
                with open(path, "rt") as reader:
                    line_dictionary = json.loads(reader.read())
                    nights.append(night)
                    runs.append(run)
                    average_fuzzs.append(line_dictionary["average_fuzz"])
                    std_fuzzs.append(line_dictionary["std_fuzz"])
                    number_muons.append(line_dictionary["number_muons"])
            except json.decoder.JSONDecodeError:
                continue
        return {
            "fNight": np.array(nights),
            "fRunID": np.array(runs),
            "average_fuzz": np.array(average_fuzzs),
            "std_fuzz": np.array(std_fuzzs),
            "number_muons": np.array(number_muons)
        }


    # sort the array
    def reduction(self, muon_fuzz_dir, suffix):
        unsorted_runs = self.reduce_unsorted(muon_fuzz_dir, suffix)
        df = pandas.DataFrame(unsorted_runs)
        return df.sort_values(by=["fNight", "fRunID"])


    # average over nights
    def night_wise(self, muon_fuzz):
        unique_nights = sorted(list(set(muon_fuzz.fNight.values)))
        unique_n = []
        avg_mu_fuzz = []
        n_std_fuzz = []
        muon_nr_night = []
        for unique_night in unique_nights:
            mask = muon_fuzz.fNight == unique_night
            muon_fuzz_night = muon_fuzz[mask]
            if np.sum(muon_fuzz_night.number_muons) != 0:
                unique_n.append(unique_night)
                valid_runs = muon_fuzz_night.number_muons > 0
                avg_muon_fuzz_night = np.average(
                    muon_fuzz_night.average_fuzz[valid_runs],
                    weights = muon_fuzz_night.number_muons[valid_runs]
                    )
                avg_mu_fuzz.append(avg_muon_fuzz_night)
                sum_mu_night = np.sum(muon_fuzz_night.number_muons[valid_runs])
                muon_nr_night.append(sum_mu_night)
                sum_mu_run = muon_fuzz_night.number_muons[valid_runs]
                std_fuzz_run = muon_fuzz_night.std_fuzz[valid_runs]
                sum_std_fz = np.square((sum_mu_run/sum_mu_night)*std_fuzz_run)
                sum_over_runs_std_w_sqrt = np.sqrt(np.sum(sum_std_fz))
                n_std_fuzz.append(sum_over_runs_std_w_sqrt)
        return(avg_mu_fuzz, n_std_fuzz, unique_n, muon_nr_night)


    # plot data nightwise
    def plot(self, muon_fuzz, plt_dir, extraction, min_alpha=0.1):
        avg_fz_rad, std_fz_rad, night, muon_nr = self.night_wise(muon_fuzz)
        unix_time = []
        max_m_count = (np.amax(muon_nr))
        alpha = np.divide(muon_nr, max_m_count)
        alpha = (min_alpha + alpha)/(1 + min_alpha)
        if extraction == 'stdev':
            avg_fz_deg = np.rad2deg(avg_fz_rad)
            std_fz_deg = np.rad2deg(std_fz_rad)
        elif extraction == 'response':
            avg_fz_deg = np.multiply(100, avg_fz_rad)
            std_fz_deg = np.multiply(100, std_fz_rad)
        for dt in night:
            dto = datetime.strptime(str(dt), "%Y%m%d")
            unix_time.append(dto.timestamp())
        first_night = datetime.fromtimestamp(np.min(unix_time))
        last_night = datetime.fromtimestamp(np.max(unix_time))
        first_year = first_night.year
        last_year = last_night.year
        years = np.arange(first_year, last_year + 1)
        year_time_stamps = []
        for year in years:
            year_time_stamps.append(
                datetime(year=year, month=1, day=1).timestamp()
            )
        y_m = np.subtract(avg_fz_deg, std_fz_deg/np.sqrt(muon_nr))
        y_p = np.add(avg_fz_deg, std_fz_deg/np.sqrt(muon_nr))
        plt.figure(figsize=(16, 9))
        plt.rcParams.update({'font.size': 25})
        for i in range(len(alpha) - 1):
            check = unix_time[i] <= 1432123200 and unix_time[i] >= 1420113600
            if not check:
                plt.errorbar(
                    unix_time[i], avg_fz_deg[i], yerr=std_fz_deg[i]/np.sqrt(muon_nr[i]),
                    alpha=alpha[i], color="k", fmt=".")
        for year_time_stamp in year_time_stamps:
            plt.axvline(x=year_time_stamp, color='k', alpha=0.2)
        dict_list = self.read_epoch_file()
        for preference in dict_list:
            x = preference["x"]
            linestyle = preference["linestyle"]
            color = preference["color"]
            linewidth = preference["linewidth"]
            comment = preference["comment"]
            self.plot_epoch(x, linestyle, color, linewidth, comment)
        plt.axvspan(
             1420113600, 1432123200, facecolor="none", edgecolor='k',
             alpha=0.05, label='faulty electronics',
             hatch="X")
        plt.xlabel("unix time / s")
        plt.grid(alpha = 0.2, axis = "y" , color = "k")
        if extraction == "response":
            plt.ylabel(r"response / \%")
        else:
            plt.ylabel(r"fuzz / deg")
        # plt.legend(fancybox= True, loc='upper right')
        fig_name = "fuzziness_over_time.png"
        fig_path = os.path.join(plt_dir, fig_name)
        plt.savefig(fig_path, dpi = 120)
        plt.close("all")


    def plot_epoch(self, x, linestyle, color, linewidth, comment):
        plt.axvline(
            x=x,
            linestyle=linestyle,
            color=color,
            linewidth=linewidth,
            label = comment)


    def read_epoch_file(self):
        with open(self.epochFile, "r") as csvin:
            csv_file = csv.reader(csvin, delimiter=',')
            dict_list = []
            next(csv_file)
            for line in csv_file:
                dictionary = {
                    "x" : float(line[0]),
                    "linestyle" : line[1],
                    "color" : line[2],
                    "linewidth" : float(line[3]),
                    "comment" : line[4]
                }
                dict_list.append(dictionary)
        return dict_list


    def fuzz_plotting(self):
        detections = ["hough", "ringM"]
        extractions = ["response", "stdev"]
        for detection in detections:
            for extraction in extractions:
                plot_outDir = os.path.join(
                    self.plot_dir, "Fuzz", detection, extraction)
                if not os.path.isdir(plot_outDir):
                    os.makedirs(plot_outDir, exist_ok=True)
                if extraction == "response":
                    suffix = "rsp.muon.fuzz.jsonl"
                elif extraction == "stdev":
                    suffix = "stdev.muon.fuzz.jsonl"
                fit_fileName = "_".join([extraction, "function_fit.csv"])
                functionFit_path = os.path.join(
                    self.fitDir, detection, fit_fileName)
                merged_nightwise = os.path.join(
                    self.output_dir, detection)
                muon_fuzz = self.reduction(merged_nightwise, suffix)
                self.plot(muon_fuzz, plot_outDir, extraction)
                self.plot_psf_vs_time(
                    muon_fuzz, plot_outDir, functionFit_path, extraction)


    """ ############## Distribution analysis ################## """

    def collect_items(self, method_dir):
        wild_card_path = os.path.join(method_dir, "*", "*", "*", "*.csv")
        rs = []
        cxs = []
        cys = []
        for run in glob.glob(wild_card_path):
            df = pandas.read_csv(run)
            df = df.dropna()
            r = np.rad2deg(df["r"])
            rs.extend(r)
        return rs



    def compare_rs(self, hough_rs, ringM_rs, plot_out):
        plt.hist(
            hough_rs, bins=250, color="k",
            label="Hough", density=True, stacked=True)
        plt.hist(
            ringM_rs, alpha=0.5, color="grey", bins=250,
            label="ringModel", density=True, stacked=True, zorder=10)
        plt.xlabel("opening angle /deg")
        plt.ylabel("normed muon count /1")
        plt.legend(loc="upper right")
        plt.xlim(0.4, 1.7)
        plt.savefig(plot_out + "/radius_comparison_real.png")
        plt.close("all")


    def distribution_main(self):
        hough_dir = os.path.join(self.output_dir, "hough")
        ringM_dir = os.path.join(self.output_dir, "ringM")
        plot_out = os.path.join(self.plot_dir, "Distributions")
        if not os.path.isdir(plot_out):
            os.makedirs(plot_out, exist_ok=True)
        hough_rs = self.collect_items(hough_dir)
        ringM_rs = self.collect_items(ringM_dir)
        self.compare_rs(hough_rs, ringM_rs, plot_out)


    """ Plot PSF vs time using the relation from the simulations """

    def plot_psf_vs_time(
        self,
        muon_fuzz,
        plt_dir,
        functionFit_path,
        extraction,
        min_alpha = 0.1
    ):
        avg_fz_rad, std_fz_rad, night, muon_nr = self.night_wise(muon_fuzz)
        dataFrame = pandas.read_csv(functionFit_path)
        a = dataFrame["x^3"][0]
        b = dataFrame["x^2"][0]
        c = dataFrame["x"][0]
        d = dataFrame["const"][0]
        max_m_count = (np.amax(muon_nr))
        unix_time = []
        std_fz_deg = np.rad2deg(std_fz_rad)
        if extraction == 'stdev':
            avg_fz_deg = np.rad2deg(avg_fz_rad)
        elif extraction == 'response':
            avg_fz_deg = np.multiply(100, avg_fz_rad)
        x = np.arange(0,0.1, 0.0001)
        y = (lambda x: a*(x**3) + b*(x**2) + c*(x) + d)
        sorted_arguments = np.argsort(y(x))
        psf = np.interp(avg_fz_deg, y(x)[sorted_arguments], x[sorted_arguments])
        # psf_err = psf/np.sqrt(muon_nr)
        max_m_count = (np.amax(muon_nr))
        alpha = np.divide(muon_nr, max_m_count)
        alpha = (min_alpha + alpha)/(1 + min_alpha)

        for dt in night:
            dto = datetime.strptime(str(dt), "%Y%m%d")
            unix_time.append(dto.timestamp())

        first_night = datetime.fromtimestamp(np.min(unix_time))
        last_night = datetime.fromtimestamp(np.max(unix_time))
        first_year = first_night.year
        last_year = last_night.year
        years = np.arange(first_year, last_year + 1)
        year_time_stamps = []
        for year in years:
            year_time_stamps.append(
                datetime(year=year, month=1, day=1).timestamp()
            )
        plt.figure(figsize=(16, 9))
        plt.rcParams.update({'font.size': 25})
        a, b, c, d = find_inverse_function(x, y(x))
        psf_error = abs((3*a*avg_fz_deg**2 + 2*b * avg_fz_deg + c) * (1/(np.sqrt(muon_nr))))
        for i in range(len(unix_time) - 1):
            check = unix_time[i] <= 1432123200 and unix_time[i] >= 1420113600
            if not check:
                plt.errorbar(
                    unix_time[i], psf[i], yerr=psf_error[i],
                    alpha=alpha[i], color="k", fmt=".")
        for year_time_stamp in year_time_stamps:
            plt.axvline(x=year_time_stamp, color='k', alpha=0.2)
        dict_list = self.read_epoch_file()
        for preference in dict_list:
            x = preference["x"]
            linestyle = preference["linestyle"]
            color = preference["color"]
            linewidth = preference["linewidth"]
            comment = preference["comment"]
            self.plot_epoch(x, linestyle, color, linewidth, comment)
        self.save_psf_results(night, psf, psf_error, muon_nr, plt_dir)
        plt.axvspan(
            1420113600, 1432123200, facecolor="none", edgecolor='k',
            alpha=0.05, label='faulty electronics',
            hatch="X")
        plt.xlabel("unix time / s")
        plt.ylim(0.02,0.08)
        plt.grid(alpha = 0.2, axis = "y" , color = "k")
        plt.ylabel("reconstructed PSF / deg")
        fig_name = "psf_vs_time.png"
        fig_path = os.path.join(plt_dir, fig_name)
        plt.savefig(fig_path, dpi = 120)
        plt.close("all")


    def save_psf_results(self, night, psf, psf_error, number_muons, plt_dir):
        df = pandas.DataFrame(
            {
                "fNight": night,
                "PSF_deg": psf,
                "PSF_err_deg":psf_error,
                "number_muons": number_muons
            }
        )
        df1=df.loc[df["fNight"] >= 20150520]
        df2=df.loc[df["fNight"] <= 20150101]
        result = pandas.concat([df2, df1])
        outpath = os.path.join(plt_dir, "psf_vs_time.csv")
        result.to_csv(outpath, index=False)


def find_inverse_function(x, y):
    popt = curve_fit(func, y, x)[0]
    a = popt[0]
    b = popt[1]
    c = popt[2]
    d = popt[3]
    return a, b, c, d


def func(x, a, b, c, d):
    return (a*(x**3) + b*(x**2) + c*(x) + d)

    """ ################## Analysis main ################## """

    def do_whole_analysis(self):
        self.run_scoop_analysis()
        self.fuzz_plotting()
        self.distribution_main()
