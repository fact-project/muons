import sys
import os
import numpy as np
import glob
from muons.analysis_utensils.simulation_analysis import (
    evaluate_detectionMethod as edM)
import photon_stream as ps
import shutil


filePath = os.path.normpath(os.path.abspath(__file__))
fileDir = os.path.normpath(os.path.join(filePath, os.pardir))
output_dir = os.path.join(fileDir, "resources", "testDir")
number_of_muons = 3
steps = 3
step_size = 10
scoop_hosts = os.path.join(fileDir, "resources", "scoop_hosts.txt")
simulation_dir = os.path.join(output_dir, "simulations")
simulationFile = os.path.join(
    fileDir, "resources", "100simulations_psf0.0.sim.phs")



def test_check_input_correctness_allCorrect():
    try:
        dme = edM.DetectionMethodEvaluation(
            output_dir, number_of_muons, steps, step_size, scoop_hosts)
        dme.check_input_correctness()
        error = False
    except ValueError:
        error = True
    assert error == False


def test_check_input_correctness_wrong_output_dir():
    try:
        dme = edM.DetectionMethodEvaluation(
            42, number_of_muons, steps, step_size, scoop_hosts)
        dme.check_input_correctness()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_check_input_correctness_wrong_muonNumber1():
    try:
        dme = edM.DetectionMethodEvaluation(
            output_dir, 2.5, steps, step_size, scoop_hosts)
        dme.check_input_correctness()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_check_input_correctness_wrong_muonNumber2():
    try:
        dme = edM.DetectionMethodEvaluation(
            output_dir, "5" , steps, step_size, scoop_hosts)
        dme.check_input_correctness()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_check_input_correctness_wrong_steps():
    try:
        dme = edM.DetectionMethodEvaluation(
            output_dir, number_of_muons, 2.5, step_size, scoop_hosts)
        dme.check_input_correctness()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_check_input_correctness_wrong_stepSize():
    try:
        dme = edM.DetectionMethodEvaluation(
            output_dir, number_of_muons, steps, "small", scoop_hosts)
        dme.check_input_correctness()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_check_input_correctness_noScoopHosts():
    try:
        dme = edM.DetectionMethodEvaluation(
            output_dir, number_of_muons, steps, step_size, "/foo/bar")
        dme.check_input_correctness()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_get_scoop_simulate_muon_rings_path():
    dme = edM.DetectionMethodEvaluation(
        output_dir, number_of_muons, steps, step_size, scoop_hosts)
    path_to_scoop_simulate = dme.get_scoop_simulate_muon_rings_path()
    existing = False
    if os.path.exists(path_to_scoop_simulate):
        existing = True
    assert existing == True


def test_create_outputDir():
    dme = edM.DetectionMethodEvaluation(
        output_dir, number_of_muons, steps, step_size, scoop_hosts)
    dme.create_outputDir()
    existing = False
    if os.path.isdir(output_dir):
        existing = True
    assert existing == True


def test_run_simulation():
    dme = edM.DetectionMethodEvaluation(
        output_dir, number_of_muons, steps, step_size, scoop_hosts)
    dme.run_simulation(simulation_dir)
    dir_wild_card_path = os.path.join(simulation_dir, "*")
    i = 0
    for path in glob.glob(dir_wild_card_path):
        i += 1
    assert i == 2


def test_do_clustering1():
    dme = edM.DetectionMethodEvaluation(
        output_dir, number_of_muons, steps, step_size, scoop_hosts)
    results = dme.do_clustering(simulationFile, simulationFile)
    assert len(results) == 3


def test_do_clustering2():
    dme = edM.DetectionMethodEvaluation(
        output_dir, number_of_muons, steps, step_size, scoop_hosts)
    results = dme.do_clustering(simulationFile, simulationFile)
    assert len(results[0]) != 0


def test_true_false_decisions():
    dme = edM.DetectionMethodEvaluation(
        output_dir, 2, steps, step_size, scoop_hosts)
    p1 = np.array([1, 1, 2])
    p2 = np.array([1, 1, 1])
    p3 = np.array([2, 2, 2])
    p4 = np.array([4, 4, 4])
    p5 = np.array([5, 5, 5])
    all_photons_run = np.array(
        [np.array([p1, p2, p3, p4, p5]), np.array([p1, p2, p3, p4, p5])])
    pure_cherenkov_run_photons = np.array(
        [np.array([p2, p3, p4]), np.array([p2, p3, p4])])
    nsb_run_found_photons = np.array(
        [np.array([p1, p3, p4]), np.array([p1, p3, p4])])
    events = dme.true_false_decisions(
        all_photons_run, pure_cherenkov_run_photons, nsb_run_found_photons)
    np.testing.assert_almost_equal(
        events,
        [[3, 3, 2, 1, 1, 1, 200/3, 200/3], [3, 3, 2, 1, 1, 1, 200/3, 200/3]],
        5)


def test_save_to_file():
    dme = edM.DetectionMethodEvaluation(
        output_dir, number_of_muons, steps, step_size, scoop_hosts)
    events = [
        [3, 3, 2, 1, 1, 1, 200/3, 200/3], [3, 3, 2, 1, 1, 1, 200/3, 200/3]]
    file_out = os.path.join(output_dir, "nsb_35e6_precision_results.csv")
    dme.save_to_file(file_out, events)
    statinfo = os.stat(file_out)
    assert os.path.exists(file_out) and statinfo.st_size > 112


def test_analyze():
    dme = edM.DetectionMethodEvaluation(
        output_dir, number_of_muons, steps, step_size, scoop_hosts)
    file_out = os.path.join(output_dir, "nsb_35e6_precision_results.csv")
    results = dme.analyze(file_out)
    np.testing.assert_almost_equal(
        results['avg_precision'],
        200/3,
        5)


def test_plot_sensitivity_precision():
    dme = edM.DetectionMethodEvaluation(
        output_dir, number_of_muons, steps, step_size, scoop_hosts)
    results = {
        "avg_precision": 90,
        "std_precision": 10,
        "avg_sensitivity": 90,
        "std_sensitivity": 10,
        "precisions": np.array([80, 100]),
        "sensitivities": np.array([80, 100])
    }
    dme.plot_sensitivity_precision(results, output_dir)
    path = os.path.join(output_dir, "sensitivity.png")
    path2 = os.path.join(output_dir, "precision.png")
    assert os.path.exists(path) and os.path.exists(path2)


def test_dummy_delete_files():
    shutil.rmtree(output_dir)


def test_one_nsb_rate():
    dme = edM.DetectionMethodEvaluation(
        output_dir, 100, steps, step_size, scoop_hosts)
    dme.one_nsb_rate(output_dir, 35e6)
    wild_card_path = os.path.join(output_dir, "*")
    i = 0
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == 4


def test_dummy_delete_files2():
    shutil.rmtree(output_dir)


def test_plot_different_NSB():
    dme = edM.DetectionMethodEvaluation(
        output_dir, 10, steps, step_size, scoop_hosts)
    NSB_rates = [1, 2, 3]
    precisions = [99, 98, 97]
    sensitivities = [100, 50, 80]
    muonCounts = [12, 12, 12]
    dme.plot_different_NSB(NSB_rates, precisions, sensitivities, muonCounts)
    number_of_elements = len(os.listdir(output_dir))
    assert number_of_elements == 2

def test_dummy_delete_files3():
    shutil.rmtree(output_dir)


def test_multiple_nsb_rates():
    dme = edM.DetectionMethodEvaluation(
        output_dir, 10, 5, 1.05, scoop_hosts)
    dme.multiple_nsb_rates()
    number_of_elements = len(os.listdir(output_dir))
    assert number_of_elements == 7


def test_dummy_delete_files4():
    shutil.rmtree(output_dir)