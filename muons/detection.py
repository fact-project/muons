from .detection_with_simple_ring_fit import detection_with_simple_ring_fit
import numpy as np
from circlehough.hough import advanced_guess_with_hough


def detection(
    event,
    clusters,
    initial_circle_model_min_samples=3,
    initial_circle_model_residual_threshold=0.25,
    initial_circle_model_max_trails=15,
    initial_circle_model_min_photon_ratio=0.6,
    density_circle_model_residual_threshold=0.20,
    density_circle_model_min_on_off_ratio=3.5,
    density_circle_model_max_ratio_photon_inside_ring=0.25,
    min_circumference_of_muon_ring_in_field_of_view=1.5,
    max_arrival_time_stddev=5e-9,
    min_overlap_of_muon_ring_with_field_of_view=0.2,
    min_muon_ring_radius=0.45,
    max_muon_ring_radius=1.6,
    hough_uncertainty=np.deg2rad(1),
    hough_epsilon=np.deg2rad(0.1111*1.5)
):
    muon_features = detection_with_simple_ring_fit(
        event,
        clusters,
        initial_circle_model_min_samples=3,
        initial_circle_model_residual_threshold=0.25,
        initial_circle_model_max_trails=15,
        initial_circle_model_min_photon_ratio=0.6,
        density_circle_model_residual_threshold=0.20,
        density_circle_model_min_on_off_ratio=3.5,
        density_circle_model_max_ratio_photon_inside_ring=0.25,
        min_circumference_of_muon_ring_in_field_of_view=1.5,
        max_arrival_time_stddev=5e-9,
        min_overlap_of_muon_ring_with_field_of_view=0.2,
        min_muon_ring_radius=0.45,
        max_muon_ring_radius=1.6
    )
    full_cluster_mask = clusters.labels >= 0
    flat_photon_stream = clusters.point_cloud
    point_cloud = flat_photon_stream[full_cluster_mask]
    if muon_features['is_muon']:
        i = 0
        while i < 100:
            i += 1
            previous_muon_features = muon_features.copy()
            muon_features = apply_hough(
                muon_features, point_cloud[:,0:2],
                hough_uncertainty, hough_epsilon
            )
            d_cx, d_cy, d_r = compare_old_new(
                previous_muon_features, muon_features
            )
            hough_uncertainty /= 2
            if (
                d_cx <= np.deg2rad(0.05) and
                d_cy <= np.deg2rad(0.05) and
                d_r <= np.deg2rad(0.03) and
                i >= 6
            ):
                break
    return muon_features


def apply_hough(
    muon_features, point_cloud, hough_uncertainty, hough_epsilon
):
    guessed_cx = muon_features['muon_ring_cx']
    guessed_cy = muon_features['muon_ring_cy']
    guessed_r = muon_features['muon_ring_r']
    hough_cx, hough_cy, hough_r = advanced_guess_with_hough(
        guessed_cx=guessed_cx, guessed_cy=guessed_cy,
        guessed_r=guessed_r, point_cloud=point_cloud,
        uncertainty=hough_uncertainty, epsilon=hough_epsilon
    )
    muon_features["muon_ring_cx"] = hough_cx
    muon_features["muon_ring_cy"] = hough_cy
    muon_features["muon_ring_r"] = hough_r
    return muon_features


def compare_old_new(previous_muon_features, muon_features):
    old_cx = previous_muon_features['muon_ring_cx']
    old_cy = previous_muon_features['muon_ring_cy']
    old_r = previous_muon_features['muon_ring_r']
    cx = muon_features['muon_ring_cx']
    cy = muon_features['muon_ring_cy']
    r = muon_features['muon_ring_r']
    d_cx = abs(old_cx)-abs(cx)
    d_cy = abs(old_cy)-abs(cy)
    d_r = abs(old_r)-abs(r)
    return d_cx, d_cy, d_r
