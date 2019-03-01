"""
Simulate muon rings
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: scoop_simulation.py --output_dir=DIR --number_of_muons=NBR --max_inclination=ANGL --max_aperture_radius=RDS [--min_opening_angle=ANGL] [--max_opening_angle=ANGL] [--min_nsb_rate=INT] [--max_nsb_rate=INT] [--arrival_time_std=STD] [--ch_rate=CHR] [--fact_aperture_radius=RDS] [--random_seed=INT] [--point_spread_function_std=FLT]

Options:
    --output_dir=DIR                   The output directory for simulations
    --number_of_muons=NBR              Number of muons to be simulated
    --max_inclination=ANGL             Maximum inclination angle of muon direction vector in deg
    --max_aperture_radius=RDS          Maximum aperture radius of muon support vector in m
    --min_opening_angle=ANGL           [default: 0.4] Minimum opening angle of the Cherenkov cone in deg
    --max_opening_angle=ANGL           [default: 1.6] Maximum opening angle of the Cherenkov cone in deg
    --min_nsb_rate=INT                 [default: 28e6] Minimum nightsky backgrount to be simulated
    --max_nsb_rate=INT                 [default: 140e6] Maximum nightsky background photon rate per pixel
    --arrival_time_std=STD             [default: 500e-12] Standard deviation of the arrival times of photons
    --ch_rate=CHR                      [default: 3.0] Rate of Cherenkov photons to be generated per meter
    --fact_aperture_radius=RDS         [default: 1.965] Aperture radius of FACT telescope in m
    --random_seed=INT                  [default: 1] Random seed
    --point_spread_function_std=FLT    [default: 0] Standard deviation of the point spread function
"""
import docopt
import scoop
from muons.muon_ring_simulation import eventsDistribution as ed
import photon_stream as ps
import numpy as np
import os
import glob


def main():
    try:
        arguments = docopt.docopt(__doc__)
        rndm_seed = int(arguments['--random_seed'])
        np.random.seed(seed=rndm_seed)
        output_dir = arguments["--output_dir"]
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        jobs = ed.create_jobs(
            output_dir=output_dir,
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
            max_nsb_rate=float(
                arguments['--max_nsb_rate']),
            min_nsb_rate=float(
                arguments['--min_nsb_rate']),
            arrival_time_std=float(
                arguments['--arrival_time_std']),
            ch_rate=float(
                arguments['--ch_rate']),
            fact_aperture_radius=float(
                arguments['--fact_aperture_radius']),
            random_seed=rndm_seed,
            point_spread_function=np.deg2rad(float(
                arguments['--point_spread_function_std'])
        ))

        chunk_jobs = []
        NUM_EVENTS_IN_CHUNK = 1000
        chunk_index = 0
        jobs_in_chunk = []
        for i, job in enumerate(jobs):
            jobs_in_chunk.append(job)
            if (len(jobs_in_chunk) == NUM_EVENTS_IN_CHUNK) or i == len(jobs) - 1:
                chunk_job = {
                    "path": os.path.join(output_dir, "{:06d}.sim.phs.chunk".format(chunk_index)),
                    "jobs": jobs_in_chunk 
                }
                chunk_jobs.append(chunk_job)
                jobs_in_chunk = []
                chunk_index += 1

        return_codes = list(
            scoop.futures.map(ed.run_chunk_job, chunk_jobs)
        )
        with open(os.path.join(output_dir, "simulations.sim.phs"), "wb") as fOut:
            wild_card_path = os.path.join(output_dir, "*.sim.phs.chunk")
            for path in glob.glob(wild_card_path):
                with open(path, "rb") as fIn:
                    fOut.write(fIn.read())
                os.remove(path)
    except docopt.DocoptExit as e:
        print(e)


if __name__ == '__main__':
    main()