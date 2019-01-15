"""
Plot fuzziness vs point spread function
and effective area vs point spread function.

Call with 'python'

Usage:
    plot_psf_fuzz.py --psf_fuzz_csv_path=DIR --plot_dir=DIR --preferences_filePath=DIR [--fuzz_parameter=NME] [--do_comparison=BOOL] [--ringM_psf_fuzz_csv_path=DIR] [--hough_psf_fuzz_csv_path=DIR]

Options:
    --psf_fuzz_csv_path=DIR                  Path to the psf_fuzz csv file
    --plot_dir=DIR                           Path to the result of muon feature extraction
    --preferences_filePath=DIR               Path to simulation preferences file
    --fuzz_parameter=NME                     [default: both] Parameter to use as measure of fuzziness (options: stdev, response or both)
    --do_comparison=BOOL                     [default: False] True if want to do comparison of different models
    --ringM_psf_fuzz_csv_path=DIR            [default: None] Path to the ringM fuzz_psf csv file
    --hough_psf_fuzz_csv_path=DIR            [default: None] Path to the hough fuzz_psf csv file
"""
import matplotlib.pyplot as plt
import pandas
import numpy as np
import docopt
import os


def plot_psf_fuzz(psf_fuzz_csv_path, plot_out, fuzz_parameter):
    psf_fuzz_df = pandas.read_csv(psf_fuzz_csv_path)
    fuzz = np.rad2deg(psf_fuzz_df["average_fuzz"])
    psf = np.rad2deg(psf_fuzz_df["point_spread_function"])
    std_fuzz = np.rad2deg(psf_fuzz_df["std_fuzz"])
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.errorbar(psf, fuzz, std_fuzz, fmt=".", color="k")
    ax.set_xlim(psf.min()-0.01, psf.max()+0.01)
    plt.grid()
    ax.set_xlabel("true point spread function /deg")
    if fuzz_parameter == "stdev":
        ax.set_ylabel("fuzziness /deg")
        ax.set_ylim(0.10,0.22)
        fig.savefig(plot_out + "/fuzz_vs_psf.png", bbox_inches="tight")
        plt.close("all")
    elif fuzz_parameter == "response":
        ax.set_ylabel("response /%")
        fig.savefig(plot_out + "/response_vs_psf.png", bbox_inches="tight")
        plt.close("all")


def plot_absolute_detected_muons(
    simulated_muonCount,
    detected_muonCount,
    psf,
    plot_out
):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.set_xlabel("true point spread function /deg")
    ax.set_ylabel("number of muons /1")
    ax.set_xlim(psf.min()-0.01, psf.max()+0.01)
    ax.axhline(
        simulated_muonCount, color="red", label="number of simulated muons")
    ax.errorbar(
        psf, detected_muonCount, fmt=".",
        yerr=np.sqrt(detected_muonCount),
        label="number of detected muons")
    plt.legend(loc="upper right")
    ax.set_yscale('log')
    plt.grid()
    plt.savefig(plot_out+"/absolute_detected_muons.png", bbox_inches="tight")
    plt.close("all")


def plot_psf_fuzz_hough_ringM_comparison(
    ringM_psf_fuzz_csv_path, hough_psf_fuzz_csv_path
):
    ring_df = pandas.read_csv(ringM_psf_fuzz_csv_path)
    hough_df = pandas.read_csv(hough_psf_fuzz_csv_path)

    fuzz_ringM = np.rad2deg(ring_df["average_fuzz"])
    psf_ringM = np.rad2deg(ring_df["point_spread_function"])
    std_fuzz_ringM = np.rad2deg(ring_df["std_fuzz"])

    fuzz_hough = np.rad2deg(hough_df["average_fuzz"])
    psf_hough = np.rad2deg(hough_df["point_spread_function"])
    std_fuzz_hough = np.rad2deg(hough_df["std_fuzz"])

    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.errorbar(
        psf_hough, fuzz_hough, std_fuzz_hough,
        fmt=".", alpha=0.4, label="Hough")
    ax.errorbar(
        psf_ringM, fuzz_ringM, std_fuzz_ringM,
        fmt=".", alpha=0.4, label="ringModel")
    ax.set_xlabel("true point spread function /deg")
    ax.set_ylabel("fuzziness /deg")
    ax.set_xlim(psf_ringM.min()-0.01, psf_ringM.max()+0.01)
    ax.set_ylim(0.10,0.22)
    plt.legend(loc="upper right")
    plt.grid()
    plt.savefig(
        plot_out+"/hough_ring_psf_fuzz_comparison.png",
        bbox_inches="tight")
    plt.close("all")


def plot_effective_area_vs_psf(
    psf_fuzz_csv_path,
    plot_out,
    preferences_file_path
):
    psf_fuzz_df = pandas.read_csv(psf_fuzz_csv_path)
    simTruth_df = pandas.read_csv(preferences_filePath)
    preferences_dataFrame = pandas.read_csv(
        preferences_file_path, delimiter=" ", header=None)
    simulated_muonCount = int(preferences_dataFrame[1][1])
    detected_muonCount = np.array(psf_fuzz_df.detected_muonCount)
    psf = np.rad2deg(psf_fuzz_df["point_spread_function"])
    aperture_radius = float(preferences_dataFrame[1][3])
    area = np.pi * np.square(aperture_radius)
    effective_area = np.divide(detected_muonCount, simulated_muonCount) * area
    plot_absolute_detected_muons(
        simulated_muonCount, detected_muonCount, psf, plot_out)
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.errorbar(psf, effective_area, xerr=0.001, fmt=".", color="k")
    ax.set_yscale('log')
    ax.set_xlabel("true point spread function /deg")
    ax.set_ylabel("effective area /m**2")
    ax.set_xlim(psf.min()-0.01, psf.max()+0.01)
    plt.grid()
    fig.savefig(plot_out + "/effective_area_vs_psf.png", bbox_inches="tight")
    plt.close("all")


try:
    arguments = docopt.docopt(__doc__)
    ringM_psf_fuzz_csv_path = arguments['--ringM_psf_fuzz_csv_path']
    hough_psf_fuzz_csv_path = arguments['--hough_psf_fuzz_csv_path']
    fuzz_parameter = arguments['--fuzz_parameter']
    psf_fuzz_csv_path = arguments['--psf_fuzz_csv_path']
    do_comparison = arguments['--do_comparison']
    plot_dir = arguments['--plot_dir']
    psf_fuzz_csv_path_std = os.path.join(
        psf_fuzz_csv_path, "std_psf.csv")
    psf_fuzz_csv_path_amplitude = os.path.join(
        psf_fuzz_csv_path, "amplitude_psf_csv")
    plot_out = os.path.join(plot_dir, "plots_psf_fuzz_effective_area")
    if not os.path.isdir(plot_out):
        os.makedirs(plot_out)
    preferences_filePath = arguments['--preferences_filePath']
    if fuzz_parameter == "both":
        plot_psf_fuzz(psf_fuzz_csv_path_std, plot_out, "stdev")
        plot_psf_fuzz(psf_fuzz_csv_path_amplitude, plot_out, "response")
    else:
        plot_psf_fuzz(psf_fuzz_csv_path, plot_out, fuzz_parameter)
    plot_effective_area_vs_psf(psf_fuzz_csv_path, plot_out, preferences_filePath)
    if do_comparison=="True":
        plot_psf_fuzz_hough_ringM_comparison(
            ringM_psf_fuzz_csv_path, hough_psf_fuzz_csv_path
        )
except docopt.DocoptExit as e:
    print(e)
