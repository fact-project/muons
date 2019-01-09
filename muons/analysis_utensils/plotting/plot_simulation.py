"""
Plot simulated muon events and compare them to reconstructed ones
Call with 'python'

Usage:
    plot_simulation.py --extracted_muons_path=DIR --simTruthPath=DIR --plot_dir=DIR

Options:
    --extracted_muons_path=DIR  Path to the result of muon feature extraction
    --simTruthPath=DIR          Path to simulation truth file
    --plot_dir=DIR              Directory of output plot files
"""

import pandas
import matplotlib.pyplot as plt
import numpy as np
import docopt
import os
import sys
import csv


def create_bins(input_data, bins=100):
    bin_edges = np.histogram_bin_edges(input_data, bins=100)
    return bin_edges


def read_dataframes(
    path_to_simulation_truth,
    path_to_extracted_muons
):
    simulation_truth = pandas.read_csv(path_to_simulation_truth)
    extracted_muons = pandas.read_csv(path_to_extracted_muons)
    return simulation_truth, extracted_muons


def choose_muon_events(extracted_muons):
    mu_events = extracted_muons["event_id"]
    muevents = pandas.to_numeric(mu_events, downcast='signed')
    return muevents


def create_axis(ax_start=0.1, ax_end=0.8):
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_axes([ax_start, ax_start, ax_end, ax_end])
    return fig, ax


def create_step_histogram(data, color, bin_edges, type):
    plt.hist(
        data, label=str(type) + " muons", histtype="step",
        bins=bin_edges, alpha=1, color=color
    )


def plot_impact_radii(
    simulation_truth,
    extracted_muons,
    plot_out
):
    muevents = choose_muon_events(extracted_muons)
    oa_extracted = extracted_muons["muon_ring_r"]
    # detected muons
    x_detected = simulation_truth.loc[muevents, "muon_support_ground0"]
    y_detected = simulation_truth.loc[muevents, "muon_support_ground1"]
    oa_detected = simulation_truth.loc[muevents, "opening_angle"]
    r_d_sq = np.square(x_detected) + np.square(y_detected)
    # thrown muons
    x_thrown = simulation_truth["muon_support_ground0"]
    y_thrown = simulation_truth["muon_support_ground1"]
    r_t_sq = np.square(x_thrown) + np.square(y_thrown)
    plot_gauss_for_R_width(oa_detected, oa_extracted, plot_out)
    plot_impact_r_sq(r_t_sq, r_d_sq, plot_out)


def plot_impact_r_sq(
    r_t_sq,
    r_d_sq,
    plot_out
):
    bin_edges = create_bins(r_t_sq)
    create_step_histogram(r_t_sq, "blue", bin_edges, "thrown")
    create_step_histogram(r_d_sq, "red", bin_edges, "detected")
    plt.legend(loc="upper right")
    plt.xlabel("muon impact radius / m**2")
    plt.ylabel("number of muons / 1")
    plt.savefig(plot_out + "/impact_r_sq.png", bbox_inches="tight")
    plt.close("all")


def compare_thrown_muon_direction_with_detected(
    simulation_truth,
    extracted_muons,
    plot_out
):
    muevents = choose_muon_events(extracted_muons)
    thrown_cx = simulation_truth["casual_muon_direction0"]
    thrown_cy = simulation_truth["casual_muon_direction1"]
    thrown_r_sq = np.square(thrown_cx) + np.square(thrown_cy)
# true_detected
    detected_mu_cx = simulation_truth.loc[muevents, "casual_muon_direction0"]
    detected_mu_cy = simulation_truth.loc[muevents, "casual_muon_direction1"]
# reconstructed_detected
    reconstructed_cx = extracted_muons["muon_ring_cx"]
    reconstructed_cy = extracted_muons["muon_ring_cy"]
    detected_r_sq = np.square(detected_mu_cx) + np.square(detected_mu_cy)
    plot_cxcy_squared(thrown_r_sq, detected_r_sq, plot_out)
    plot_cx_reconstructed_and_thrown(
        detected_mu_cx, reconstructed_cx, plot_out)
    plot_cy_reconstructed_and_thrown(
        detected_mu_cy, reconstructed_cy, plot_out)
#    plot_gauss_for_cx_width(detected_mu_cx, reconstructed_cx, plot_out)
#    plot_gauss_for_cy_width(detected_mu_cy, reconstructed_cy, plot_out)


def add_matrix_to_ax(
    matrix, bin_edges_axis0, bin_edges_axis1, ax
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


def plot_cx_reconstructed_and_thrown(
    thrown_cx,
    reconstructed_cx,
    plot_out
):
    bin_edges = np.linspace(-4.5, 4.5, num=100)
    bin_counts = np.histogram2d(
        np.rad2deg(reconstructed_cx),
        np.rad2deg(thrown_cx),
        bins=[bin_edges, bin_edges])[0]
    fig_cx, ax_cx = create_axis()
    im = add_matrix_to_ax(
        matrix=bin_counts,
        bin_edges_axis0=bin_edges,
        bin_edges_axis1=bin_edges,
        ax=ax_cx)
    fig_cx.colorbar(im, ax=ax_cx)
    ax_cx.set_xlabel("reconstructed muons cx /deg")
    ax_cx.set_ylabel("true muons cx /deg")
    fig_cx.savefig(plot_out + "/confusionMatrix_cx.png", bbox_inches="tight")
    plt.close("all")


def plot_cy_reconstructed_and_thrown(
    thrown_cy,
    reconstructed_cy,
    plot_out
):
    bin_edges = np.linspace(-4.5, 4.5, num=100)
    bin_counts = np.histogram2d(
        np.rad2deg(reconstructed_cy),
        np.rad2deg(thrown_cy),
        bins=[bin_edges, bin_edges])[0]
    fig_cy, ax_cy = create_axis()
    im = add_matrix_to_ax(
        matrix=bin_counts,
        bin_edges_axis0=bin_edges,
        bin_edges_axis1=bin_edges,
        ax=ax_cy)
    fig_cy.colorbar(im, ax=ax_cy)
    ax_cy.set_xlabel("reconstructed muons cy /deg")
    ax_cy.set_ylabel("true muons cy /deg")
    fig_cy.savefig(plot_out + "/confusionMatrix_cy.png", bbox_inches="tight")
    plt.close("all")


def plot_cxcy_squared(
    thrown_r_sq,
    detected_r_sq,
    plot_out
):
    bin_edges = np.rad2deg(create_bins(thrown_r_sq))
    create_step_histogram(
        np.rad2deg(thrown_r_sq), "blue", bin_edges, "thrown")
    create_step_histogram(
        np.rad2deg(detected_r_sq), "red", bin_edges, "detected")
    plt.legend(loc="upper right")
    plt.xlabel("muon cx**2 + cy**2 /deg**2")
    plt.ylabel("number of muons / 1")
    plt.savefig(plot_out + "/cxcy_squared.png", bbox_inches="tight")
    plt.close("all")


def confusionMatrix_opening_angle(
    simulation_truth,
    extracted_muons,
    plot_out
):
    muevents = choose_muon_events(extracted_muons)
    thrown_opening_angle = np.rad2deg(
        simulation_truth.loc[muevents, "opening_angle"])
    reconstructed_opening_angle = np.rad2deg(extracted_muons["muon_ring_r"])
    bin_edges = np.linspace(0, 1.8, num=100)
    bin_counts = np.histogram2d(
        reconstructed_opening_angle, thrown_opening_angle, bins=[
            bin_edges, bin_edges])[0]
    fig_oa, ax_oa = create_axis()
    im = add_matrix_to_ax(
        matrix=bin_counts,
        bin_edges_axis0=bin_edges,
        bin_edges_axis1=bin_edges,
        ax=ax_oa)
    fig_oa.colorbar(im, ax=ax_oa)
    ax_oa.set_xlabel("reconstructed muons oa /deg")
    ax_oa.set_ylabel("true muons oa /deg")
    fig_oa.savefig(plot_out + "/confusionMatrix_oa.png", bbox_inches="tight")
    plt.close("all")


def compare_thrown_muon_opening_angle_with_detected(
    simulation_truth,
    extracted_muons,
    plot_out
):
    thrown_opening_angle = simulation_truth["opening_angle"]
    detected_opening_angle = extracted_muons["muon_ring_r"]
    bin_edges = create_bins(thrown_opening_angle)
    create_step_histogram(
        np.rad2deg(detected_opening_angle),
        "red", np.rad2deg(bin_edges), "reconstructed")
    create_step_histogram(
        np.rad2deg(thrown_opening_angle),
        "blue", np.rad2deg(bin_edges), "true")
    plt.legend(loc="upper right")
    plt.xlabel("muon Cherenkov cone opening angle /deg")
    plt.ylabel("number of muons / 1")
    plt.savefig(plot_out + "/opening_angle.png", bbox_inches="tight")
    plt.close("all")



def plot_gauss_for_R_width(
    oa_detected,
    oa_extracted,
    plot_out
):
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
    plt.savefig(plot_out + "/r_difference_gauss.png", bbox_inches="tight")
    plt.close("all")



def main(extracted_muons_path, simtruthpath, plot_out):
    simulation_truth, extracted_muons = read_dataframes(
        simtruthpath,
        extracted_muons_path
    )
    plot_impact_radii(
        simulation_truth,
        extracted_muons,
        plot_out
    )
    compare_thrown_muon_direction_with_detected(
        simulation_truth,
        extracted_muons,
        plot_out
    )
    compare_thrown_muon_opening_angle_with_detected(
        simulation_truth,
        extracted_muons,
        plot_out
    )
    confusionMatrix_opening_angle(
        simulation_truth,
        extracted_muons,
        plot_out
    )


try:
    arguments = docopt.docopt(__doc__)
    plot_dir = arguments['--plot_dir']
    plot_out = os.path.join(plot_dir, "plots_comparison")
    if not os.path.isdir(plot_out):
        os.mkdir(plot_out)
    input_file = open(arguments['--extracted_muons_path'], "r")
    reader_file = csv.reader(input_file)
    if len(list(reader_file)) < 2:
        sys.exit("No muons detected")
    main(
        simtruthpath=arguments['--simTruthPath'],
        extracted_muons_path=arguments['--extracted_muons_path'],
        plot_out=plot_out,
    )
except docopt.DocoptExit as e:
    print(e)
