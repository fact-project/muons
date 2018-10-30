import astropy
from astropy.modeling.functional_models import Ring2D
import numpy as np


def hough_transform_ring(
    point_positions,
    cx_bin_centers,
    cy_bin_centers,
    r_bin_centers,
    epsilon
):
    ones = np.ones(point_positions.shape[0])
    houghSpace = np.zeros(
        shape=(cx_bin_centers.shape[0],
            cy_bin_centers.shape[0],
            r_bin_centers.shape[0])
    )
    for i_cx, cx in enumerate(cx_bin_centers):
        for i_cy, cy in enumerate(cy_bin_centers):
            for i_r, r in enumerate(r_bin_centers):
                houghSpace[i_cx, i_cy, i_r] = sum(
                    Ring2D.evaluate(
                        x=point_positions[:,0],
                        y=point_positions[:,1],
                        x_0=cx,
                        y_0=cy,
                        amplitude=ones,
                        r_in=r - epsilon,
                        width=2*epsilon
                    )
                )
    return houghSpace


def get_bin_centers(
    c_x, c_y, r, uncertainty
):
    cx_bin_centers = np.linspace(
        start = c_x- 0.5*uncertainty,
        stop= c_x + 0.5*uncertainty,
        num=10)
    cy_bin_centers = np.linspace(
        start = c_y- 0.5*uncertainty,
        stop= c_y + 0.5*uncertainty,
        num=10)
    r_bin_centers = np. linspace(
        start = r- 0.5*uncertainty,
        stop= r + 0.5*uncertainty,
        num=10)
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
