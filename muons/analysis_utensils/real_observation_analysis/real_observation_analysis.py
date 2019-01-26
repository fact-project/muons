import os
import numpy as np
# import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas
import glob
import json
import fact
import time
from datetime import datetime
import csv
from muons.muon_ring_fuzzyness import muon_ring_fuzzyness as mrf
from muons.muon_ring_fuzzyness import ring_fuzziness_with_amplitude as mrfa
import subprocess
import photon_stream as ps
from muons.detection_with_simple_ring_fit import (
    detection_with_simple_ring_fit as ringM_detection)
from muons.detection import detection


class RealObservationAnalysis:

    """ Performs the analysis of real observations 
        using all here established tools"""


    def __init__(self, muon_dir, output_dir, epochFile, scoop_hosts):
        self.muon_dir = muon_dir
        self.output_dir = output_dir
        self.epochFile = epochFile
        self.scoop_hosts =scoop_hosts
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
            os.makedirs(output_dirR)
        if not os.path.isdir(output_dirH):
            os.makedirs(output_dirH)
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
        with open(outpath + ".temp", "wt") as fout:
            out = {
                "average_fuzz": float(np.average(fuzz)),
                "std_fuzz": float(np.std(fuzz)),
                "number_muons": number_muons,
            }
            fout.write(json.dumps(out))
        os.rename(outpath + ".temp", outpath)


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
        parentDir = os.getcwd()
        # scriptDir = os.path.join(parentDir, "real_observation_analysis")
        scoopScriptPath = os.path.join(
            parentDir, "scoop_real_distributions.py")
        return scoopScriptPath


    def run_scoop_analysis(self):
        scriptPath = self.get_scoopScript_path()
        scoopCommand = [
            "python", "-m", "scoop", "--hostfile", self.scoop_hosts,
            scriptPath, "--muon_dir", self.muon_dir, "--output_dir",
            self.output_dir, "--epochFile", self.epochFile, "--scoop_hosts",
            self.scoop_hosts
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
    def plot(self, muon_fuzz, plt_dir, min_alpha=0.1):
        avg_fz_rad, std_fz_rad, night, muon_nr = self.night_wise(muon_fuzz)
        unix_time = []
        max_m_count = (np.amax(muon_nr))
        alpha = np.divide(muon_nr, max_m_count)
        alpha = (min_alpha + alpha)/(1 + min_alpha)
        avg_fz_deg = np.rad2deg(avg_fz_rad)
        std_fz_deg = np.rad2deg(std_fz_rad)
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
        y_p = np.subtract(avg_fz_deg, std_fz_deg)
        y_m = np.add(avg_fz_deg, std_fz_deg)
        plt.figure(figsize=(16, 9))
        plt.rcParams.update({'font.size': 15})
        for i in range(len(alpha) - 1):
            check = unix_time[i] <= 1432123200 and unix_time[i] >= 1420113600
            if not check:
                plt.plot(
                    [unix_time[i], unix_time[i + 1]], 
                    [avg_fz_deg[i], avg_fz_deg[i + 1]],
                    "k-",
                    linewidth=0.5,
                    alpha=alpha[i],
                    )
                plt.fill_between(
                    [unix_time[i], unix_time[i + 1]],
                    [y_m [i], y_m[i + 1]],
                    [y_p[i], y_p[i + 1]],
                    color="c",
                    alpha=alpha[i],
                    linewidth = 0.0
                    )
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
            1420113600, 1432123200, color='r',
            alpha=0.3, label='faulty electronics')
        axes = plt.gca()
        # axes.set_ylim([0.1, 0.275])
        plt.xlabel("unix time / s")
        plt.grid(alpha = 0.2, axis = "y" , color = "k")
        plt.ylabel("fuzz / deg")
        plt.legend(fancybox= True, loc='upper right')
        fig_name = "fuzziness_over_time.png"
        fig_path = os.path.join(plt_dir, fig_name)
        plt.savefig(fig_path, dpi = 120)


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
                if extraction == "response":
                    suffix = "rsp.muon.fuzz.jsonl"
                elif extraction == "stdev":
                    suffix = "stdev.muon.fuzz.jsonl"
                merged_nightwise = os.path.join(self.output_dir, detection)
                muon_fuzz = self.reduction(merged_nightwise, suffix)
                plot_outDir = os.path.join(
                    self.plot_dir, "Fuzz", detection, extraction)
                if not os.path.isdir(plot_outDir):
                    os.makedirs(plot_outDir)
                self.plot(muon_fuzz, plot_outDir)


    """ ############## Distribution analysis ################## """

    def collect_items(self, method_dir):
        wild_card_path = os.path.join(method_dir, "*", "*", "*", "*.csv")
        rs = []
        cxs = []
        cys = []
        for run in glob.glob(wild_card_path):
            df = pandas.read_csv(run)
            r = np.rad2deg(df["cx"])
            cx = np.rad2deg(df["cy"])
            cy = np.rad2deg(df["r"])
            rs.extend(r)
            cxs.extend(cx)
            cys.extend(cy)
        return cxs, cys, rs


    def plot_distribution(self, cxs, cys, rs, plot_out):
        observables = [cxs, cys, rs]
        names = ["cx", "cy", "opening angle"]
        for name, observable in zip(names, observables):
            bin_count = np.sqrt(len(observable))
            bin_count = int(round(bin_count, 0))
            if bin_count < 100 and bin_count != 0:
                bin_count = bin_count
            else:
                bin_count = 100
            plt.hist(observable, histtype='step', color='k', bins=bin_count)
            plt.xlabel(name +" /deg")
            plt.ylabel("muon count /1")
            figname = str(name) + "_histogram_real.png"
            plotPath = os.path.join(plot_out, figname)
            plt.savefig(plotPath)
            plt.close("all")


    def compare_rs(self, hough_rs, ringM_rs, plot_out):
        bin_count = np.sqrt(len(hough_rs))
        bin_count = int(round(bin_count, 0))
        plt.hist(
            hough_rs, alpha=0.5, bins=250,
            label="Hough", density=True, stacked=True)
        plt.hist(
            ringM_rs, alpha=0.5, bins=bin_count,
            label="ringModel", density=True, stacked=True)
        plt.xlabel("opening angle /deg")
        plt.ylabel("muon count /1")
        plt.legend(loc="upper right")
        plt.savefig(plot_out + "/radius_comparison_real.png")
        plt.close("all")


    def distribution_main(self):
        hough_dir = os.path.join(self.output_dir, "hough")
        ringM_dir = os.path.join(self.output_dir, "ringM")
        plot_out = os.path.join(self.plot_dir, "Distributions")
        if not os.path.isdir(plot_out):
            os.makedirs(plot_out)
        hough_cxs, hough_cys, hough_rs = self.collect_items(hough_dir)
        hough_plotOut = os.path.join(plot_out, "Hough")
        hough_plotOut = os.path.normpath(hough_plotOut)
        if not os.path.isdir(hough_plotOut):
            os.makedirs(hough_plotOut)
        self.plot_distribution(hough_cxs, hough_cys, hough_rs, hough_plotOut)
        ringM_cx, ringM_cy, ringM_rs = self.collect_items(ringM_dir)
        ringM_plotOut = os.path.join(plot_out, "ringM")
        ringM_plotOut = os.path.normpath(ringM_plotOut)
        if not os.path.isdir(ringM_plotOut):
            os.makedirs(ringM_plotOut)
        self.plot_distribution(ringM_cx, ringM_cy, ringM_rs, ringM_plotOut)
        self.compare_rs(hough_rs, ringM_rs, plot_out)


    """ ################## Analysis main ################## """

    def do_whole_analysis(self):
        self.run_scoop_analysis()
        self.fuzz_plotting()
        self.distribution_main()