"""
Simulate muon rings
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: scoop_simulate_muon_rings.py --outpath=DIR --number_of_muons=NBR --max_inclination=ANGL --max_aperture_radius=RDS --opening_angle=ANGL [--nsb_rate_per_pixel=NBR] [--arrival_time_std=STD] [--ch_rate=CHR] [--fact_aperture_radius=RDS]

Options:
    --outpath=DIR               The output path for simulations
    --number_of_muons=NBR       Number of muons to be simulated
    --max_inclination=ANGL      Maximum inclination angle of muon direction vector in deg
    --max_aperture_radius=RDS   Maximum aperture radius of muon support vector in m
    --opening_angle=ANGL        Opening angle of the Cherenkov cone in deg
    --nsb_rate_per_pixel=NBR    [default: 35e6] Nightsky background photon rate per pixel
    --arrival_time_std=STD      [default: 500e-12] Standard deviation of the arrival times of photons
    --ch_rate=CHR               [default: 3.0] Rate of Cherenkov photons to be generated per meter
    --fact_aperture_radius=RDS  [default: 1.965] Aperture radius of FACT telescope in m
"""
import docopt
import scoop
import muons


def main():
    try:
        arguments = docopt.docopt(__doc__)
        jobs = muons.muon_ring_simulation.many_simulations.create_jobs(
            outpath=arguments['--outpath'],
            number_of_muons=int(arguments['--number_of_muons']),
            max_inclination=float(arguments['--max_inclination']),
            max_aperture_radius=float(arguments['--max_aperture_radius']),
            opening_angle=float(arguments['--opening_angle']),
            nsb_rate_per_pixel=float(arguments['--nsb_rate_per_pixel']),
            arrival_time_std=float(arguments['--arrival_time_std']),
            ch_rate=float(arguments['--ch_rate']),
            fact_aperture_radius=float(arguments['--fact_aperture_radius'])
        )
        job_return_codes = list(scoop.futures.map(
            muons.muon_ring_simulation.many_simulations.run_job,
            jobs))
    except docopt.DocoptExit as e:
        print(e)


if __name__ == "__main__":
    main()
