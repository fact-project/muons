#!/usr/bin/python
"""
Comparison of PSF and fuzziness
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: compare_psf_fuzz.py --simulation_dir=DIR --output_dir=DIR --filename=NME

Options:
    --simulation_dir=DIR    Directory of the simulations
    --output_dir=DIR        Directory for the output file
    --filename=NME          Name of the output file
"""

import docopt
import scoop
from muons.muon_ring_fuzzyness import muon_ring_fuzzyness as mrf
from muons import extraction
import os
import photon_stream as ps
import pandas
import glob
import numpy as np
np.warnings.filterwarnings('ignore')


def paths(simulation_dir, suffix="**/psf*.sim.phs"):
    paths = []
    wild_card_path = os.path.join(simulation_dir, suffix)
    for path in glob.glob(wild_card_path, recursive=True):
        paths.append(path)
    return paths


def run_fuzz_job(inpath):
    results = []
    run = ps.EventListReader(inpath)
    number_muons = 0
    mu_event_ids = []
    for i, event in enumerate(run):
        clusters = ps.PhotonStreamCluster(event.photon_stream)
        random_state = np.random.get_state()
        np.random.seed(event.photon_stream.number_photons)
        muon_props = extraction.detection(event, clusters)
        np.random.set_state(random_state)
        if muon_props["is_muon"]:
            event_id = i
            std_photons_on_ring = mrf.muon_ring_std_event(
                clusters, muon_props)
            results.append(std_photons_on_ring)
            number_muons += 1
            mu_event_ids.append(event_id)
    average_fuzz = float(np.average(results))
    std_fuzz = float(np.std(results))
    return average_fuzz, std_fuzz, number_muons, mu_event_ids


def get_simTruth(simTruthPath, mu_event_ids):
    simulation_truth = pandas.read_csv(simTruthPath)
    point_spread_function = simulation_truth["point_spread_function_std"][0]
    return point_spread_function


def with_one_PSF(inpath):
    splitInpath = inpath.split(".")
    fileName_noSuffix = ".".join([splitInpath[0], splitInpath[1]])
    simTruthPath = "".join([fileName_noSuffix, ".simulationtruth.csv"])
    average_fuzz, std_fuzz, detected_muonCount, mu_event_ids = (
        run_fuzz_job(inpath)
    )
    try:
        point_spread_function = get_simTruth(simTruthPath, mu_event_ids)
    except IndexError:
        point_spread_function = np.nan
    event_info = [
        point_spread_function,
        average_fuzz, std_fuzz, detected_muonCount
    ]
    return event_info


def main():
    try:
        arguments = docopt.docopt(__doc__)
        simulation_dir = arguments['--simulation_dir']
        output_dir = arguments['--output_dir']
        filename = arguments['--filename']
        jobs = paths(simulation_dir)
        events = list(scoop.futures.map(
            with_one_PSF,
            jobs
        )
        )
        header_list = list([
            "point_spread_function",
            "average_fuzz",
            "std_fuzz",
            "detected_muonCount"
        ])
        headers = ",".join(header_list)
        events = sorted(events)
        file_out = os.path.join(output_dir, filename)
        np.savetxt(
            file_out,
            events,
            delimiter=",",
            comments='',
            header=headers
        )
    except docopt.DocoptExit as e:
        print(e)


if __name__ == "__main__":
    main()
