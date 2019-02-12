import numpy as np
from muons.tools import circle_overlapp
from muons.tools import tight_circle_on_off_region
from muons.tools import xy2polar
from circlehough.hough import main as hough_transform
from skimage.measure import ransac
from skimage.measure import CircleModel


deg2rad = np.deg2rad(1)


def detection(
    event,
    clusters,
    epsilon=np.deg2rad(0.5*0.1111),
    initial_circle_model_min_samples=3,
    initial_circle_model_residual_threshold=0.25,
    initial_circle_model_max_trials=15,
    uncertainty=np.deg2rad(0.8),
    min_muon_ring_radius=0.4,
    max_muon_ring_radius=1.6,
    min_overlap_of_muon_ring_with_field_of_view=0.20,
    max_arrival_time_stddev=3e-9,
    initial_circle_model_min_photon_ratio=0.8,
    min_circumference_of_muon_ring_in_field_of_view=1.5,
    density_circle_model_residual_threshold=0.20,
    density_circle_model_min_on_off_ratio=3.5,
    density_circle_model_max_ratio_photon_inside_ring=0.35
):
    ret = {}
    ret['is_muon'] = False
    full_cluster_mask = clusters.labels >= 0
    flat_photon_stream = clusters.point_cloud
    # full_clusters_fps = flat_photon_stream[full_cluster_mask]
    initial_found_cherenkov = flat_photon_stream[full_cluster_mask]
    full_clusters_fps = cut_hist(initial_found_cherenkov)
    if len(full_clusters_fps) == 0:
        return ret
    number_of_photons = full_cluster_mask.sum()
    ret, inliers = perform_circleModel(
        ret, full_clusters_fps,
        initial_circle_model_min_samples,
        initial_circle_model_residual_threshold,
        initial_circle_model_max_trials
    )
    ret = perform_hough(
        ret, full_clusters_fps,
        uncertainty,
        epsilon
    )
    to_continue, ret = check_photon_count(
        full_cluster_mask, ret, number_of_photons,
        initial_circle_model_min_samples)
    if to_continue == False:
        return ret
    to_continue = check_ring_radius(
        ret,
        min_muon_ring_radius,
        max_muon_ring_radius)
    if to_continue == False:
        return ret
    # print("find inliers_count")
    # inliers = find_inliers_count(epsilon, full_clusters_fps, ret)
    to_continue, ret, field_of_view_radius = (
        check_ring_overlap_with_FOV(
            ret, event,
            min_overlap_of_muon_ring_with_field_of_view
        ))
    if to_continue == False:
        return ret
    to_continue, ret = check_arrival_time(
        full_clusters_fps, ret,
        max_arrival_time_stddev)
    if to_continue == False:
        return ret
    to_continue, ret, onoff = circle_model_on_off_ratio(
        full_clusters_fps, ret,
        density_circle_model_residual_threshold,
        density_circle_model_min_on_off_ratio)
    if to_continue == False:
        return ret
    to_continue, ret = check_ratio_inside_circle(
        onoff, ret, number_of_photons,
        density_circle_model_max_ratio_photon_inside_ring)
    if to_continue == False:
        return ret
    to_continue, ret = find_visible_muon_ring_circumfance(
        number_of_photons, ret, field_of_view_radius,
        min_circumference_of_muon_ring_in_field_of_view)
    if to_continue == False:
        return ret
    to_continue, ret = find_photon_ratio(
        inliers, number_of_photons, ret,
        initial_circle_model_min_photon_ratio
    )
    if to_continue == False:
        return ret
    ring_population_hist, number_of_fraction_bins = check_population(
        ret, full_clusters_fps, number_of_photons)
    ret = check_if_population_is_even(
        ret, ring_population_hist, number_of_fraction_bins)
    return ret


def cut_hist(nsb_cherenkov_photon_stream):
    cherenkov_photons = []
    r = np.sqrt(
        nsb_cherenkov_photon_stream[:,0]**2
        + nsb_cherenkov_photon_stream[:,1]**2
    )
    r_stedev = np.std(r)
    r_average = np.average(r)
    t_stdev = np.std(nsb_cherenkov_photon_stream[:,2])
    t_average = np.average(nsb_cherenkov_photon_stream[:,2])
    for photon in nsb_cherenkov_photon_stream:
        photon_r = np.sqrt(photon[0]**2 + photon[1]**2)
        if not (photon_r > r_average + 1.95*r_stedev) and not (
            photon_r < r_average - 1.95*r_stedev
        ):
            if not (photon[2] > t_average + 1.95*t_stdev) and not (
                photon[2] < t_average - 1.95*t_stdev
            ):
                cherenkov_photons.append(photon)
    return np.array(cherenkov_photons)


def check_photon_count(
    full_cluster_mask,
    ret,
    number_of_photons,
    initial_circle_model_min_samples
):
    ret['number_of_photons'] = number_of_photons

    if number_of_photons < initial_circle_model_min_samples:
        return False, ret
    else:
        return True, ret


def perform_circleModel(
    ret,
    full_clusters_fps,
    initial_circle_model_min_samples,
    initial_circle_model_residual_threshold,
    initial_circle_model_max_trials
):
    initial_circle_model_residual_threshold *= deg2rad
    try:
        with np.errstate(invalid='ignore'):
            circle_model, inliers = ransac(
                data=full_clusters_fps[:, 0:2],  # only cx and cy not the time
                model_class=CircleModel,
                min_samples=initial_circle_model_min_samples,
                residual_threshold=initial_circle_model_residual_threshold,
                max_trials=initial_circle_model_max_trials)
        cx = circle_model.params[0]
        cy = circle_model.params[1]
        r = circle_model.params[2]
        ret['muon_ring_cx'] = cx
        ret['muon_ring_cy'] = cy
        ret['muon_ring_r'] = r
        return ret, inliers.sum()
    except ValueError:
        ret['muon_ring_cx'] = np.deg2rad(2.5)
        ret['muon_ring_cy'] = np.deg2rad(2.5)
        ret['muon_ring_r'] = np.deg2rad(0.8)
        return ret, 0


def perform_hough(
    ret,
    clusters_point_cloud,
    uncertainty,
    epsilon
):
    guessed_cx = ret['muon_ring_cx']
    guessed_cy = ret['muon_ring_cy']
    guessed_r = ret['muon_ring_r']
    hough_cx, hough_cy, hough_r = hough_transform(
        guessed_cx, guessed_cy, guessed_r, clusters_point_cloud,
        uncertainty, epsilon
    )
    ret['muon_ring_cx'] = hough_cx
    ret['muon_ring_cy'] = hough_cy
    ret['muon_ring_r'] = hough_r
    return ret


def check_ring_radius(
    ret,
    min_muon_ring_radius,
    max_muon_ring_radius
):
    r = ret['muon_ring_r']
    min_muon_ring_radius *= deg2rad
    max_muon_ring_radius *= deg2rad
    if r < min_muon_ring_radius or r > max_muon_ring_radius:
        return False
    else:
        return True


def check_ring_overlap_with_FOV(
    ret,
    event,
    min_overlap_of_muon_ring_with_field_of_view
):
    cx = ret["muon_ring_cx"]
    cy = ret["muon_ring_cy"]
    r = ret["muon_ring_r"]
    field_of_view_radius = event.photon_stream.geometry.fov_radius
    muon_ring_overlapp_with_field_of_view = circle_overlapp(
        cx1=0.0,
        cy1=0.0,
        r1=field_of_view_radius,
        cx2=cx,
        cy2=cy,
        r2=r)
    ret['muon_ring_overlapp_with_field_of_view'] = (
        muon_ring_overlapp_with_field_of_view)
    if (
        muon_ring_overlapp_with_field_of_view <
        min_overlap_of_muon_ring_with_field_of_view
    ):
        return False, ret, field_of_view_radius
    else:
        return True, ret, field_of_view_radius


def check_arrival_time(
    full_clusters_fps,
    ret,
    max_arrival_time_stddev
):
    arrival_time_stddev = full_clusters_fps[:, 2].std()
    ret['arrival_time_stddev'] = arrival_time_stddev
    ret['mean_arrival_time_muon_cluster'] = full_clusters_fps[:, 2].mean()
    if arrival_time_stddev > max_arrival_time_stddev:
        return False, ret
    else:
        return True, ret


def find_inliers_count(epsilon, cluster_point_cloud, ret):
    cx = ret["muon_ring_cx"]
    cy = ret["muon_ring_cy"]
    r = ret["muon_ring_r"]
    x_loc = np.array(cluster_point_cloud[:,0])
    y_loc = np.array(cluster_point_cloud[:,1])
    x_diff = x_loc - cx
    y_diff = y_loc - cy
    ph_r = np.sqrt(x_diff**2 + y_diff**2)
    difference = abs(ph_r - r)
    upper_limit = r + epsilon
    lower_limit = r - epsilon
    lower_limit_mask = difference >= lower_limit
    difference = difference[lower_limit_mask]
    upper_limit_mask = difference <= upper_limit
    inliers = upper_limit_mask.sum()
    return inliers


def find_photon_ratio(
    inliers,
    number_of_photons,
    ret,
    initial_circle_model_min_photon_ratio
):
    initial_circle_model_photon_ratio = (
        inliers/number_of_photons
    )
    ret['initial_circle_model_photon_ratio'] = (
        initial_circle_model_photon_ratio
    )
    if (
        initial_circle_model_photon_ratio <
        initial_circle_model_min_photon_ratio
    ):
        return False, ret
    else:
        return True, ret


def find_visible_muon_ring_circumfance(
    number_of_photons,
    ret,
    field_of_view_radius,
    min_circumference_of_muon_ring_in_field_of_view
):
    cx = ret['muon_ring_cx']
    cy = ret['muon_ring_cy']
    r = ret['muon_ring_r']
    min_circumference_of_muon_ring_in_field_of_view *= deg2rad
    muon_ring_overlap_with_field_of_view = circle_overlapp(
        cx1=0.0,
        cy1=0.0,
        r1=field_of_view_radius,
        cx2=cx,
        cy2=cy,
        r2=r
    )
    visible_ring_circumfance = r*2*np.pi*muon_ring_overlap_with_field_of_view
    ret['visible_muon_ring_circumfance'] = visible_ring_circumfance
    if (
        visible_ring_circumfance <
        min_circumference_of_muon_ring_in_field_of_view
    ):
        return False, ret
    else:
        return True, ret


def circle_model_on_off_ratio(
    full_clusters_fps,
    ret,
    density_circle_model_residual_threshold,
    density_circle_model_min_on_off_ratio
):
    density_circle_model_residual_threshold *= deg2rad
    cx = ret["muon_ring_cx"]
    cy = ret["muon_ring_cy"]
    r = ret["muon_ring_r"]
    onoff = tight_circle_on_off_region(
        cx=cx,
        cy=cy,
        r=r,
        residual_threshold=density_circle_model_residual_threshold,
        xy=full_clusters_fps[:, 0:2])
    on_density = onoff['on'].sum()/onoff['area_on']
    inner_off_density = onoff['inner_off'].sum()/onoff['area_inner_off']
    outer_off_density = onoff['outer_off'].sum()/onoff['area_outer_off']
    off_density = (outer_off_density + inner_off_density)/2
    on_off_ratio = on_density/off_density
    ret['density_circle_model_on_off_ratio'] = on_off_ratio
    if (
        (off_density == 0) or (
            on_off_ratio < density_circle_model_min_on_off_ratio)):
        return False, ret, onoff
    else:
        return True, ret, onoff


def check_ratio_inside_circle(
    onoff,
    ret,
    number_of_photons,
    density_circle_model_max_ratio_photon_inside_ring
):
    number_of_photons_inside_ring_off = onoff['inside_off'].sum()
    ratio_inside_circle = number_of_photons_inside_ring_off/number_of_photons
    ret['density_circle_model_inner_ratio'] = ratio_inside_circle
    if ratio_inside_circle > density_circle_model_max_ratio_photon_inside_ring:
        return False, ret
    else:
        return True, ret


def check_population(ret, full_clusters_fps, number_of_photons):
    cx = ret["muon_ring_cx"]
    cy = ret["muon_ring_cy"]
    r = ret["muon_ring_r"]
    xy_relative_to_ring_center = full_clusters_fps
    xy_relative_to_ring_center[:, 0] -= cx
    xy_relative_to_ring_center[:, 1] -= cy
    rphi = xy2polar(xy=xy_relative_to_ring_center[:, 0:2])
    number_bins = 3*int(np.ceil(np.sqrt(number_of_photons)))
    phi_bin_edges = np.linspace(-np.pi, np.pi, number_bins)
    ring_population_hist, phi_bin_edges = np.histogram(
        rphi[:, 1],
        bins=phi_bin_edges)
    min_ring_circumfance = 2.5*deg2rad
    ring_circumfance = 2*r*np.pi
    min_ring_fraction = min_ring_circumfance/ring_circumfance
    if min_ring_fraction < 0.33:
        min_ring_fraction = 0.33
    number_of_fraction_bins = int(np.round(min_ring_fraction*number_bins))
    return ring_population_hist, number_of_fraction_bins


def check_if_population_is_even(
    ret,
    ring_population_hist,
    number_of_fraction_bins
):
    is_populated_evenly = False
    is_populated_at_all = False
    most_even_population_std = 1e99
    for i in range(ring_population_hist.shape[0]):
        section = np.take(
            ring_population_hist,
            range(i, i+number_of_fraction_bins),
            mode='wrap')
        if (section > 0).sum() >= 0.5*number_of_fraction_bins:
            is_populated_at_all = True
            rel_std = section.std()/section.mean()
            if rel_std < most_even_population_std:
                most_even_population_std = rel_std
    if is_populated_at_all and most_even_population_std < 0.8:
        is_populated_evenly = True
    if is_populated_evenly:
        ret['is_muon'] = True
    return ret