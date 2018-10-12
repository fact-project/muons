"""
Simulate muon rings
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: simulate_muon_rings --outpath=DIR --number_of_muons=NBR --max_inclination=ANGL --max_aperture_radius=RDS --opening_angle=ANGL [--nsb_rate_per_pixel=NBR] [--arrival_time_std=STD] [--ch_rate=CHR] [--fact_aperture_radius=RDS]

Options:
    --outpath=DIR               The output path for simulations
    --number_of_muons=NBR       Number of muons to be simulated
    --max_inclination=ANGL      Maximum inclination angle of muon direction vector [deg]
    --max_aperture_radius=RDS   Maximum aperture radius of muon support vector [m]
    --opening_angle=ANGL        Opening angle of the Cherenkov cone [deg]
    --nsb_rate_per_pixel=NBR    Nightsky background photon rate per pixel
    --arrival_time_std=STD      Standard deviation of the arrival times of photons
    --ch_rate=CHR               Rate of Cherenkov photons to be generated [1/m]
    --fact_aperture_radius=RDS  Aperture radius of FACT telescope [m]
"""
import docopt
import scoop
import muons
import photon_stream as ps


def run(job):
    muons.muon_ring_simulation.many_simulations.run_job(job)


def main():
    try:
        arguments = docopt.docopt(__doc__)
        outpath = arguments['outpath']
        number_of_muons = arguments['number_of_muons']
        max_inclination = arguments['max_inclination']
        max_aperture_radius = arguments['max_aperture_radius']
        opening_angle = arguments['opening_angle']
        nsb_rate_per_pixel = arguments['nsb_rate_per_pixel']
        arrival_time_std = arguments['arrival_time_std']
        ch_rate = arguments['ch_rate']
        fact_aperture_radius = arguments['fact_aperture_radius']
        jobs = muons.muon_ring_simulation.many_simulations.create_jobs(
            outpath
            number_of_muons,
            max_inclination,
            max_aperture_radius,
            opening_angle
            nsb_rate_per_pixel=35e6,
            arrival_time_std=500e-12,
            ch_rate=3,
            fact_aperture_radius=3.93/2
        )
        job_return_codes = list(scoop.futures.map(run, jobs))
    except docopt.DocoptExit as e:
        print(e)


if __name__ == "__main__":
    main()
