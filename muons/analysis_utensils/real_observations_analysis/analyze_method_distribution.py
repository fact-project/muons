"""
Collect ring features from different run files and plot them for ringM and Hough
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: scoop_real_distributions.py --hough_dir=DIR --ringM_dir=DIR --plot_out=DIR

Options:
    --hough_dir=DIR      The location of muon data
    --ringM_dir=DIR      The output of caluculated fuzzyness
    --plot_out=DIR       Direcotry for plots
"""

import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas
import warnings
warnings.filterwarnings("ignore")

def collect_items(method_dir):
    wild_card_path = os.path.join(method_dir, "*.csv")
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


def plot_distribution(cxs, cys, rs, plot_out):
    observables = [cxs, cys, rs]
    names = ["cx", "cy", "opening_angle"]
    for name, observable in zip(names, observables):
        bin_count = np.sqrt(len(observable))
        bin_count = int(round(bin_count, 0))
        if bin_count < 100:
            bin_count = bin_count
        else:
            bin_count = 100
        plt.hist(observable, histtype='step', color='k', bins=bin_count)
        plt.xlabel(name +" /deg")
        plt.ylabel("muon_count /1")
        plt.savefig(plot_out + "/" + str(name) + "_histogram_real.png")
        plt.close("all")


def compare_rs(hough_rs, ringM_rs, plot_out):
    bin_count = np.sqrt(len(hough_rs))
    bin_count = int(round(bin_count, 0))
    plt.hist(hough_rs, alpha=0.5, bins=250, label="Hough", density=True, stacked=True)
    plt.hist(ringM_rs, alpha=0.5, bins=250, label="ringModel", density=True, stacked=True)
    plt.xlabel("opening_angle /deg")
    plt.ylabel("muon_count /1")
    plt.legend(loc="upper right")
    plt.savefig(plot_out + "/radius_comparison_real.png")
    plt.close("all")


def main(hough_dir, ringM_dir, plot_out):
    hough_cxs, hough_cys, hough_rs = collect_items(hough_dir)
    hough_plotOut = os.path.join(plot_out, "Hough")
    hough_plotOut = os.path.normpath(hough_plotOut)
    if not os.path.isdir(hough_plotOut):
        os.mkdir(hough_plotOut)
    plot_distribution(hough_cxs, hough_cys, hough_rs, hough_plotOut)
    ringM_cx, ringM_cy, ringM_rs = collect_items(ringM_dir)
    ringM_plotOut = os.path.join(plot_out, "ringM")
    ringM_plotOut = os.path.normpath(ringM_plotOut)
    if not os.path.isdir(ringM_plotOut):
        os.mkdir(ringM_plotOut)
    plot_distribution(ringM_cx, ringM_cy, ringM_rs, ringM_plotOut)
    compare_rs(hough_rs, ringM_rs, plot_out)


if __name__=='__main__':
    try:
        arguments = docopt.docopt(__doc__)
        hough_dir = arguments['--hough_dir']
        ringM_dir = arguments['--ringM_dir']
        plot_out = arguments['--plot_out']
        main(hough_dir, ringM_dir, plot_out)
    except docopt.DocoptExit as e:
        print(e)