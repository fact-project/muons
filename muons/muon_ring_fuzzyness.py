import photon_stream as ps
import muons
import numpy as np
import csv
import os
import os.path
import sys
import json
from pathlib import Path


def standard_deviation(point_cloud, muon_props):
    x_loc = point_cloud[:, 0]
    y_loc = point_cloud[:, 1]
    difference = [x_loc - muon_props["muon_ring_cx"],
                  y_loc - muon_props["muon_ring_cy"]]
    deviation_from_fit = (np.sqrt(np.square(difference[0])
                          + np.square(difference[1]))
                          - muon_props["muon_ring_r"])
    real_std = np.std(deviation_from_fit)
    return real_std


def muon_ring_std_event(clusters, muon_props):
    full_cluster_mask = clusters.labels >= 0
    number_of_photons = full_cluster_mask.sum()
    flat_photon_stream = clusters.point_cloud
    point_cloud = flat_photon_stream[full_cluster_mask]
    real_std = standard_deviation(point_cloud, muon_props)
    return real_std

"""
def muon_ring_std_run(path):
    run = ps.EventListReader(path)
    average_run_dev = 0
    hist_data = []
    muon_count = 0
    for events, event in enumerate(run):
        clusters = ps.PhotonStreamCluster(event.photon_stream)
        muon_props = muons.extraction.detection(event, clusters)
        real_std_event= muon_ring_std_event(event)[0]
        muon_count += muon_ring_std_event(event)[1]
        if real_std_event != 0:
            hist_data.append(real_std_event)
    average_run = np.average(hist_data)
    if events != 0:
        percent = (muon_count/events)*100
    print("Finished run ", "Events: ", events,
     "muons: ", muon_count, "efficiency: ", percent)
    return average_run
"""

def create_jobs(muon_dir, output_dir, suffix=".phs.jsonl.gz"):
    jobs = []
    wild_card_path = os.path.join(muon_dir, "*", "*", "*", "*"+suffix)
    for path in glob.glob(wild_card_path):
        job = {}
        job["input_path"] = path
        fact_path = fact.path.parse(path)
        job["output_path"] = fact.path.tree_path(
            night=fact_path["night"],
            run=fact_path["run"],
            suffix=".muon.fuzz.csv",
            prefix=output_dir)
        jobs.append(job)
    return jobs


def run_job(inpath, outpath):
    results = []
    run = ps.EventListReader(inpath)
    number_muons = 0
    for event in run:
        clusters = ps.PhotonStreamCluster(event.photon_stream)
        random_state = np.random.get_state()
        np.random.seed(event.observation_info.event)
        muon_props = muons.extraction.detection(event, clusters)
        np.random.set_state(random_state)
        if muon_props["is_muon"]:
            std_photons_on_ring = muon_ring_std_event(clusters, muon_props)
            results.append(std_photons_on_ring)
            number_muons += 1
    outdir = os.path.dirname(outpath)
    os.makedirs(outdir, exist_ok=True)
    with open(outpath + ".temp", "wt") as fout:
        out = {
            "average_fuzz": float(np.average(results)),
            "std_fuzz": float(np.std(results)),
            "number_muons": number_muons,
        }
        fout.write(json.dumps(out))
    os.rename(outpath + ".temp", outpath)

"""
def muon_ring_std_nights(muon_dir, save_dir_data):
    for dir, subdirList, fileList in os.walk(muon_dir):
        if dir[len(muon_dir)+1:].count(os.sep) == 2:
            date = str(dir)[-10:-6] + str(dir)[-5:-3] + str(dir)[-2:]
            year = date [0:4]
            month = date [4:6]
            night = date[6:8]
            aveg_name = (save_dir_data + "std_of_runs_" 
            + date + ".csv")
            temp_name = (save_dir_data + "temp_" 
            + "std_of_runs_" + date + ".csv")
            res_path = Path(aveg_name)
            saving = []
            print(date)
            if not res_path.is_file():
                for f in fileList:
                    run_number = str(f)[9:12]
                    if "phs" in str(f):
                        path = (muon_dir + "/" + year + "/" 
                        + month + "/" + night + "/" + f)
                        statinfo = os.stat(path)
                        if statinfo.st_size > 67:
                            run_std = muon_ring_std_run(path)
                            saving.append((run_std, date, run_number))
                        else:
                            continue
                if len(saving) != 0:
                    with open(temp_name, "w") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerows(saving)
            else:
                print("Already calculated")
            try:
                os.rename(temp_name, aveg_name)
            except:
                print("Skipped")
            print("Finished night ")
"""
