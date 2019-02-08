import numpy as np
import fact
import scipy
import photon_stream as ps
import single_photon_extractor as spe


def pol2cart(r, azimuth, inclination):
    x = r * np.cos(azimuth) * np.sin(inclination)
    y = r * np.sin(azimuth) * np.sin(inclination)
    z = r * np.cos(inclination)
    return np.array([float(x), float(y), float(z)])


def position_on_ray(support, direction, alpha):
    return support + np.multiply(alpha, direction)


def get_d_alpha(ch_rate):
    d_alpha = -np.log(np.random.uniform())/ch_rate
    return d_alpha


def emit_photons(
    casual_muon_support,
    casual_muon_direction,
    opening_angle,
    ch_rate
):
    casual_muon_support = np.array(casual_muon_support)
    casual_muon_direction = np.array(casual_muon_direction)
    path_length = 0
    photon_emission_pos = []
    photon_directions = []
    u, v = get_u_v(casual_muon_direction)
    while True:
        d_alpha = get_d_alpha(ch_rate)
        path_length += d_alpha
        ch_emission_position = position_on_ray(
            casual_muon_support,
            casual_muon_direction,
            path_length
        )
        if ch_emission_position[2] <= 0:
            break
        photon_emission_pos.append(ch_emission_position)
        direction_of_photon = draw_direction_of_cherenkov_photon(
            opening_angle,
            u,
            v,
            casual_muon_direction)
        photon_directions.append(direction_of_photon)
    return np.array(photon_emission_pos), np.array(photon_directions)


def get_u_v(direction):
    dx, dz = direction[0], direction[2]
    a = np.sqrt(1 / (1+((dx/dz)**2)))
    b = np.sqrt(1 - a**2)
    u = (a, 0, b)
    v = np.cross(np.array(u), np.array(direction))
    return np.array(u), v


def draw_direction_of_cherenkov_photon(
    opening_angle,
    u,
    v,
    casual_muon_direction
):
    azimuth = np.random.uniform(
        low=0,
        high=2*np.pi)
    position_on_ring = np.cos(azimuth)*u + np.sin(azimuth)*v
    dist_on_mu_path = 1 / np.tan(opening_angle)
    cherenkov_ph_dir = dist_on_mu_path*casual_muon_direction + position_on_ring
    return cherenkov_ph_dir/np.linalg.norm(cherenkov_ph_dir)


def project_ch_photon_on_ground(
    photon_emission_positions,
    photon_directions
):
    t = -photon_emission_positions[:, 2] / photon_directions[:, 2]
    xys = np.multiply(t[:, np.newaxis], photon_directions)
    xys += photon_emission_positions
    return xys


def mask_for_photons_in_aperture_radius(
        intersection_point_on_xy_plane,
        aperture_radius
):
    distances_squared = (
        intersection_point_on_xy_plane[:, 0]**2
        + intersection_point_on_xy_plane[:, 1]**2)
    return distances_squared <= aperture_radius**2


def perfect_imaging(
        photon_emission_positions,
        photon_directions,
        aperture_radius
):
    intersection_points = project_ch_photon_on_ground(
        photon_emission_positions,
        photon_directions
    )
    inside_aperture = mask_for_photons_in_aperture_radius(
        intersection_points,
        aperture_radius
    )
    return photon_directions[inside_aperture, 0:2]


def create_fact_pixel_tree():
    x_pos_mm, y_pos_mm = fact.instrument.get_pixel_coords()
    x_angle = np.arctan(x_pos_mm/fact.instrument.constants.FOCAL_LENGTH_MM)
    y_angle = np.arctan(y_pos_mm/fact.instrument.constants.FOCAL_LENGTH_MM)
    return scipy.spatial.KDTree(np.c_[x_angle, y_angle])


def artificial_point_spread_function(number_photons, standard_dev):
    return np.random.normal(
        loc=0,
        scale=standard_dev,
        size=(number_photons, 2))


def assign_to_pixels(
    photons_cx_cy,
    pixel_position_tree,
    pixel_radius=np.deg2rad(fact.instrument.camera.FOV_PER_PIXEL_DEG)/2
):
    distances, pixel_CHIDs = pixel_position_tree.query(
        photons_cx_cy)
    inside_field_of_view = distances <= pixel_radius
    return inside_field_of_view, pixel_CHIDs


def arrival_times_for_cherenkov_photons_from_muon(
    number_photons,
    arrival_time_std
):
    return np.random.normal(
        loc=0.0,
        scale=arrival_time_std,
        size=number_photons)


def create_raw_photon_stream(pixel_CHIDs, arrival_times, nsb_rate_per_pixel):
    arrival_slices = np.round(
        arrival_times/ps.io.magic_constants.TIME_SLICE_DURATION_S).astype(
            np.int)
    lol = spe.air_shower_classification.air_shower_classification.generate_nsb(
        nsb_rate_per_pixel
    )
    for i in range(len(lol)):
        lol[i] = list(lol[i])
    for photon, chid in enumerate(pixel_CHIDs):
        lol[chid].append(arrival_slices[photon])
    return ps.representations.list_of_lists_to_raw_phs(lol)


def create_event(arrival_times, ch_CHIDs, event_id, nsb_rate_per_pixel):
    arrival_times += 22e-9
    phs = ps.PhotonStream()
    phs.slice_duration = np.float32(
        ps.io.magic_constants.TIME_SLICE_DURATION_S)
    phs.raw = create_raw_photon_stream(
        ch_CHIDs,
        arrival_times,
        nsb_rate_per_pixel)
    event = ps.Event()
    event.photon_stream = phs
    event.photon_stream.saturated_pixels = np.zeros(0, dtype=np.uint16)
    event.zd = np.float32(0.0)
    event.az = np.float32(0.0)
    sim = ps.simulation_truth.SimulationTruth()
    sim.reuse = np.uint32(0)
    sim.run = np.uint32(0)
    sim.event = np.uint32(event_id)
    event.simulation_truth = sim
    return event


def simulate_response(
    casual_muon_support,
    casual_muon_direction,
    opening_angle,
    nsb_rate_per_pixel,
    event_id,
    arrival_time_std,
    ch_rate,
    fact_aperture_radius,
    point_spread_function_std
):
    ch_sup, ch_dir = emit_photons(
        casual_muon_support,
        casual_muon_direction,
        opening_angle,
        ch_rate)
    photons_cx_cy = perfect_imaging(
        ch_sup,
        ch_dir,
        aperture_radius=fact_aperture_radius)
    fuzz_cx_cy = photons_cx_cy + artificial_point_spread_function(
        number_photons=photons_cx_cy.shape[0],
        standard_dev=point_spread_function_std)
    inside_pixels, ch_CHIDs = assign_to_pixels(
        fuzz_cx_cy,
        create_fact_pixel_tree())
    ch_CHIDs = ch_CHIDs[inside_pixels]
    arrival_times = arrival_times_for_cherenkov_photons_from_muon(
        number_photons=ch_CHIDs.shape[0],
        arrival_time_std=arrival_time_std)
    event = create_event(
        arrival_times, ch_CHIDs, event_id, nsb_rate_per_pixel)
    return event