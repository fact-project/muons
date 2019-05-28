import numpy as np
from . import ring_simulation as rs


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


def create_jobs(
    number_of_muons,
    max_inclination,
    max_aperture_radius,
    min_opening_angle,
    max_opening_angle,
    nsb_rate_per_pixel,
    arrival_time_std,
    ch_rate,
    fact_aperture_radius,
    random_seed,
    point_spread_function_std,
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
        job["casual_muon_support"] = casual_muon_support
        job["casual_muon_direction"] = casual_muon_direction
        job["event_id"] = event_id
        job["nsb_rate_per_pixel"] = nsb_rate_per_pixel
        job["ch_rate"] = ch_rate
        job["opening_angle"] = opening_angle
        job["fact_aperture_radius"] = fact_aperture_radius
        job["arrival_time_std"] = arrival_time_std
        job["random_seed"] = random_seed
        job["point_spread_function_std"] = point_spread_function_std
        job["muon_support_ground"] = muon_support_ground
        jobs.append(job)
    return jobs


def run_job(job):
    pure_event, nsb_event = rs.simulate_response(
        casual_muon_support=job["casual_muon_support"],
        casual_muon_direction=job["casual_muon_direction"],
        opening_angle=job["opening_angle"],
        nsb_rate_per_pixel=job["nsb_rate_per_pixel"],
        event_id=job["event_id"],
        arrival_time_std=job["arrival_time_std"],
        ch_rate=job["ch_rate"],
        fact_aperture_radius=job["fact_aperture_radius"],
        point_spread_function_std=job["point_spread_function_std"]
    )
    return {"pure_event": pure_event, "nsb_event": nsb_event}


def write_to_csv(simTruthPath, simulationTruths):
    with open(simTruthPath, "wt") as fout:
        h = "casual_muon_support0,"
        h += "casual_muon_support1,"
        h += "casual_muon_support2,"
        h += "casual_muon_direction0,"
        h += "casual_muon_direction1,"
        h += "casual_muon_direction2,"
        h += "event_id,"
        h += "nsb_rate_per_pixel,"
        h += "ch_rate,"
        h += "opening_angle,"
        h += "fact_aperture_radius,"
        h += "arrival_time_std,"
        h += "random_seed,"
        h += "point_spread_function_std,"
        h += "muon_support_ground0,"
        h += "muon_support_ground1\n"
        fout.write(h)
        for sT in simulationTruths:
            s = "{:f},{:f},{:f},".format(
                sT["casual_muon_support"][0],
                sT["casual_muon_support"][1],
                sT["casual_muon_support"][2])
            s += "{:f},{:f},{:f},".format(
                sT["casual_muon_direction"][0],
                sT["casual_muon_direction"][1],
                sT["casual_muon_direction"][2])
            s += "{:d},".format(sT["event_id"])
            s += "{:f},".format(sT["nsb_rate_per_pixel"])
            s += "{:f},".format(sT["ch_rate"])
            s += "{:f},".format(sT["opening_angle"])
            s += "{:f},".format(sT["fact_aperture_radius"])
            s += "{:f},".format(sT["arrival_time_std"])
            s += "{:d},".format(sT["random_seed"])
            s += "{:f},".format(sT["point_spread_function_std"])
            s += "{:f},".format(sT["muon_support_ground"][0])
            s += "{:f}\n".format(sT["muon_support_ground"][1])
            fout.write(s)
