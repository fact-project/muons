"""
Simulate muon rings
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: scoop_simulate_muon_rings.py --output_dir=DIR --number_of_muons=NBR --max_inclination=ANGL --max_aperture_radius=RDS [--min_opening_angle=ANGL] [--max_opening_angle=ANGL] [--nsb_rate_per_pixel=NBR] [--arrival_time_std=STD] [--ch_rate=CHR] [--fact_aperture_radius=RDS] [--random_seed=INT] [--point_spread_function_std=FLT] [--test_detection=BOOL]

Options:
    --output_dir=DIR                   The output directory for simulations
    --number_of_muons=NBR              Number of muons to be simulated
    --max_inclination=ANGL             Maximum inclination angle of muon direction vector in deg
    --max_aperture_radius=RDS          Maximum aperture radius of muon support vector in m
    --min_opening_angle=ANGL           [default: 0.4] Minimum opening angle of the Cherenkov cone in deg
    --max_opening_angle=ANGL           [default: 1.6] Maximum opening angle of the Cherenkov cone in deg
    --nsb_rate_per_pixel=NBR           [default: 35e6] Nightsky background photon rate per pixel
    --arrival_time_std=STD             [default: 500e-12] Standard deviation of the arrival times of photons
    --ch_rate=CHR                      [default: 3.0] Rate of Cherenkov photons to be generated per meter
    --fact_aperture_radius=RDS         [default: 1.965] Aperture radius of FACT telescope in m
    --random_seed=INT                  [default: 1] Random seed
    --point_spread_function_std=FLT    [default: 0] Standard deviation of the point spread function
    --test_detection=BOOL              [default:False] For checking the efficiency of cherenkov photon detection
"""
import docopt
import scoop
import muons
import photon_stream as ps
import numpy as np
import os



def main():
    try:
        arguments = docopt.docopt(__doc__)
        rndm_seed = int(arguments['--random_seed'])
        test_detection = arguments['--test_detection']
        np.random.seed(seed=rndm_seed)
        jobs = muons.analysis_utensils.detectionTesting_muon_simulation.many_simulations.create_jobs(
            number_of_muons=int(
                arguments['--number_of_muons']),
            max_inclination=float(
                arguments['--max_inclination']),
            max_aperture_radius=float(
                arguments['--max_aperture_radius']),
            min_opening_angle=np.deg2rad(float(
                arguments['--min_opening_angle'])),
            max_opening_angle=np.deg2rad(float(
                arguments['--max_opening_angle'])),
            nsb_rate_per_pixel=float(
                arguments['--nsb_rate_per_pixel']),
            arrival_time_std=float(
                arguments['--arrival_time_std']),
            ch_rate=float(
                arguments['--ch_rate']),
            fact_aperture_radius=float(
                arguments['--fact_aperture_radius']),
            random_seed=rndm_seed,
            point_spread_function_std=np.deg2rad(float(
                arguments['--point_spread_function_std'])
        ))
        events = list(
            scoop.futures.map(
                muons.analysis_utensils.detectionTesting_muon_simulation.many_simulations.run_job,
                jobs
            )
        )
        pure_events = [event.get("pure_event") for event in events]
        nsb_events = [event.get("nsb_event") for event in events]
        output_dir = arguments["--output_dir"]
        if test_detection:
            save_file(
                os.path.join(output_dir, "pure"), arguments, pure_events, jobs)
            save_file(
                os.path.join(output_dir, "NSB"), arguments, nsb_events, jobs)
        else:
            save_file(
                os.path.join(output_dir), arguments, nsb_events, jobs)
    except docopt.DocoptExit as e:
        print(e)


def save_file(output_dir, arguments, events, jobs):
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    simTruthFilename = "".join([
        "psf_",
        arguments["--point_spread_function_std"],
        ".simulationtruth.csv"]
    )
    simTruthPath = os.path.join(output_dir, simTruthFilename)
    muons.analysis_utensils.detectionTesting_muon_simulation.many_simulations.write_to_csv(
        simTruthPath+".temp",
        jobs
    )
    simulationFileName = "".join([
        "psf_",
        arguments["--point_spread_function_std"],
        ".sim.phs"
    ])
    simulationPath = os.path.join(output_dir, simulationFileName)
    with open(simulationPath + ".temp", "wb") as fout:
        for event in events:
            ps.io.binary.append_event_to_file(event, fout)
    os.rename(simTruthPath + ".temp", simTruthPath)
    os.rename(simulationPath + ".temp", simulationPath)

if __name__ == "__main__":
    main()
