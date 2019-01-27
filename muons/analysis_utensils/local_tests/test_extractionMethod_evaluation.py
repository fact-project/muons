import sys
import os
import numpy as np
import shutil
import glob
filePath = os.path.normpath(os.path.abspath(__file__))
fileDir = os.path.normpath(os.path.join(filePath, os.pardir))
parentDir = os.path.normpath(os.path.join(
    fileDir, os.pardir))
scriptDir = os.path.join(parentDir, "simulation_analysis")
sys.path.insert(0, scriptDir)
import extractionMethod_evaluation as eMe
import muons
import photon_stream as ps


simulationFile = os.path.join(
    fileDir, "resources", "100simulations_psf0.0.sim.phs")
simulationTruth_path = os.path.join(
    fileDir, "resources", "100simulations_psf0.0.simulationtruth.csv")
output_dir = os.path.join(fileDir, "resources", "testDir")


def test_create_output_dir():
    eme = eMe.ExtractionMethod_Evaluation(
        simulationFile, simulationTruth_path, output_dir)
    eme.create_output_dir()
    existing = False
    if os.path.isdir(output_dir):
        existing = True
    assert existing == True


def test_check_for_correct_input_allCorrect():
    try:
        eme = eMe.ExtractionMethod_Evaluation(
            simulationFile, simulationTruth_path, output_dir)
        eme.check_for_correct_input()
        error = False
    except ValueError:
        error = True
    assert error == False


def test_check_for_correct_input_wrong_simulationFile():
    try:
        eme = eMe.ExtractionMethod_Evaluation(
            "/foo/bar", simulationTruth_path, output_dir)
        eme.check_for_correct_input()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_check_for_correct_input():
    try:
        eme = eMe.ExtractionMethod_Evaluation(
            simulationFile, "/foo/bar", output_dir)
        eme.check_for_correct_input()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_check_for_correct_input():
    try:
        eme = eMe.ExtractionMethod_Evaluation(
            simulationFile, simulationTruth_path, 3)
        eme.check_for_correct_input()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_calculate_median_radius():
    eme = eMe.ExtractionMethod_Evaluation(
        simulationFile, simulationTruth_path, output_dir)
    x_loc = np.array([1,1,3,1,2])
    y_loc = np.array([1,1,3,1,2])
    muon_ring_cx = 0
    muon_ring_cy = 0
    median_radius = eme.calculate_median_radius(
        x_loc, y_loc, muon_ring_cx, muon_ring_cy)
    assert median_radius == np.sqrt(2)


def test_get_point_cloud():
    eme = eMe.ExtractionMethod_Evaluation(
        simulationFile, simulationTruth_path, output_dir)
    run = ps.EventListReader(simulationFile)
    for i, event in enumerate(run):
        if i == 47:
            photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
    point_cloud = eme.get_point_cloud(photon_clusters)
    assert len(point_cloud[0]) == 3


def test_medianR_extraction():
    eme = eMe.ExtractionMethod_Evaluation(
        simulationFile, simulationTruth_path, output_dir)
    muon_features = {
        "muon_ring_cx": 0,
        "muon_ring_cy": 0}
    run = ps.EventListReader(simulationFile)
    for i, event in enumerate(run):
        if i == 47:
            photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
    medianR_event_info = eme.medianR_extraction(
        muon_features, photon_clusters, 1)
    assert len(medianR_event_info) == 4


def test_save_to_file():
    eme = eMe.ExtractionMethod_Evaluation(
        simulationFile, simulationTruth_path, output_dir)
    method_name = "ringM"
    event_infos = [[1,2,3,4], [1,2,3,4], [1,2,3,4], [1,2,3,4]]
    eme.save_to_file(event_infos, method_name)
    existing = False
    fileName = str(method_name) + "_extracted" + ".csv"
    outpath = os.path.join(output_dir, "extractionFiles", fileName)
    if os.path.exists(outpath):
        existing = True
    assert existing == True


def test_read_cx_cy_from_simulationTruth():
    eme = eMe.ExtractionMethod_Evaluation(
        simulationFile, simulationTruth_path, output_dir)
    event_id = 0
    muon_ring_cx, muon_ring_cy = eme.read_cx_cy_from_simulationTruth(event_id)
    true_cx = -0.051820
    true_cy = -0.000037
    np.testing.assert_almost_equal(
        muon_ring_cx,
        true_cx,
        5)
    np.testing.assert_almost_equal(
        muon_ring_cy,
        true_cy,
        5)


def test_known_center():
    eme = eMe.ExtractionMethod_Evaluation(
        simulationFile, simulationTruth_path, output_dir)
    run = ps.EventListReader(simulationFile)
    event_id = 0
    run = ps.EventListReader(simulationFile)
    for i, event in enumerate(run):
        if i == 47:
            photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
    knownC_event_info = eme.known_center(event_id, photon_clusters)
    assert len(knownC_event_info) == 4


def test_only_ringModel():
    eme = eMe.ExtractionMethod_Evaluation(
        simulationFile, simulationTruth_path, output_dir)
    muon_features = {
        "muon_ring_cx": 0,
        "muon_ring_cy": 0,
        "muon_ring_r": 1}
    event_id = 0
    ringModel_event_info = eme.only_ringModel(event_id, muon_features)
    assert len(ringModel_event_info) == 4


def test_extract_with_hough():
    eme = eMe.ExtractionMethod_Evaluation(
        simulationFile, simulationTruth_path, output_dir)
    muon_features = {
        "muon_ring_cx": 0,
        "muon_ring_cy": 0,
        "muon_ring_r": 1}
    event_id = 0
    ringModel_event_info = eme.only_ringModel(event_id, muon_features)
    assert len(ringModel_event_info) == 4


def test_analysis_main():
    eme = eMe.ExtractionMethod_Evaluation(
        simulationFile, simulationTruth_path, output_dir)
    eme.analysis_main()
    wild_card_path = os.path.join(output_dir, "extractionFiles", "*")
    i = 0
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == 4


def test_do_plotting():
    eme = eMe.ExtractionMethod_Evaluation(
        simulationFile, simulationTruth_path, output_dir)
    eme.do_plotting()
    wild_card_path = os.path.join(output_dir, "Plots", "*", "*")
    i = 0
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == 28


def test_evaluate_methods():
    eme = eMe.ExtractionMethod_Evaluation(
        simulationFile, simulationTruth_path, output_dir)
    eme.evaluate_methods()
    wild_card_path_plots = os.path.join(output_dir, "Plots", "*", "*")
    wild_card_path_extractionFiles = os.path.join(output_dir, "*", "*.csv")
    i = 0
    for path in glob.glob(wild_card_path_plots):
        i += 1
    j = 0
    for path in glob.glob(wild_card_path_extractionFiles):
        j += 1
    assert i == 28 and j==4


def test_dummy_delete_files():
    shutil.rmtree(output_dir)

