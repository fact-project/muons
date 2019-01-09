"""
Muon ring fuzziness
Call with 'python'

Usage: merge_fuzz_and_plot_nightwise.py --merged_nightwise=DIR --plot_directory=DIR --path_to_epoch_file=PTH [--min_alpha=FLT]

Options:
    --merged_nightwise=DIR      Directory of merged nightwise fuzziness
    --plot_directory=DIR        Directory of the outputted plot
    --path_to_epoch_file=PTH    Path to the epoch file
    --min_alpha=FLT             [default: 0.1] Minimum transparency for plotting

"""

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
import json
import fact
import time
from datetime import datetime
import docopt
import csv


# write an array of data
def reduce_unsorted(muon_fuzz_dir):
    nights = []
    runs = []
    average_fuzzs = []
    std_fuzzs = []
    number_muons = []
    wCardPath = os.path.join(muon_fuzz_dir, "*", "*", "*", "*")
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
def reduction(muon_fuzz_dir):
    unsorted_runs = reduce_unsorted(muon_fuzz_dir)
    df = pd.DataFrame(unsorted_runs)
    return df.sort_values(by=["fNight", "fRunID"])


# average over nights
def night_wise(muon_fuzz):
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
def plot(muon_fuzz, plt_dir, path_to_epoch_file, min_alpha):
    avg_fz_rad, std_fz_rad, night, muon_nr = night_wise(muon_fuzz)
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
    plt.rcParams.update({'font.size': 15})
    plt.figure(figsize=(16, 9))
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
    dict_list = read_epoch_file(path_to_epoch_file)
    for preference in dict_list:
        x = preference["x"]
        linestyle = preference["linestyle"]
        color = preference["color"]
        linewidth = preference["linewidth"]
        comment = preference["comment"]
        plot_epoch(x, linestyle, color, linewidth, comment)
    plt.axvspan(1420113600, 1432123200, color='r', alpha=0.3, label='faulty electronics')
    axes = plt.gca()
    axes.set_ylim([0.1, 0.275])
    plt.xlabel("unix time / s")
    plt.grid(alpha = 0.2, axis = "y" , color = "k")
    plt.ylabel("fuzz / deg")
    plt.legend(fancybox= True)
    plt.savefig(plt_dir + "/fuzziness_over_time.png", dpi = 120)


def plot_epoch(x, linestyle, color, linewidth, comment):
    plt.axvline(
        x=x,
        linestyle=linestyle,
        color=color,
        linewidth=linewidth,
        label = comment)


def read_epoch_file(path_to_epoch_file):
    with open(path_to_epoch_file, "r") as csvin:
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


if __name__ == '__main__':
    try:
        arguments = docopt.docopt(__doc__)
        merged_nightwise = arguments["--merged_nightwise"]
        plt_dir = arguments["--plot_directory"]
        min_alpha = float(arguments["--min_alpha"])
        path_to_epoch_file = arguments["--path_to_epoch_file"]
        muon_fuzz = reduction(merged_nightwise)
        plot(muon_fuzz, plt_dir, path_to_epoch_file, min_alpha)
    except docopt.DocoptExit as e:
        print(e)
