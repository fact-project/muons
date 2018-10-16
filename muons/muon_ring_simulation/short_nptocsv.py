def write_to_csv(simTruthPath, simulationTruths):
    with open(simTruthPath, "wt") as fout:
        h = "casual_muon_support0,"
        h += "casual_muon_support1,"
        h += "casual_muon_support2,"
        h += "casual_muon_direction0,"
        h += "casual_muon_direction1,"
        h += "casual_muon_direction2,"
        h += "event_id,"
        h += "nsb_rate_per_pixel,"
        h += "ch_rate,"
        h += "opening_angle,"
        h += "fact_aperture_radius,"
        h += "arrival_time_std,"
        h += "random_seed\n"
        fout.write(h)
        for sT in simulationTruths:
            s = "{:f},{:f},{:f},".format(
                sT["casual_muon_support"][0],
                sT["casual_muon_support"][1],
                sT["casual_muon_support"][2])
            s += "{:f},{:f},{:f},".format(
                sT["casual_muon_direction"][0],
                sT["casual_muon_direction"][1],
                sT["casual_muon_direction"][2])
            s +="{:d},".format(sT["event_id"])
            s +="{:f},".format(sT["nsb_rate_per_pixel"])
            s +="{:f},".format(sT["opening_angle"])
            s +="{:f},".format(sT["fact_aperture_radius"])
            s +="{:f},".format(sT["arrival_time_std"])
            s +="{:d}\n".format(sT["random_seed"])
            fout.write(s)
