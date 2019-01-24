"""
Analyze effective area vs opening angle
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: scoop_simulate_muon_rings.py --simulation_dir=DIR --scoop_hosts=PTH --preferencesFile=PTH --steps=INT --output_dir=DIR

Options:
    --simulation_dir=DIR        Directory of the simulations
    --scoop_hosts=PTH           Path to scoop_hosts.txt
    --preferencesFile=PTH       Path to preferences_file.csv
    --steps=INT                 Number of different opening angles -1
    --output_dir=DIR            Directory of the output
"""
import sys
import numpy as np
import docopt
import os
filePath = os.path.normpath(os.path.abspath(__file__))
parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
scriptDir = os.path.normpath(os.path.join(parentDir, os.pardir))
sys.path.insert(0, scriptDir)
import effectiveArea_vs_openingAngle as evo

def run_all_jobs(
    simulation_dir,
    scoop_hosts,
    preferencesFile,
    steps,
    output_dir
):
    EvO = evo.EffectiveArea_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)

    filename = "effective_area_vs_oa.csv"
    jobs = EvO.create_jobs_for_scoop()
    events = list(scoop.futures.map(EvO.run_detection, jobs))
    header_list = list([
        "opening_angle",
        "detected_muons",
        "simulated_muons"
    ])
    headers = ",".join(header_list)
    events = np.array(sorted(events), dtype='<U21')
    file_out = os.path.join(simulation_dir, filename)
    np.savetxt(
        file_out,
        events,
        delimiter=",",
        comments='',
        header=headers,
        fmt='%s'
    )


if __name__ == '__main__':
    try:
        arguments = docopt.docopt(__doc__)
        simulation_dir = arguments['--simulation_dir']
        scoop_hosts = arguments['--scoop_hosts']
        preferencesFile = arguments['--preferencesFile']
        steps = int(arguments['--steps'])
        output_dir = arguments['--output_dir']
        run_all_jobs(
            simulation_dir,
            scoop_hosts,
            preferencesFile,
            steps,
            output_dir
        )
    except docopt.DocoptExit as e:
        print(e)