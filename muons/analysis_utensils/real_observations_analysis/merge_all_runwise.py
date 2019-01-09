import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
import json
import fact
import time
from fact import credentials
from datetime import datetime


# merge all average stdev of a run into one file
def merge_files(data_in, outPutFilePath):
    data = []
    wCardPath = os.path.join(data_in, "*", "*", "*", "*")
    for path in sorted(glob.glob(wCardPath)):
        fPath = fact.path.parse(path)
        night = fPath["night"]
        run = fPath["run"]
        with open(path, "rt") as reader:
            line_dictionary = json.loads(reader.read())
            csv_line = (
                "{night:d}\t{run:03d}\t".format(
                    night=night,
                    run=run) +
                "{average_fuzz:f}\t{std_fuzz}\t".format(
                    average_fuzz=line_dictionary["average_fuzz"],
                    std_fuzz=line_dictionary["std_fuzz"]) +
                "{number_muons:d}".format(
                    number_muons=line_dictionary["number_muons"])
            )
            data.append(csv_line)
    with open(outPutFilePath, "wt") as dOut:
        dOut.write("fNight\tfRunID\taverage_fuzz\tstd_fuzz\tnumber_muons\n")
        for csv_line in data:
            dOut.write(csv_line + "\n")


# download latest run info for FACT
def get_df_values(df_filePath):
    factdb = credentials.create_factdb_engine()
    runInfoDB = pd.read_sql_table(
                table_name = "RunInfo",
                con = factdb,
                columns = ["fNight", "fRunID", "fRunStart", "fCurrentsMedMean"]
                )
    runInfoDB.to_msgpack(df_filePath)


# merge info from FACT and info from muon_fuzz
def merge_dfs(df_filePath, muon_fuzzPath, new_db):
    muon_fuzz = pd.read_csv(muon_fuzzPath, delimiter="\t")
    runinfo = pd.read_msgpack(df_filePath)
    merged = pd.merge(muon_fuzz, runinfo, on = ["fNight", "fRunID"])
    merged.to_csv(new_db, index = False)


# add unix timestamp to the dataframe
def add_unix(db_file):
    df = pd.read_csv(db_file)
    index = pd.DatetimeIndex(df["fRunStart"])
    df["fRunStart"] = index.astype(np.int64) // 10**9
    df.to_csv(db_file, index=False, na_rep="nan")


# combine functions
def create_dataframe(df_filePath, muon_fuzzPath, new_db):
    get_df_values(df_filePath)
    merge_dfs(df_filePath, muon_fuzzPath, new_db)
    add_unix(new_db)


# plot the std_fuzz and average_fuzz vs time
def plot(new_db, plt_dir):
    df = pd.read_csv(new_db)
    df = df.dropna()
    mask = df["fRunStart"] > 1.2e9
    df1 = df[mask]
    plt.plot(df1["fRunStart"].values, df1["average_fuzz"].values)
    plt.plot(df1["fRunStart"].values, df1["std_fuzz"].values)
    plt.savefig(plt_dir)

# add mask for weird timestamps
