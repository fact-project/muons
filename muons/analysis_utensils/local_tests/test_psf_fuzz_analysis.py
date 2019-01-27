import sys
import os
import shutil
import glob
filePath = os.path.normpath(os.path.abspath(__file__))
fileDir = os.path.normpath(os.path.join(filePath, os.pardir))
parentDir = os.path.normpath(os.path.join(
    fileDir, os.pardir))
scriptDir = os.path.join(parentDir, "simulation_analysis")
sys.path.insert(0, scriptDir)
import psf_fuzz_analysis as pfa
import pandas
import numpy as np
import photon_stream as ps
from numbers import Number


output_dir = os.path.join(fileDir, "resources", "testDir")
scoop_hosts = os.path.join(fileDir, "resources", "scoop_hosts.txt")
preferencesFile = os.path.join(fileDir, "resources", "preferences_file.csv")
maximum_PSF = 0.1
steps = 10
simulation_dir = os.path.join(output_dir, "simulations")
fuzz_resultDir = os.path.join(output_dir, "fuzzResults")

def test_checkInputValidity_AllCorrect():
    try:
        Analysis = pfa.PSF_FuzzAnalysis(
            preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
        Analysis.checkInputValidity()
        error = False
    except ValueError:
        error = True
    assert error == False


def test_checkInputValidity_wrongPreferences():
    try:
        Analysis = pfa.PSF_FuzzAnalysis(
            "/foo/bar", maximum_PSF, steps, scoop_hosts, output_dir)
        Analysis.checkInputValidity()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_checkInputValidity_wrongPSF():
    try:
        Analysis = pfa.PSF_FuzzAnalysis(
            preferencesFile, "5", steps, scoop_hosts, output_dir)
        Analysis.checkInputValidity()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_checkInputValidity_wrongSteps():
    try:
        Analysis = pfa.PSF_FuzzAnalysis(
            preferencesFile, maximum_PSF, 3.5, scoop_hosts, output_dir)
        Analysis.checkInputValidity()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_checkInputValidity_wrongScoop():
    try:
        Analysis = pfa.PSF_FuzzAnalysis(
            preferencesFile, maximum_PSF, steps, "/foo/bar", output_dir)
        Analysis.checkInputValidity()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_checkInputValidity_wrongSteps():
    try:
        Analysis = pfa.PSF_FuzzAnalysis(
            preferencesFile, maximum_PSF, 3.5, scoop_hosts, output_dir)
        Analysis.checkInputValidity()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_checkInputValidity_wrongOutput():
    try:
        Analysis = pfa.PSF_FuzzAnalysis(
            preferencesFile, maximum_PSF, 3.5, scoop_hosts, 3)
        Analysis.checkInputValidity()
        error = False
    except ValueError:
        error = True
    assert error == True


def test_calculate_stepSize():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    stepSize = Analysis.calculate_stepSize()
    np.testing.assert_almost_equal(
        stepSize,
        0.01,
        2)


def test_readPreferences_keys():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    preferences = Analysis.readPreferences()
    number_of_keys = list(preferences.keys())
    assert len(number_of_keys) == 11


def test_readPreferences_values():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    preferences = Analysis.readPreferences()
    number_of_values = list(preferences.values())
    print(preferences)
    assert len(number_of_values) == 11


def test_get_scoop_simulation_scriptPath():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    simulation_scriptPath = Analysis.get_scoop_simulation_scriptPath()
    existing = False
    if os.path.exists(simulation_scriptPath):
        existing = True
    assert existing == True


def test_call_scoop_once():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    Analysis.call_scoop_once(step_number=0)
    path = os.path.join(simulation_dir, "iterStep_0", "psf_0.0.sim.phs")
    existing = False
    if os.path.exists(path):
        existing = True
    assert existing == True


def test_multiple_scoop_calls():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    Analysis.multiple_scoop_calls()
    wild_card_path = os.path.join(simulation_dir, "*")
    i = 0
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == steps


def test_find_all_simulation_files():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    Analysis.find_all_simulation_files()
    wild_card_path = os.path.join(simulation_dir, "*", "*.sim.phs")
    i = 0
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == steps


def test_get_reconstructed_muons_info():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    muon_props = {
        "muon_ring_cx": 0,
        "muon_ring_cy": 0,
        "muon_ring_r": 1,
        "mean_arrival_time_muon_cluster": 2,
        "muon_ring_overlapp_with_field_of_view": 3,
        "number_of_photons": 3
    }
    event_id = 3
    muon_event_info = Analysis.get_reconstructed_muons_info(
        muon_props, event_id)
    assert len(muon_event_info) == 7


def test_get_fuzziness_parameters():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    simulationFile = os.path.join(
        fileDir, "resources", "100simulations_psf0.0.sim.phs")
    run = ps.EventListReader(simulationFile)
    for i, event in enumerate(run):
        if i == 47:
            photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
    muon_props = {
        "muon_ring_cx": 0,
        "muon_ring_cy": 0,
        "muon_ring_r": 1,
        "mean_arrival_time_muon_cluster": 2,
        "muon_ring_overlapp_with_field_of_view": 3,
        "number_of_photons": 3
    }
    normed_response, fuzziness_stdParam = Analysis.get_fuzziness_parameters(
        photon_clusters, muon_props)
    assert (
        isinstance(normed_response, Number) and 
        isinstance(fuzziness_stdParam, Number)
    )


def test_save_muon_events():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    reconstructed_muon_events = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1]
    ]
    simulationFile = os.path.join(
        fileDir, "resources", "100simulations_psf0.0.sim.phs")
    Analysis.save_muon_events(
        reconstructed_muon_events, simulationFile, "hough")
    reconstructedEvent_path = os.path.join(
        fileDir, "resources", "hough_reconstructed_muon_events.csv")
    existing = False
    if os.path.exists(reconstructedEvent_path):
        existing = True
    os.remove(reconstructedEvent_path)
    assert existing == True


def test_using_hough_extraction():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    simulationFile = os.path.join(
        fileDir, "resources", "100simulations_psf0.0.sim.phs")
    run = ps.EventListReader(simulationFile)
    event_id = 3
    for i, event in enumerate(run):
        if i == event_id:
            photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
    muon_props = {
        "muon_ring_cx": 0,
        "muon_ring_cy": 0,
        "muon_ring_r": 1,
        "mean_arrival_time_muon_cluster": 2,
        "muon_ring_overlapp_with_field_of_view": 3,
        "number_of_photons": 3
    }
    returns = Analysis.using_hough_extraction(
        muon_props, photon_clusters, event_id)
    assert len(returns) == 3


def test_using_ringM_extraction():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    simulationFile = os.path.join(
        fileDir, "resources", "100simulations_psf0.0.sim.phs")
    run = ps.EventListReader(simulationFile)
    event_id = 3
    for i, event in enumerate(run):
        if i == event_id:
            photon_clusters = ps.PhotonStreamCluster(event.photon_stream)
    muon_props = {
        "muon_ring_cx": 0,
        "muon_ring_cy": 0,
        "muon_ring_r": 1,
        "mean_arrival_time_muon_cluster": 2,
        "muon_ring_overlapp_with_field_of_view": 3,
        "number_of_photons": 3
    }
    returns = Analysis.using_ringM_extraction(
        muon_props, photon_clusters, event_id)
    assert len(returns) == 3


def test_get_point_spread_function():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    simulationFile = os.path.join(
        fileDir, "resources", "100simulations_psf0.0.sim.phs")
    psf = Analysis.get_point_spread_function(simulationFile)
    assert psf == 0


def test_save_fuzz_info():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    psf = [0, 0, 0, 0]
    extractionMethod = "hough"
    fuzzParameter = "response"
    muonCount = [3, 4, 5, 6]
    fuzz_avg = [0.5, 0.5, 0.5, 0.5]
    stdev_fuzz = [0.5, 0.5, 0.5, 0.5]
    filename = "_".join([fuzzParameter, "fuzzResults.csv"])
    filepath = os.path.join(fuzz_resultDir, extractionMethod, filename)
    Analysis.save_fuzz_info(
        psf, extractionMethod, fuzzParameter,
        muonCount, fuzz_avg, stdev_fuzz)
    existing = False
    if os.path.exists(filepath):
        existing = True
    assert existing == True


def test_save_fuzz_info():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    psf = [0, 0, 0, 0]
    extractionMethod = "hough"
    fuzzParameter = "response"
    muonCount = [3, 4, 5, 6]
    fuzz_avg = [0.5, 0.5, 0.5, 0.5]
    stdev_fuzz = [0.5, 0.5, 0.5, 0.5]
    filename = "_".join([fuzzParameter, "fuzzResults.csv"])
    filepath = os.path.join(fuzz_resultDir, extractionMethod, filename)
    Analysis.save_fuzz_info(
        psf, extractionMethod, fuzzParameter,
        muonCount, fuzz_avg, stdev_fuzz)
    df = pandas.read_csv(filepath)
    assert (df['point_spread_function'] == 0).all()


def test_calculate_average_and_stdev():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    fuzz = [1,1,1,1,1,1,1,1,1]
    average_fuzz, fuzz_stdev = Analysis.calculate_average_and_stdev(fuzz)
    assert average_fuzz == 1


def test_calculate_average_and_stdev():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    fuzz = [1,1,1,1,1,1,1,1,1]
    average_fuzz, fuzz_stdev = Analysis.calculate_average_and_stdev(fuzz)
    assert fuzz_stdev == 0


def test_extract_fuzzParam_from_single_run1():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    simulationFile = os.path.join(
        fileDir, "resources", "100simulations_psf0.0.sim.phs")
    returns = Analysis.extract_fuzzParam_from_single_run(simulationFile)
    assert len(returns.keys()) == 14


def test_extract_fuzzParam_from_single_run2():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    simulationFile = os.path.join(
        fileDir, "resources", "100simulations_psf0.0.sim.phs")
    returns = Analysis.extract_fuzzParam_from_single_run(simulationFile)
    assert len(returns.values()) == 14


def test_call_scoop_for_all1():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    Analysis.call_scoop_for_all()
    filename = "_".join(["response", "fuzzResults.csv"])
    filepath = os.path.join(fuzz_resultDir, "ringM", filename)
    existing = False
    if os.path.exists(filepath):
        existing = True
    assert existing == True


def test_call_scoop_for_all2():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    Analysis.call_scoop_for_all()
    filename = "_".join(["stdev", "fuzzResults.csv"])
    filepath = os.path.join(fuzz_resultDir, "ringM", filename)
    existing = False
    if os.path.exists(filepath):
        existing = True
    assert existing == True


def test_call_scoop_for_all3():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    Analysis.call_scoop_for_all()
    filename = "_".join(["response", "fuzzResults.csv"])
    filepath = os.path.join(fuzz_resultDir, "hough", filename)
    existing = False
    if os.path.exists(filepath):
        existing = True
    assert existing == True


def test_call_scoop_for_all4():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    Analysis.call_scoop_for_all()
    filename = "_".join(["stdev", "fuzzResults.csv"])
    filepath = os.path.join(fuzz_resultDir, "hough", filename)
    existing = False
    if os.path.exists(filepath):
        existing = True
    assert existing == True


def test_call_scoop_for_all5():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    Analysis.call_scoop_for_all()
    wild_card_path = os.path.join(
        simulation_dir, "*","ringM_reconstructed_muon_events.csv")
    i = 0
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == 10


def test_call_scoop_for_all6():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    Analysis.call_scoop_for_all()
    wild_card_path = os.path.join(
        simulation_dir, "*","hough_reconstructed_muon_events.csv")
    i = 0
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == 10


def test_call_scoop_for_all7():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    Analysis.call_scoop_for_all()
    wild_card_path = os.path.join(fuzz_resultDir, "*", "*")
    i = 0
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == 4


def test_plot_psf_fuzz1():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    psf_fuzz_csv_path = os.path.join(
        fileDir, "resources", "response_fuzzResults.csv")
    Analysis.plot_psf_fuzz(psf_fuzz_csv_path, "response", "ringM")
    checkPath = os.path.join(
        output_dir, "Plots", "ringM", "response_vs_psf.png")
    existing = False
    if os.path.exists(checkPath):
        existing = True
    shutil.rmtree(os.path.join(output_dir, "Plots"))
    assert existing == True


def test_plot_psf_fuzz2():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    psf_fuzz_csv_path = os.path.join(
        fileDir, "resources", "response_fuzzResults.csv")
    Analysis.plot_psf_fuzz(psf_fuzz_csv_path, "stdev", "hough")
    checkPath = os.path.join(
        output_dir, "Plots", "hough", "stdev_vs_psf.png")
    existing = False
    if os.path.exists(checkPath):
        existing = True
    shutil.rmtree(os.path.join(output_dir, "Plots"))
    assert existing == True


def test_plot_absolute_detected_muons():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    psf_fuzz_csv_path = os.path.join(
        fileDir, "resources", "response_fuzzResults.csv")
    Analysis.plot_absolute_detected_muons(psf_fuzz_csv_path, "hough")
    filename = "hough_absolute_detected_muons.png"
    plotPath = os.path.join(output_dir, "Plots", filename)
    if os.path.exists(plotPath):
        existing = True
    shutil.rmtree(os.path.join(output_dir, "Plots"))
    assert existing == True


def test_plot_effective_area_vs_psf():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    psf_fuzz_csv_path = os.path.join(
        fileDir, "resources", "response_fuzzResults.csv")
    Analysis.plot_effective_area_vs_psf(psf_fuzz_csv_path, "ringM")
    plotPath = os.path.join(
        output_dir, "Plots", "ringM", "effective_area_vs_psf.png")
    existing = False
    if os.path.exists(plotPath):
        existing = True
    shutil.rmtree(os.path.join(output_dir, "Plots"))
    assert existing == True


def test_plot_psf_fuzz_hough_ringM_comparison():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    psf_fuzz_csv_path = os.path.join(
        fileDir, "resources", "response_fuzzResults.csv")
    psf_fuzz_csv_path1 = os.path.join(
        fileDir, "resources", "stdev_fuzzResults.csv")
    Analysis.plot_psf_fuzz_hough_ringM_comparison(
        psf_fuzz_csv_path, psf_fuzz_csv_path1, "stdev")
    exists = False
    plotPath = os.path.join(
        output_dir, "Plots", "hough_ringM_psf_stdev_comparison.png")
    if os.path.exists(plotPath):
        existing = True
    shutil.rmtree(os.path.join(output_dir, "Plots"))
    assert existing == True


def test_plot_all1():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    Analysis.plot_all()
    i = 0
    wild_card_path = os.path.join(output_dir, "Plots", "*.png")
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == 4


def test_plot_all2():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    Analysis.plot_all()
    i = 0
    wild_card_path = os.path.join(output_dir, "Plots", "*", "*.png")
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == 10


def test_read_dataFrame():
    psf_fuzz_csv = os.path.join(fileDir, "resources", "psf_fuzz.csv")
    CurveFit = pfa.CurveFitting(
        psf_fuzz_csv, "stdev", "ringM", output_dir)
    psf, fuzz = CurveFit.read_dataFrame()
    assert len(psf) == 21


def test_only_some_psf():
    psf_fuzz_csv = os.path.join(fileDir, "resources", "psf_fuzz.csv")
    CurveFit = pfa.CurveFitting(
        psf_fuzz_csv, "stdev", "ringM", output_dir)
    dataFrame = pandas.read_csv(psf_fuzz_csv)
    psf = np.rad2deg(dataFrame['point_spread_function'])
    fuzz = np.rad2deg(dataFrame['average_fuzz'])
    psfN, fuzzN = CurveFit.only_some_psf(psf, fuzz)
    assert len(psfN) == 10


def test_plot_curve_fit():
    psf_fuzz_csv = os.path.join(fileDir, "resources", "psf_fuzz.csv")
    CurveFit = pfa.CurveFitting(
        psf_fuzz_csv, "stdev", "ringM", output_dir)
    path = os.path.join(output_dir, "Plots", "ringM", "stdev_curve_fit.png")
    CurveFit.plot_curve_fit()
    assert os.path.exists(path)


def test_save_function():
    psf_fuzz_csv = os.path.join(fileDir, "resources", "psf_fuzz.csv")
    CurveFit = pfa.CurveFitting(
        psf_fuzz_csv, "stdev", "ringM", output_dir)
    path = os.path.join(output_dir, "Plots", "ringM", "stdev_function_fit.csv")
    CurveFit.save_function()
    assert os.path.exists(path)


def test_dummy_delete_files1():
    shutil.rmtree(output_dir)


def test_call_all():
    Analysis = pfa.PSF_FuzzAnalysis(
        preferencesFile, maximum_PSF, steps, scoop_hosts, output_dir)
    Analysis.call_all()
    wild_card_path = os.path.join(output_dir, "*")
    i = 0
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == 3


def test_dummy_delete_files2():
    shutil.rmtree(output_dir)