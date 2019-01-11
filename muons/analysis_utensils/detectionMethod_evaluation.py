"""
Call scoop for simulation muon rings for different point spread functions (PSF)
Call with 'python'

Usage: evaluate_detectionMethod.py --output_dir=DIR --number_of_muons=INT [--different_nsb=BOOL] [--steps=INT] [--step_size=INT]

Options:
    --output_dir=DIR            Directory of output
    --number_of_muons=INT       Number of muons to be simulated
    --different_nsb=BOOL        [default: False] Whether to do analysis with different NSB
    --steps=INT                 [default: 20] Number of steps to iterate with different NSB
    --step_size=INT             [default: 10] Step size

"""
import photon_stream as ps
import numpy as np
import os
import subprocess
import docopt
import pandas
from statistics import mean
import matplotlib.pyplot as plt
import glob


def start_simulation(simulation_dir, number_of_muons):
    scoopList = [
        "python", "-m", "scoop", "--hostfile",
        os.path.join(os.getcwd(),"muon_ring_simulation/scoop_hosts.txt"),
        os.path.join(
                os.getcwd(),
                "./muon_ring_simulation/scoop_simulate_muon_rings.py"),
        "--output_dir", str(simulation_dir), "--number_of_muons",
        str(number_of_muons), "--max_inclination", str(4.5),
        "--max_aperture_radius", str(4), "--test_detection", str(True)
    ]
    subprocess.call(scoopList)


def start_simulation2(simulation_dir, number_of_muons, nsb_rate):
    scoopList = [
        "python", "-m", "scoop", "--hostfile",
        os.path.join(os.getcwd(),"muon_ring_simulation/scoop_hosts.txt"),
        os.path.join(
                os.getcwd(),
                "./muon_ring_simulation/scoop_simulate_muon_rings.py"),
        "--output_dir", str(simulation_dir), "--number_of_muons",
        str(number_of_muons), "--max_inclination", str(4.5),
        "--max_aperture_radius", str(4), "--nsb_rate_per_pixel", str(nsb_rate),
        "--test_detection", str(True)
    ]
    subprocess.call(scoopList)


def read_runs(
    pure_cherenkov_events_path,
    events_with_nsb_path
):
    pure_cherenkov_run = ps.EventListReader(pure_cherenkov_events_path)
    nsb_run = ps.EventListReader(events_with_nsb_path)
    return pure_cherenkov_run, nsb_run


def do_clustering(
    pure_cherenkov_run,
    nsb_run
):
    nsb_run_found_photons = []
    pure_cherenkov_run_photons = []
    all_photons_run = []
    for event in nsb_run:
        photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
        cherenkov_cluster_mask = photon_clusters.labels >= 0
        nsb_cherenkov_photon_stream = photon_clusters.point_cloud
        nsb_cherenkov_ps = nsb_cherenkov_photon_stream[cherenkov_cluster_mask]
        nsb_run_found_photons.append(nsb_cherenkov_ps[:, 0:3])
        all_photons = event.photon_stream.point_cloud
        all_photons_run.append(all_photons)
    for muon in pure_cherenkov_run:
        pure_photon_stream = muon.photon_stream.point_cloud
        pure_cherenkov_run_photons.append(pure_photon_stream)
    return all_photons_run, pure_cherenkov_run_photons, nsb_run_found_photons


def true_false_decisions(
    number_of_events,
    all_photons_run,
    pure_cherenkov_run_photons,
    nsb_run_found_photons
):
    true_positives_list = []
    false_positives_list = []
    false_negatives_list = []
    true_negatives_list = []
    precisions = []
    sensitivities = []
    events = []
    for muon in range(number_of_events):
        true_positives = 0
        for photon in nsb_run_found_photons[muon]:
            true_positives = 0
            for pure_photon in pure_cherenkov_run_photons[muon]:
                if photon.all() == pure_photon.all():
                    true_positives += 1
        true_positives_list.append(true_positives)
        false_positives = (
            len(nsb_run_found_photons[muon])
            - true_positives_list[muon])
        false_positives_list.append(false_positives)
        false_negatives = (
            len(pure_cherenkov_run_photons[muon])
            - true_positives_list[muon])
        false_negatives_list.append(false_negatives)
        true_negatives = (
            len(all_photons_run[muon])
            - len(nsb_run_found_photons[muon]))
        try:
            true_negatives_list.append(true_negatives)
            precision = true_positives / (true_positives + false_positives)
            sensitivity = true_positives / (true_positives + false_negatives)
            precisions.append(precision)
            sensitivities.append(sensitivity)
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


def save_to_file(file_out, events):
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


def analyze(file_out):
    dataFrame = pandas.read_csv(file_out)
    non_zero = dataFrame.loc[dataFrame['precision']!=0]
    precisions = non_zero['precision']
    sensitivities = non_zero['sensitivity']
    avg_precision = mean(precisions)
    std_precision = np.std(precisions)
    avg_sensitivity = mean(sensitivities)
    std_sensitivity = np.std(sensitivities)
    return (
        avg_precision, std_precision, avg_sensitivity,
        std_sensitivity, precisions, sensitivities)


def plot_sensitivity_precision(
    avg_precision, std_precision,
    avg_sensitivity, std_sensitivity,
    precisions, sensitivities, output_dir
):
    event_nrs = list(range(len(sensitivities)))
    sens_max = avg_sensitivity + std_sensitivity
    sens_min = avg_sensitivity - std_sensitivity
    prec_max = avg_precision + std_precision
    prec_min = avg_precision - std_precision
    fig, ax = plt.subplots()
    prec = plt.scatter(event_nrs, precisions, s=0.5, color = 'red')
    avg_prec_line = plt.axhline(avg_precision, label="average_precision", color='k')
    fill2 = plt.fill_between(x=event_nrs, y1=prec_min, y2=prec_max, alpha=0.3, color='gray')
    plt.xlabel("event_id")
    plt.ylabel("persentage / %")
    plt.ylim([0, 100])
    plt.xlim([0, len(event_nrs)])
    fig.suptitle("Precision")
    plt.legend(fancybox= True, loc='lower right')
    plot_out = os.path.join(output_dir, "precision.png")
    plt.savefig(plot_out)
    plt.close("all")
    sens = plt.scatter(event_nrs, sensitivities, s=0.5, color = 'red')
    avg_sens_line = plt.axhline(avg_sensitivity, label="average_sensitivity", color='k')
    fill1 = plt.fill_between(x=event_nrs, y1=sens_min, y2=sens_max, alpha=0.3, color='gray')
    plt.xlabel("event_id")
    plt.ylabel("persentage / %")
    plt.ylim([0, 100])
    plt.xlim([0, len(event_nrs)])
    fig.suptitle("Sensitivity")
    plt.legend(fancybox= True, loc='lower right')
    plot_out = os.path.join(output_dir, "sensitivity.png")
    plt.savefig(plot_out)
    plt.close("all")


def main(
    output_dir, number_of_muons
):
    simulation_dir = os.path.join(output_dir, "simulation")
    if not os.path.isdir(simulation_dir):
        os.mkdir(simulation_dir)
    start_simulation(simulation_dir, number_of_muons)
    pure_cherenkov_events_path = os.path.join(simulation_dir, "pure", "psf_0.sim.phs")
    events_with_nsb_path = os.path.join(simulation_dir, "NSB", "psf_0.sim.phs")
    pure_cherenkov_run, nsb_run = read_runs(
        pure_cherenkov_events_path, events_with_nsb_path)
    all_photons_run, pure_cherenkov_run_photons, nsb_run_found_photons = do_clustering(
        pure_cherenkov_run, nsb_run)
    events = true_false_decisions(
        number_of_muons, all_photons_run, pure_cherenkov_run_photons, nsb_run_found_photons)
    file_out = os.path.join(output_dir,"precision_results.csv")
    save_to_file(file_out, events)
    avg_precision, std_precision, avg_sensitivity, std_sensitivity, precisions, sensitivities = analyze(fle_out)
    plot_sensitivity_precision(
            avg_precision, std_precision, avg_sensitivity,
            std_sensitivity, precisions, sensitivities, output_dir)


def plot_different_NSB(plot_out, NSB_rates, precisions, sensitivities):
    fig, ax = plt.subplots()
    plt.scatter(NSB_rates, precisions, color = "k")
    plt.xlabel("NSB_rate /Hz/pixel")
    fig.suptitle("Precision")
    plt.ylabel("precision")
    plt.legend(fancybox= True, loc='lower right')
    plt.savefig(plot_out+"/NSB_precision.png")
    plt.close("all")
    fig, ax = plt.subplots()
    plt.scatter(NSB_rates, sensitivities, color = "k")
    plt.xlabel("NSB_rate /Hz/pixel")
    fig.suptitle("Sensitivity")
    plt.ylabel("sensitivity")
    plt.legend(fancybox= True, loc='lower right')
    plt.savefig(plot_out+"/NSB_sensitivity.png")
    plt.close("all")


def main2(
    output_dir,
    number_of_muons,
    steps,
    step_size,
    darkNight_NSB=35e6
):
    simulation_dir = os.path.join(output_dir, "simulation")
    precisions = []
    sensitivities = []
    NSB_rates = []
    for i in range(1, steps+1):
        NSB_rate = darkNight_NSB * i * step_size
        simulation_step_dir = os.path.join(simulation_dir, str("{:.2e}".format(NSB_rate)))
        if not os.path.isdir(simulation_step_dir):
            os.makedirs(simulation_step_dir)
        start_simulation2(simulation_step_dir, number_of_muons, NSB_rate)
    print("simulations done")
    wild_card_path = os.path.join(simulation_dir, "*")
    for simulation_step_dir in glob.glob(wild_card_path):
        pure_cherenkov_events_path = os.path.join(
            simulation_step_dir, "pure", "psf_0.sim.phs")
        events_with_nsb_path = os.path.join(
            simulation_step_dir, "NSB", "psf_0.sim.phs")
        pure_cherenkov_run, nsb_run = read_runs(
            pure_cherenkov_events_path, events_with_nsb_path)
        all_photons_run, pure_cherenkov_run_photons, nsb_run_found_photons = do_clustering(
            pure_cherenkov_run, nsb_run)
        events = true_false_decisions(
            number_of_muons, all_photons_run,
            pure_cherenkov_run_photons, nsb_run_found_photons)
        print("Run done")
        avg_precision = mean(events[6])
        avg_sensitivity = mean(events[7])
        NSB_rates.append(NSB_rate)
        precisions.append(avg_precision)
        sensitivities.append(avg_sensitivity)
    plot_different_NSB(plot_out, NSB_rates, precisions, sensitivities)
    save_to_file2(output_dir, NSB_rates, precisions, sensitivities)


def save_to_file2(file_out, NSB_rates, precisions, sensitivities):
    events = [NSB_rates, precisions, sensitivities]
    header = list([
        "NSB_rate",
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


if __name__ == "__main__":
    try:
        arguments = docopt.docopt(__doc__)
        number_of_muons = int(arguments['--number_of_muons'])
        output_dir = arguments['--output_dir']
        different_nsb = bool(arguments['--different_nsb'])
        steps = int(arguments['--steps'])
        step_size = int(arguments['--step_size'])
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        if different_nsb:
            main2(output_dir, number_of_muons, steps, step_size)
        else:
            main(output_dir, number_of_muons)
    except docopt.DocoptExit as e:
        print(e)