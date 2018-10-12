import numpy as np
import photon_stream as ps
import muons

def draw_position_on_aperture_plane(max_aperture_radius):
    theta = np.random.uniform(
        low=0,
        high=2 * np.pi)
    b = np.random.uniform(
        low=0,
        high=max_aperture_radius)
    return theta, b


def draw_inclination(low=0, high=np.pi/2, size=1):
    v_min = (np.cos(low)+1)/2
    v_max = (np.cos(high)+1)/2
    v = np.random.uniform(
        low=v_min,
        high=v_max,
        size=size)
    return np.arccos(2*v - 1)


def draw_azimuth(low=0, high=2*np.pi, size=1):
    return np.random.uniform(
        low=low,
        high=high,
        size=size)


def get_trajectory(max_inclination, max_aperture_radius):
    inclination = draw_inclination(high=max_inclination)
    azimuth = draw_azimuth()
    muon_direction = pol2cart(1, azimuth, inclination)
    theta, b = draw_position_on_aperture_plane(max_aperture_radius)
    muon_support = pol2cart(b, theta, 0.5*np.pi)
    return muon_support, muon_direction


def create_jobs(
    outpath
    number_of_muons,
    max_inclination,
    max_aperture_radius,
    opening_angle
    nsb_rate_per_pixel=35e6,
    arrival_time_std=500e-12,
    ch_rate=3,
    fact_aperture_radius=3.93/2
):
    jobs = []
    for event_id in range(number_of_muons):
        job = {}
        muon_support, muon_direction = get_trajectory(
            max_inclination,
            max_aperture_radius
        )
        job["muon_support"] = muon_support
        job["muon_direction"] = muon_direction
        job["event_id"] = event_id
        job["nsb_rate_per_pixel"] = nsb_rate_per_pixel
        job["ch_rate"] = ch_rate
        job["opening_angle"] = opening_angle
        job["fact_aperture_radius"] = fact_aperture_radius
        job["arrival_time_std"] = arrival_time_std
        job["outpath"] = outpath
        jobs.append(job)
    return jobs


def run_job(job):
    event = muons.muon_ring_simulation.simulate_response(
        muon_support=job["muon_support"],
        muon_direction=job["muon_direction"],
        opening_angle=job["opening_angle"],
        nsb_rate_per_pixel=job["nsb_rate_per_pixel"],
        event_id=["event_id"],
        arrival_time_std=["arrival_time_std"],
        ch_rate=["ch_rate"],
        fact_aperture_radius=["fact_aperture_radius"]
    )
    with open(outpath + str(event_id) + ".sim.phs", "ab") as fout:
        ps.io.binary.append_event_to_file(event, fout)
