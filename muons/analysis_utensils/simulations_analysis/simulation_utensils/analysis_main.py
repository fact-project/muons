"""
Simulate and analyze fuzz vs PSF and effective_area vs opening_angle. Create 
also the correct folder structure.

Usage: 'python'
    simulate_and_find_effective_area_vs_oa.py --scoop_hostfilePath=NME [--maximum_PSF=INT] [--steps_fuzz_psf=INT] [--steps_oa=INT] [--job=NME]

Options:
    --scoop_hostfilePath=PTH    Path to scoop_hosts.txt
    --maximum_PSF=INT           [default: 0.25] Maximum PSF to be simulated
    --steps_fuzz_psf=INT        [default: 20] Number of steps to reach maximum PSF
    --steps_oa                  [default: 20] Number of steps in simulating opening angle.
    --job=NME                   [default: both] what analysist to do. Options: PSF_fuzz or effectiveArea_oa
"""
import subprocess
import os
import pandas
import docopt


 def read_preferencesFile():
    filePath = os.path.normpath(os.path.abspath(__file__))
    parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
    preferencesFile_path = os.path.join(parentDir, "preferences_file.csv")
    preferences = {}
    with open(preferencesFile_path) as fIn:
        for line in fIn:
            (key, value) = line.split("= ")
            preferences[key] = value
    outputs_parent = preferences['--output_dir'].strip('\n')
    return outputs_parent, preferencesFile_path


def run_multiple_PSF_simulation(
    preferencesFile_path,
    arguments,
    output):
    print("###### Start simulations for multiple PSF #####")
    output_dir = os.path.join(output, "")
    maximum_PSF = arguments['--maximum_PSF']
    steps = arguments['--steps']
    scriptName = "multiple_PSF.py"
    functionCall = [
        "python", scriptName, "--preferencesFile_path",
        preferencesFile_path, "--maximum_PSF",
        maximum_PSF, "--steps", steps,
        "--output_dir", output_dir
    ]
    subprocess.call(functionCall)
    print("##### Finished simulations #####")


def run_PSF_fuzz_analysis(simulation_dir, scoop_hosts):
    print("###### Start PSF_fuzz analysis #####")
    scriptName = "compare_psf_fuzz.py"
    functionCall = [
        "python", "-m", "--hostfile", scoop_hosts,
        scriptName, "--simulation_dir", simulation_dir,
        "--output_dir", simulation_dir
    ]
    subprocess.call(functionCall)
    print("##### Finished analysis #####")


def simulate_effective_area_vs_opening_angle(
    preferences_file,
    steps,
    output_dir
):
    print("##### Start simulation for different opening angle #####")
    simulation_scriptName = "multiple_openingAngle.py"
    simulation_command = [
        "python", simulation_scriptName, "--preferencesFile_path",
        preferences_file, "--steps", steps, "--output_dir", output_dir
    ]
    subprocess.call(simulation_command)
    print("##### Finished simulations #####")


def analyze_effective_area_vs_opening_angle(
    scoop_hosts,
    number_of_muons,
    simulation_dir
):
    print("##### Start effective area vs opening angle analysis #####")
    analysis_scriptName = "compare_opening_angle.py"
    analyze_command = [
        "python", "-m", "scoop", "--hostfile", scoop_hosts,
        analyze_command, "--simulation_dir", simulation_dir,
        "--output_dir", simulation_dir, "--number_of_muons",
        number_of_muons
    ]
    subprocess.call(analyze_command)
    print("###### Finished analysis ######")


def get_plotting_script_path():
    filePath = os.path.normpath(os.path.abspath(mrf.__file__))
    file_parentDir = os.path.normpath(os.path.join(filePath, os.pardir))
    simulation_analysis_dir = os.path.normpath(os.path.join(
        file_parentDir, os.pardir))
    plotting_dir = os.path.join(simulation_analysis_dir, "plotting")
    plot_all_path = os.path.join(plotting_dir, "plot_all.py")
    return plot_all_path


def do_plotting(plot_all_path):
    plot_command = [
        "python", plot_all_path, "--simulation_dir", simulation_dir]
    subprocess.call(plot_command)



def main():
    try:
        arguments = docopt.docopt(__doc__)
        outputs_parent, preferencesFile_path = read_preferencesFile()
        maximum_PSF = arguments["--maximum_PSF"]
        steps_fuzz_psf = arguments["--steps_fuzz_psf"]
        steps_oa = arguments["--steps_oa"]
        job = arguments['--job']
        scoop_hosts = arguments["--scoop_hostfilePath"]
        output_dir_PSF_fuzz = os.path.join(
            outputs_parent, "PSF_fuzz_comparison")
        effectiveArea_oa_output = ps.path.join(
            outputs_parent, "effective_area_vs_oa")
        if job == "PSF_fuzz":
            run_multiple_PSF_simulation(
                preferencesFile_path, arguments, output_dir_PSF_fuzz)
            run_PSF_fuzz_analysis(output_dir_PSF_fuzz, scoop_hosts)
        elif job == "effectiveArea_oa":
            simulate_effective_area_vs_opening_angle(
                preferences_file,
                steps_oa,
                effectiveArea_oa_output)
            analyze_effective_area_vs_opening_angle(
                scoop_hosts,
                number_of_muons,
                effectiveArea_oa_output)
        elif job == "both":
            run_multiple_PSF_simulation(
                preferencesFile_path, arguments, output_dir_PSF_fuzz)
            run_PSF_fuzz_analysis(output_dir_PSF_fuzz, scoop_hosts)
            simulate_effective_area_vs_opening_angle(
                preferences_file,
                steps_oa,
                effectiveArea_oa_output)
            analyze_effective_area_vs_opening_angle(
                scoop_hosts,
                number_of_muons,
                effectiveArea_oa_output)
        else:
            raise Exception('Wrong "--job" parameter')
        plot_all_path = get_plotting_script_path()
        do_plotting(plot_all_path)
    except docopt.DocoptExit as e:
        print(e)



if __name__ == '__main__':
    main()