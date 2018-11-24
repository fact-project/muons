import math
import numpy as np


def apply_triangular_evaluation(
    r_photon, hough_epsilon, ring_radius, amplitude
):
    if (
        r_photon > ring_radius-hough_epsilon and
        r_photon < ring_radius+hough_epsilon
    ):
        abs_loc = abs(r_photon-ring_radius)
        photon_contribution = amplitude*(
            hough_epsilon-abs_loc)/(hough_epsilon)
    else:
        photon_contribution = 0
    return photon_contribution


def calculate_photon_distance(
    ring_cx, ring_cy, photon_x, photon_y
):
    distance_vector = (photon_x-ring_cx, photon_y-ring_cy)
    r_photon = math.sqrt(distance_vector[0]**2 + distance_vector[1]**2)
    return r_photon


def sum_photon_contributions(photon_positions, cx, cy, r, hough_epsilon):
    total_amplitude = 0
    for photon in photon_positions:
        photon_x = photon[0]
        photon_y = photon[1]
        r_photon = calculate_photon_distance(
            ring_cx=cx, ring_cy=cy,
            photon_x=photon_x, photon_y=photon_y)
        photon_contribution = apply_triangular_evaluation(
            ring_radius=r, amplitude=1,
            r_photon=r_photon, hough_epsilon=hough_epsilon)
        total_amplitude += photon_contribution
    return total_amplitude


def hough_transform_ring(
    point_positions,
    cx_bin_centers,
    cy_bin_centers,
    r_bin_centers,
    hough_epsilon
):
    houghSpace = np.zeros(
        shape=(
            cx_bin_centers.shape[0],
            cy_bin_centers.shape[0],
            r_bin_centers.shape[0])
    )
    for i_cx, cx in enumerate(cx_bin_centers):
        for i_cy, cy in enumerate(cy_bin_centers):
            for i_r, r in enumerate(r_bin_centers):
                houghSpace[i_cx, i_cy, i_r] = sum_photon_contributions(
                    point_positions, cx, cy, r, hough_epsilon)
    return houghSpace


# ---------------old--------------------------


def get_bin_centers(
    c_x, c_y, r, uncertainty
):
    cx_bin_centers = np.linspace(
        start=c_x - 0.5*uncertainty,
        stop=c_x + 0.5*uncertainty,
        num=11)
    cy_bin_centers = np.linspace(
        start=c_y - 0.5*uncertainty,
        stop=c_y + 0.5*uncertainty,
        num=11)
    r_bin_centers = np.linspace(
        start=r - 0.5*uncertainty,
        stop=r + 0.5*uncertainty,
        num=11)
    return cx_bin_centers, cy_bin_centers, r_bin_centers


def interpretHoughSpace(
    houghSpace
):
    indices_of_maximum_value = np.unravel_index(
        np.argmax(houghSpace), dims=houghSpace.shape)
    return indices_of_maximum_value


def advanced_guess_with_hough(
    guessed_cx, guessed_cy, guessed_r, point_cloud,
    uncertainty, epsilon
):
    cx_bin_centers, cy_bin_centers, r_bin_centers = (
        get_bin_centers(guessed_cx, guessed_cy, guessed_r, uncertainty)
    )
    point_positions = point_cloud
    houghSpace = hough_transform_ring(
        point_positions, cx_bin_centers,
        cy_bin_centers, r_bin_centers, epsilon
    )
    location_for_maxima = interpretHoughSpace(houghSpace)
    hough_cx_idx = int(location_for_maxima[0])
    hough_cy_idx = int(location_for_maxima[1])
    hough_r_idx = int(location_for_maxima[2])
    hough_cx = cx_bin_centers[hough_cx_idx]
    hough_cy = cy_bin_centers[hough_cy_idx]
    hough_r = r_bin_centers[hough_r_idx]
    return hough_cx, hough_cy, hough_r
