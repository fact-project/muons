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
import acceptance_vs_openingAngle as evo


scoop_hosts = os.path.join(fileDir, "resources", "scoop_hosts.txt")
preferencesFile = os.path.join(fileDir, "resources", "preferences_file.csv")
steps = 3
output_dir = os.path.join(fileDir, "resources", "testDir")
simulationDir = os.path.join(output_dir, "simulations")


def test_check_if_correct_variables_with_correct_variables():
    try:
        EvO = evo.Acceptance_vs_OpeningAngle(
            scoop_hosts,
            preferencesFile,
            steps,
            output_dir)
        error = False
        EvO.check_if_correct_variables()
    except ValueError:
        error = True
    assert error == False


def test_check_if_correct_variables_wrong_scoop_hosts():
    try:
        EvO = evo.Acceptance_vs_OpeningAngle(
            3,
            preferencesFile,
            steps,
            output_dir)
        error = False
        EvO.check_if_correct_variables()
    except ValueError:
        error = True
    assert error == True


def test_check_if_correct_variables_wrong_scoop_hosts():
    try:
        EvO = evo.Acceptance_vs_OpeningAngle(
            "/foo/bar/",
            preferencesFile,
            steps,
            output_dir)
        error = False
        EvO.check_if_correct_variables()
    except ValueError:
        error = True
    assert error == True


def test_check_if_correct_variables_wrong_preferencesFile():
    try:
        EvO = evo.Acceptance_vs_OpeningAngle(
            scoop_hosts,
            3,
            steps,
            output_dir)
        error = False
        EvO.check_if_correct_variables()
    except ValueError:
        error = True
    assert error == True


def test_check_if_correct_variables_wrong_preferencesFile():
    try:
        EvO = evo.Acceptance_vs_OpeningAngle(
            scoop_hosts,
            "/foo/bar",
            steps,
            output_dir)
        error = False
        EvO.check_if_correct_variables()
    except ValueError:
        error = True
    assert error == True


def test_check_if_correct_variables_wrong_steps():
    try:
        EvO = evo.Acceptance_vs_OpeningAngle(
            scoop_hosts,
            preferencesFile,
            "steps",
            output_dir)
        error = False
        EvO.check_if_correct_variables()
    except (TypeError, ValueError):
        error = True
    assert error == True


def test_check_if_correct_variables_wrong_ouput_dir():
    try:
        EvO = evo.Acceptance_vs_OpeningAngle(
            scoop_hosts,
            preferencesFile,
            steps,
            3)
        error = False
        EvO.check_if_correct_variables()
    except ValueError:
        error = True
    assert error == True


def test_read_preferencesFile_keys():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    preferences = EvO.read_preferencesFile()
    number_of_keys = list(preferences.keys())
    assert len(number_of_keys) == 11


def test_read_preferencesFile_values():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    preferences = EvO.read_preferencesFile()
    number_of_keys = list(preferences.values())
    assert len(number_of_keys) == 11


def test_calculate_stepSize():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    real_stepSize = (1.6 - 0.4)/3
    calculated_stepSize = EvO.calculate_stepSize()
    assert real_stepSize == calculated_stepSize


def test_create_outputDir_and_copy_preferencesFile():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    EvO.create_outputDir_and_copy_preferencesFile()
    existing = False
    new_preferences_path = os.path.join(output_dir, preferencesFile)
    if os.path.exists(new_preferences_path):
        existing = True
    assert existing == True


def test_get_scoop_simulation_scriptPath():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    simulation_scriptPath = EvO.get_scoop_simulation_scriptPath()
    existing = False
    if os.path.exists(simulation_scriptPath):
        existing = True
    assert existing == True


def test_calculate_current_openingAngle():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    step_number = 1
    openingAngle = EvO.calculate_current_openingAngle(step_number)
    assert openingAngle == 0.8


def test_run_single_simulation_with_fixed_openingAngle():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    step_number = 1
    EvO.run_single_simulation_with_fixed_openingAngle(step_number)
    existing = False
    simulation_dir = os.path.join(simulationDir, "opening_angle_0.8")
    if os.path.isdir(simulation_dir):
        existing = True
    assert existing == True


def test_run_multiple_openingAngle_simulations():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    EvO.run_multiple_openingAngle_simulations()
    wild_card_path = os.path.join(simulationDir, "opening_angle_*")
    i = 0
    for folder in glob.glob(wild_card_path, recursive=True):
        i += 1
    assert steps == 3


def test_create_jobs_for_scoop():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    paths = EvO.create_jobs_for_scoop()
    assert steps + 1 == len(list(paths))


def test_run_detection_finding_oa():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    inpath = os.path.join(
        simulationDir, "opening_angle_0.8", "psf_0.sim.phs")
    openingAngle, found_muons, number_of_muons = EvO.run_detection(inpath)
    assert openingAngle


def test_call_scoop_for_analyzing():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    EvO.call_scoop_for_analyzing()
    Acceptance_vs_openingAngle_csvPath = os.path.join(
        simulationDir, "acceptance_vs_oa.csv")
    existing = False
    if os.path.exists(Acceptance_vs_openingAngle_csvPath):
        existing = True
    assert existing == True


def test_read_openingAngle_dataFrame_check_muonCount():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    opening_angle, detected_muons, simulated_muons = (
        EvO.read_openingAngle_dataFrame())
    assert (simulated_muons == [30, 30, 30, 30]).all()


def test_read_openingAngle_dataFrame_check_openingAngle():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    opening_angle, detected_muons, simulated_muons = (
        EvO.read_openingAngle_dataFrame())
    assert len(opening_angle) == steps + 1


def test_find_area():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    area = EvO.find_area()
    np.testing.assert_almost_equal(
        area/np.pi,
        np.square(1.965),
        7
    )


def test_calculate_acceptance():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    area = 1
    detected_muonCount = 10
    simulated_muonCount = 10
    acceptance = EvO.calculate_acceptance(
        area, detected_muonCount, simulated_muonCount)
    np.testing.assert_almost_equal(
        acceptance,
        0,
        5)


def test_plot_acceptance_vs_opening_angle():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    opening_angle = np.array([0.4, 0.8, 1.2, 1.6])
    acceptance = np.array([8, 12, 14, 16])
    detected_muonCount = np.array([10, 9, 8, 7])
    EvO.plot_acceptance_vs_opening_angle(
        opening_angle, acceptance, detected_muonCount)
    path_to_plot = os.path.join(
        output_dir, "acceptance_vs_opening_angle.png")
    if os.path.exists(path_to_plot):
        existing = True
    assert existing == True


def test_plotting_main():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    EvO.plotting_main()
    existing = False
    path_to_plot = os.path.join(
        output_dir, "acceptance_vs_opening_angle.png")
    if os.path.exists(path_to_plot):
        existing = True
    assert existing == True


def test_investigate_Acceptance_vs_openingAngle():
    EvO = evo.Acceptance_vs_OpeningAngle(
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir)
    EvO.investigate_acceptance_vs_openingAngle()
    wild_card_path = os.path.join(output_dir, "*")
    i = 0
    for path in glob.glob(wild_card_path):
        i += 1
    assert i == 2


def test_dummy_delete_files():
    shutil.rmtree(output_dir)
