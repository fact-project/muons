import photon_stream as ps
from muons.detection import detection
import json
import numpy as np
import os



a = 2.768e4
b = -2.759e3
c = -2.859e2
d = 5.127e1


def evaluate_ring(
    point_positions,
    cx,
    cy,
    r,
    hough_epsilon=np.deg2rad(0.5*0.1111)
):
    total_amplitude = 0
    point_positions_max = point_positions.shape[0]
    for i_point in range(point_positions_max):
        point_x = point_positions[i_point, 0]
        point_y = point_positions[i_point, 1]
        r_point = calculate_point_distance(
            ring_cx=cx, ring_cy=cy,
            point_x=point_x, point_y=point_y)
        point_contribution = apply_triangular_evaluation(
            ring_radius=r, amplitude=1,
            r_point=r_point, hough_epsilon=hough_epsilon)
        total_amplitude += point_contribution
        normed_amplitude = total_amplitude/point_positions_max
    return normed_amplitude


def calculate_point_distance(
    ring_cx,
    ring_cy,
    point_x,
    point_y
):
    x_pos = point_x - ring_cx
    y_pos = point_y - ring_cy
    r_point = np.sqrt(x_pos**2 + y_pos**2)
    return r_point


def apply_triangular_evaluation(
    r_point,
    hough_epsilon,
    ring_radius,
    amplitude
):
    if (
        r_point > ring_radius-hough_epsilon and
        r_point < ring_radius+hough_epsilon
    ):
        abs_loc = abs(r_point-ring_radius)
        point_contribution = amplitude*(
            hough_epsilon-abs_loc)/(hough_epsilon)
    else:
        point_contribution = 0
    return point_contribution


def calculate_PSF(hough_response):
    """ 
    relation between hough_response and PSF is
    ax^3 + bx^2 + cx + d , where 
    a = 2.768e4
    b = -2.759e3
    c = -2.859e2
    d = 5.127e1
    For more info look at the thesis of Laurits
    """
    x = np.arange(0,0.1, 0.0001)
    y = (lambda x: a*(x**3) + b*(x**2) + c*(x) + d)
    sorted_arguments = np.argsort(y(x))
    psf = np.interp(hough_response, y(x)[sorted_arguments], x[sorted_arguments])
    return psf


def calculate_one_run(inpath, outpath):
    hough_responses = []
    run = ps.EventListReader(inpath)
    number_muons = 0
    for event in run:
        photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
        cherenkov_cluster_mask = photon_clusters.labels>=0
        cherenkov_point_cloud = photon_clusters.point_cloud
        cherenkov_clusters = cherenkov_point_cloud[cherenkov_cluster_mask]
        point_positions = cherenkov_clusters[:,0:2]
        muon_props = detection(event, photon_clusters)
        if muon_props["is_muon"]:
            cx = muon_props["muon_ring_cx"]
            cy = muon_props["muon_ring_cy"]
            r = muon_props["muon_ring_r"]
            total_amplitude = evaluate_ring(
                point_positions, cx, cy, r)
            hough_responses.append(total_amplitude)
            number_muons += 1
    hough_responses = np.multiply(hough_responses, 100)
    psf_values = calculate_PSF(hough_responses)
    psf_error = psf_values * 1/np.sqrt(number_muons)
    average_psf = float(np.average(psf_values))
    outdir = os.path.dirname(outpath)
    os.makedirs(outdir, exist_ok=True)
    with open(outpath + ".temp", "wt") as fout:
        out = {
            "average_psf": float(np.average(psf_values)),
            "psf_stdev": float(np.std(psf_values)),
            "standard_error": np.average(psf_error),
            "number_muons": number_muons
        }
        fout.write(json.dumps(out))
    os.rename(outpath + ".temp", outpath)
    return 0