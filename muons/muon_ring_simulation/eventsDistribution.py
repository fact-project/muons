import numpy as np
from muons.muon_ring_simulation import single_simulation as rs
import os
from numbers import Number
import photon_stream as ps


def draw_position_on_aperture_plane(max_aperture_radius):
    theta = np.random.uniform(
        low=0,
        high=2 * np.pi)
    b = np.random.uniform(
        low=0,
        high=1)
    return theta, np.sqrt(b)*max_aperture_radius


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
    max_inclination = np.deg2rad(max_inclination)
    inclination = draw_inclination(high=max_inclination)
    azimuth = draw_azimuth()
    muon_direction_ground = rs.pol2cart(1, azimuth, inclination)
    theta, b = draw_position_on_aperture_plane(max_aperture_radius)
    muon_support_ground = rs.pol2cart(b, theta, 0.5*np.pi)
    return muon_support_ground, muon_direction_ground


def casual_trajectory(
    muon_support_ground,
    muon_direction_ground,
    muon_travel_dist=1000
):
    casual_muon_direction = -muon_direction_ground
    casual_muon_support = (
        muon_travel_dist*muon_direction_ground
        + muon_support_ground
    )
    return np.array(casual_muon_support), np.array(casual_muon_direction)


def nsb_rate(min_nsb_rate, max_nsb_rate):
    return np.random.uniform(
        low=min_nsb_rate,
        high=max_nsb_rate,
        size=1)


def create_jobs(
    output_dir,
    number_of_muons,
    max_inclination,
    max_aperture_radius,
    min_opening_angle,
    max_opening_angle,
    min_nsb_rate,
    max_nsb_rate,
    arrival_time_std=500e-12,
    ch_rate=3,
    fact_aperture_radius=1.965,
    random_seed=1,
    point_spread_function=0
):
    jobs = []
    for event_id in range(number_of_muons):
        job = {}
        opening_angle = np.random.uniform(min_opening_angle, max_opening_angle)
        muon_support_ground, muon_direction_ground = get_trajectory(
            max_inclination,
            max_aperture_radius
        )
        casual_muon_support, casual_muon_direction = casual_trajectory(
            muon_support_ground,
            muon_direction_ground
        )
        nsb_rate = float(np.random.uniform(
            low=min_nsb_rate,
            high=max_nsb_rate,
            size=1
        ))
        job["output_dir"] = output_dir
        job["casual_muon_support"] = casual_muon_support
        job["casual_muon_direction"] = casual_muon_direction
        job["event_id"] = event_id
        job["nsb_rate"] = nsb_rate
        job["ch_rate"] = ch_rate
        job["opening_angle"] = opening_angle
        job["fact_aperture_radius"] = fact_aperture_radius
        job["arrival_time_std"] = arrival_time_std
        job["random_seed"] = random_seed
        job["point_spread_function"] = point_spread_function
        job["muon_support_ground"] = muon_support_ground
        jobs.append(job)
        new_job_dict = job.copy()
        del new_job_dict["output_dir"]
        save_simulationTruth(event_id, new_job_dict, output_dir)
    return jobs


def run_job(job):
    output_dir = job['output_dir']
    event_id = job['event_id']
    event = rs.simulate_response(
        casual_muon_support=job["casual_muon_support"],
        casual_muon_direction=job["casual_muon_direction"],
        opening_angle=job["opening_angle"],
        nsb_rate_per_pixel=job["nsb_rate"],
        event_id=job["event_id"],
        arrival_time_std=job["arrival_time_std"],
        ch_rate=job["ch_rate"],
        fact_aperture_radius=job["fact_aperture_radius"],
        point_spread_function_std=job["point_spread_function"]
    )
    save_simulationFile(event_id, event, output_dir)
    return 0


def save_simulationFile(event_id, event, output_dir):
    simulationFileName = "_".join(["event", str(event_id)]) + ".sim.phs"
    simulationPath = os.path.join(output_dir, simulationFileName)
    with open(simulationPath, "wb") as fOut:
        ps.io.binary.append_event_to_file(event, fOut)


def save_simulationTruth(event_id, dictionary, output_dir):
    filename = "_".join(["event", str(event_id)]) + ".simulationtruth.csv"
    simTruthPath = os.path.join(output_dir, filename)
    header, values = get_header_and_values(dictionary)
    values = map(str, values)
    value_string = ",".join(values)
    with open(simTruthPath, "w") as fOut:
        fOut.write(("\n".join([header, value_string])))

def create_new_dict(dictionary):
    keys = dictionary.keys()
    new_dict = {}
    for key in keys:
        if isinstance(dictionary[key], Number):
            new_dict[key] = dictionary[key]
        else:
            for i, value in enumerate(dictionary[key]):
                new_key = "_".join([key, str(i)])
                new_dict[new_key] = value
    return new_dict


def get_header_and_values(dictionary):
    new_dict = create_new_dict(dictionary)
    headers = new_dict.keys()
    values = list(new_dict.values())
    header = ",".join(headers)
    return header, values
