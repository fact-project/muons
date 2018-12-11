"""
Comparison of PSF and fuzzinessand reeconstruction of muon events runwise
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: compare_psf_fuzz.py --simulation_dir=DIR --output_dir=DIR --number_of_muons=NBR

Options:
    --simulation_dir=DIR    Directory of the simulations
    --output_dir=DIR        Directory for the output file
    --number_of_muons=NBR   Number of muons simulated
"""

import docopt
import scoop
from muons.muon_ring_fuzzyness import muon_ring_fuzzyness as mrf
from muons.detection import detection
import os
import photon_stream as ps
import pandas
import glob
import numpy as np
import re
np.warnings.filterwarnings('ignore')


def paths(simulation_dir, suffix="**/psf*.sim.phs"):
    paths = []
    wild_card_path = os.path.join(simulation_dir, suffix)
    for path in glob.glob(wild_card_path, recursive=True):
        paths.append(path)
    return paths


def run_detection(inpath):
    run = ps.EventListReader(inpath)
    arguments = docopt.docopt(__doc__)
    path = os.path.normpath(inpath)
    split_path = path.split(os.sep)
    oa_name = split_path[5]
    oa = re.split('_',oa_name)[3]
    number_of_muons = arguments['--number_of_muons']
    found_muons = 0
    for event in run:
        clusters = ps.PhotonStreamCluster(event.photon_stream)
        muon_props = detection(event, clusters)
        if muon_props["is_muon"]:
            found_muons += 1
    return oa, found_muons, number_of_muons


def main():
    try:
        arguments = docopt.docopt(__doc__)
        simulation_dir = arguments['--simulation_dir']
        output_dir = arguments['--output_dir']
        filename = "effective_area_vs_oa.csv"
        jobs = paths(simulation_dir)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        events = list(scoop.futures.map(
            run_detection,
            jobs
        ))
        header_list = list([
            "opening_angle",
            "detected_muons",
            "simulated_muons"
        ])
        headers = ",".join(header_list)
        events = np.array(sorted(events), dtype='<U21')
        file_out = os.path.join(output_dir, filename)
        np.savetxt(
            file_out,
            events,
            delimiter=",",
            comments='',
            header=headers,
            fmt='%s'
        )
    except docopt.DocoptExit as e:
        print(e)


if __name__ == "__main__":
    main()