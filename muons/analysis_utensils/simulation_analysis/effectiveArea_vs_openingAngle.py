import matplotlib
matplotlib.use('agg')
import subprocess
import docopt
import numpy as np
import os
from shutil import copy
import shutil
import pandas
import scoop
from muons.muon_ring_simulation import many_simulations as ms
import re
import photon_stream as ps
from muons.detection import detection
from muons.muon_ring_fuzzyness import muon_ring_fuzzyness as mrf
import glob
import matplotlib.pyplot as plt


class EffectiveArea_vs_OpeningAngle:

    """Simulate, analyze and plot effective areas vs opening angle"""

    def __init__(
        self,
        scoop_hosts,
        preferencesFile,
        steps,
        output_dir
    ):
        self.scoop_hosts = scoop_hosts
        self.preferencesFile = preferencesFile
        self.steps = steps
        self.output_dir = output_dir
        self.check_if_correct_variables()
        self.simulation_dir = os.path.join(output_dir, "simulations")
        self.preferences = self.read_preferencesFile()


    def check_if_correct_variables(self):
        if not os.path.exists(self.scoop_hosts):
            raise ValueError(
                'Entered path to scoop_hosts.txt must exist')
        if not type(self.scoop_hosts) == str:
            raise ValueError(
            'Entered path to scoop_hosts needs to ba a string')
        if not os.path.exists(self.preferencesFile):
            raise ValueError(
            'Entered path to preferencesFile needs to ba a string')
        if not type(self.preferencesFile) == str:
            raise ValueError(
            'Entered path to preferencesFile needs to ba a string')
        if not type(self.steps) == int:
            raise ValueError(
            'Entered "steps" value needs to ba an integer')
        if not type(self.output_dir) == str:
            raise ValueError(
            'Entered path to output_dir needs to ba a string')


    """ ##################### Simulating ############################ """


    def read_preferencesFile(
        self
    ):
        preferences = {}
        with open(self.preferencesFile, "r") as fIn:
            for line in fIn:
                (key, value) = line.split("= ")
                preferences[key] = value
        return preferences


    def calculate_stepSize(
        self
    ):
        preferences = self.read_preferencesFile()
        min_openingAngle = float(
            preferences['--min_opening_angle'].strip("\n"))
        max_openingAngle = float(
            preferences['--max_opening_angle'].strip("\n"))
        stepSize = (max_openingAngle - min_openingAngle)/self.steps
        return stepSize


    def create_outputDir_and_copy_preferencesFile(
        self
    ):
        if not os.path.isdir(self.simulation_dir):
            os.makedirs(self.simulation_dir)
        copy(self.preferencesFile, self.simulation_dir)


    def get_scoop_simulation_scriptPath(
        self
    ):
        filePath = os.path.normpath(os.path.abspath(ms.__file__))
        parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
        simulation_scriptPath = os.path.join(
            parentDir, "scoop_simulate_muon_rings.py")
        return simulation_scriptPath


    def calculate_current_openingAngle(
        self,
        step_number
    ):
        preferences = self.read_preferencesFile()
        min_openingAngle = float(
            preferences['--min_opening_angle'].strip("\n"))
        stepSize = self.calculate_stepSize()
        current_openingAngle = round(
            float(min_openingAngle + step_number*stepSize), 2)
        return current_openingAngle


    def run_single_simulation_with_fixed_openingAngle(
        self,
        step_number
    ):
        simulation_scriptPath = self.get_scoop_simulation_scriptPath()
        scoopList = [
            "python", "-m", "scoop", "--hostfile",
            self.scoop_hosts, simulation_scriptPath
        ]
        current_openingAngle = self.calculate_current_openingAngle(
            step_number)
        dirname = "_".join(["opening_angle", str(current_openingAngle)])
        simulationDir = os.path.join(self.simulation_dir, dirname)
        scoopDictionary = self.read_preferencesFile()
        scoopDictionary["--output_dir"] = simulationDir
        scoopDictionary["--min_opening_angle"] = (
            str(current_openingAngle))
        scoopDictionary["--max_opening_angle"] = (
            str(current_openingAngle))
        for key in scoopDictionary:
            scoopList.append(key)
            scoopList.append(scoopDictionary[key].rstrip('\n'))
        subprocess.call(scoopList)


    def run_multiple_openingAngle_simulations(
        self
    ):
        for step_number in range(self.steps +1):
            self.run_single_simulation_with_fixed_openingAngle(step_number)


    """ ################### Analyzing ##################### """

    def create_jobs_for_scoop(
        self,
        suffix="*/psf*.sim.phs"
    ):
        paths = []
        wild_card_path = os.path.join(self.simulation_dir, suffix)
        for path in glob.glob(wild_card_path, recursive=True):
            paths.append(path)
        return paths


    def run_detection(
        self,
        inpath
    ):
        run = ps.EventListReader(inpath)
        path = os.path.normpath(inpath)
        split_path = path.split(os.sep)
        oa_name = split_path[-2]
        oa = re.split('_',oa_name)[2]
        preferences = self.read_preferencesFile()
        number_of_muons = preferences['--number_of_muons']
        found_muons = 0
        for event in run:
            clusters = ps.PhotonStreamCluster(event.photon_stream)
            muon_props = detection(event, clusters)
            if muon_props["is_muon"]:
                found_muons += 1
        return oa, found_muons, number_of_muons


    def call_scoop_for_analyzing(
        self
    ):
        filePath = os.path.normpath(os.path.abspath(__file__))
        currentDirectory = os.path.normpath(os.path.join(filePath, os.pardir))
        scoop_scriptName = os.path.join(
            currentDirectory, "scoop_effectiveArea_vs_openingAngle.py")
        commandList = [
            "python", "-m", "scoop", "--hostfile",
            self.scoop_hosts, scoop_scriptName, "--simulation_dir",
            self.simulation_dir, "--scoop_hosts", self.scoop_hosts,
            "--preferencesFile", self.preferencesFile, "--steps",
            str(self.steps), "--output_dir", self.output_dir
        ]
        subprocess.call(commandList)


    """ ################# Plotting ########################## """

    def read_openingAngle_dataFrame(self):
        filename = "effective_area_vs_oa.csv"
        effective_area_oa_csvPath = os.path.join(self.simulation_dir, filename)
        dataFrame = pandas.read_csv(effective_area_oa_csvPath)
        opening_angle = dataFrame['opening_angle'].values
        detected_muonCount = dataFrame['detected_muons'].values
        simulated_muonCount = dataFrame['simulated_muons'].values
        return opening_angle, detected_muonCount, simulated_muonCount


    def find_area(self):
        aperture_radius = float(self.preferences['--fact_aperture_radius'])
        area = np.pi * np.square(aperture_radius)
        return area


    def calculate_effective_area(
        self,
        area,
        detected_muonCount,
        simulated_muonCount):
        effective_area = (
            np.divide(detected_muonCount, simulated_muonCount) * area)
        return effective_area


    def plot_effective_area_vs_opening_angle(
        self,
        opening_angle,
        effective_area
    ):
        plt.scatter(opening_angle, effective_area)
        plt.grid()
        plt.xlim(opening_angle.min()-0.1, opening_angle.max() + 0.1)
        plt.xlabel("openingAngle /deg")
        plt.ylabel("effectiveArea")
        plt.yscale('log')
        plotPath = os.path.join(
            self.output_dir, "effective_area_vs_opening_angle.png")
        plt.savefig(plotPath, bbox_inches="tight")
        plt.close("all")


    def plotting_main(self):
        opening_angle, detected_muonCount, simulated_muonCount = (
            self.read_openingAngle_dataFrame())
        area = self.find_area()
        effective_area = self.calculate_effective_area(
            area, detected_muonCount, simulated_muonCount)
        self.plot_effective_area_vs_opening_angle(
            opening_angle, effective_area)



    """ ################### Main call ############################"""


    def remove_simulation_folder(self):
        shutil.rmtree(self.simulation_dir)


    def investigate_effectiveArea_vs_openingAngle(self):
        self.run_multiple_openingAngle_simulations()
        self.call_scoop_for_analyzing()
        self.plotting_main()
        self.remove_simulation_folder()