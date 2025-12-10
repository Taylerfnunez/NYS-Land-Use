import re
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

tech_types = ["hydro", "gas", "wind", "solar", "nuclear"]
zones = [2,3,4,5,6,7]

s1_path_2030 = 'output/202512092100-PG-2030-B/s1/results/capacity.csv'
s2_path = 'output/202512092100-PG-2030-B/s2/results/capacity.csv'
s3_path = 'output/202512092100-PG-2030-B/s3/results/capacity.csv'
s1_path_2040 = 'output/202512092232-PG-2040-B/s1/results/capacity.csv'
s4_path = 'output/202512092232-PG-2040-B/s4/results/capacity.csv'
s5_path = 'output/202512092232-PG-2040-B/s5/results/capacity.csv'
s6_path = 'output/202512092232-PG-2040-B/s6/results/capacity.csv'
s7_path = 'output/202512092232-PG-2040-B/s7/results/capacity.csv'

pathnames = [s1_path_2030, s2_path, s3_path, s1_path_2040, s4_path, s5_path, s6_path, s7_path]
scenario_names = ['s1 2030', 's2', 's3', 's1 2040', 's4', 's5', 's6', 's7']

# plot aggregation levels: 1 - by tech, 2 - by tech with specific zones only, 3 - all techs and specific zones
plot_aggregation = 1

def get_data_from_csv(pathname):
    capacity = pd.read_csv(pathname)
    df = capacity.copy()
    resources = ["hydro", "gas", "wind", "utilitypv", "nuclear", "trans", "biomass", "distributed", "photovoltaic"]

    pattern = "|".join(resources)

    df["ResourceType"] = (
        df["Resource"]
        .str.lower()
        .str.extract("(" + pattern + ")", expand=False)
    )

    data = {
        "wind": df[df["ResourceType"] == "wind"],
        "gas": df[df["ResourceType"] == "gas"],
        "hydro": df[df["ResourceType"] == "hydro"],
        "solar": df[df["ResourceType"].isin(["utilitypv", "photovoltaic"])],
        "nuclear": df[df["ResourceType"] == "nuclear"],
        "trans": df[df["ResourceType"] == "trans"],
        "biomass": df[df["ResourceType"] == "biomass"],
        "distributed": df[df["ResourceType"] == "distributed"],
        "other": df[~df["ResourceType"].isin(resources)],
        "all": df,
    }

    return data


def plot_resource_capacity(resource_df, resource_name, tech_types, zones, plot_aggregation, scenario_name):

    if plot_aggregation == 1:
        to_plot = resource_df[((resource_df["StartCap"] > 0) | (resource_df["EndCap"] > 0)) & (resource_df["EndCap"] >= resource_df["StartCap"])].copy()
    
    elif plot_aggregation == 2:
        to_plot = resource_df[((resource_df["StartCap"] > 0) | (resource_df["EndCap"] > 0)) & (resource_df["EndCap"] >= resource_df["StartCap"]) & (resource_df["Zone"].isin(zones))].copy()

    elif plot_aggregation == 3:
        to_plot = resource_df[((resource_df["StartCap"] > 0) | (resource_df["EndCap"] > 0)) & (resource_df["EndCap"] >= resource_df["StartCap"]) & (resource_df["ResourceType"].isin(tech_types)) & (resource_df["Zone"].isin(zones))].copy()


    # Numeric x positions
    x_positions = list(range(len(to_plot)))

    # Data for bars
    startcap = to_plot["StartCap"].values
    capbuilt = to_plot["NewCap"].values
    x_labels = to_plot["Resource"].values

    # Plot
    plt.figure(figsize=(10,5))
    plt.bar(x_positions, startcap, label="StartCap")
    plt.bar(x_positions, capbuilt, bottom=startcap, label="Capacity Built")

    # Align x-axis labels with bars
    plt.xticks(ticks=x_positions, labels=x_labels, rotation=45, ha="right")

    plt.xlabel("Resource")
    plt.ylabel("Capacity (MW)")
    plt.title(f"Capacity for {resource_name} {scenario_name}")
    plt.legend()
    plt.tight_layout()

    save_path = f"Land Analysis/Capacity Figures/capacity_{scenario_name}.png"   # <-- update this
    plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()



def plot_retired_capacity(resource_df, resource_name, plot_aggregation, tech_types, zones):
    # Filter rows where RetCap > 0
    if plot_aggregation == 1:
        to_plot = resource_df[(resource_df["RetCap"] > 0)].copy()
 
    elif plot_aggregation == 2:
        to_plot = resource_df[((resource_df["RetCap"] > 0)) & (resource_df["ResourceType"].isin(tech_types))].copy()

    elif plot_aggregation == 3:
        to_plot = resource_df[((resource_df["StartCap"] > 0) | (resource_df["EndCap"] > 0)) & (resource_df["EndCap"] >= resource_df["StartCap"]) & (resource_df["TechType"].isin(tech_types)) & (resource_df["Zone"].isin(zones))].copy()


    # Numeric x positions
    x_positions = list(range(len(to_plot)))

    # Data for bars
    startcap = to_plot["StartCap"].values
    retired = -to_plot["RetCap"].values  # make negative for plotting below x-axis
    x_labels = to_plot["Resource"].values

    # Plot
    plt.figure(figsize=(12,5))

    # StartCap above x-axis
    plt.bar(x_positions, startcap, label="StartCap")

    # Retired capacity below x-axis
    plt.bar(x_positions, retired, bottom=0, label="Retired")

    # Align x-axis labels with bars
    plt.xticks(ticks=x_positions, labels=x_labels, rotation=45, ha="right")

    plt.xlabel("Resource")
    plt.ylabel("Capacity (MW)")
    plt.title(f"Capacity for {resource_name}")
    plt.legend()
    plt.tight_layout()
    plt.show()

# for resource_type in resources:
#     if resource_type == "wind":
#         plot_retired_capacity(wind_df, "Wind", plot_aggregation, tech_types, zones)
#     elif resource_type == "gas":
#         plot_retired_capacity(gas_df, "Gas", plot_aggregation, tech_types, zones)
#     elif resource_type == "hydro":
#         plot_retired_capacity(hydro_df, "Hydro", plot_aggregation, tech_types, zones)
#     elif resource_type in ["utilitypv", "photovoltaic"]:
#         plot_retired_capacity(solar_df, "Solar", plot_aggregation, tech_types, zones)
#     elif resource_type == "nuclear":
#         plot_retired_capacity(nuclear_df, "Nuclear", plot_aggregation, tech_types, zones)
#     elif resource_type == "trans":
#         plot_retired_capacity(trans_df, "Transmission", plot_aggregation, tech_types, zones)
#     elif resource_type == "biomass":
#         plot_retired_capacity(biomass_df, "Biomass", plot_aggregation, tech_types, zones)
#     elif resource_type == "distributed":
#         plot_retired_capacity(distributed_df, "Distributed", plot_aggregation, tech_types, zones)  
        

for i in range(len(pathnames)):
    data = get_data_from_csv(pathnames[i])
    solar_data = data["solar"]    

    resource_name = 'solar'
    tech_types = ["solar"]
    zones = [2,3,4,5,6,7,8,9]
    plot_aggregation = 2
    scenario = scenario_names[i]

    plot_resource_capacity(solar_data, resource_name, tech_types, zones, plot_aggregation, scenario)