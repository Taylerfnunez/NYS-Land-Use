import re
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

tech_types = ["hydro", "gas", "wind", "solar", "nuclear"]
zones = [2,3,4,5,6,7]
# plot aggregation levels: 1 - by tech, 2 - by tech with specific zones only, 3 - all techs and specific zones
plot_aggregation = 1

capacity = pd.read_csv("capacity.csv")
df = capacity.copy()

# want to plot by zone and by resource for the zones called
# zones_specific = plot_settings["zones_specific"]
# fig_size = plot_settings["fig_size"]
# dpi = plot_settings["dpi"]
# resource_types = plot_settings["Recource Types"]

resources = ["hydro", "gas", "wind", "utilitypv", "nuclear", "trans", "biomass", "distributed", "photovoltaic"]


pattern = "|".join(resources)

df["ResourceType"] = (
    df["Resource"]
    .str.lower()
    .str.extract("(" + pattern + ")", expand=False)
)


# Wind
wind_df = df[df["ResourceType"] == "wind"]
# Gas
gas_df = df[df["ResourceType"] == "gas"]
# Hydro
hydro_df = df[df["ResourceType"] == "hydro"]
# Solar
solar_df = df[df["ResourceType"].isin(["utilitypv", "photovoltaic"])]
# Nuclear
nuclear_df = df[df["ResourceType"] == "nuclear"]
# Transmission
trans_df = df[df["ResourceType"] == "trans"]
# Biomass
biomass_df = df[df["ResourceType"] == "biomass"]
# Distributed
distributed_df = df[df["ResourceType"] == "distributed"]
# All other resources
other_df = df[~df["ResourceType"].isin(resources)]

# print(wind_df)


def plot_resource_capacity(resource_df, resource_name, tech_types, zones):

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
    plt.figure(figsize=(12,5))
    plt.bar(x_positions, startcap, label="StartCap")
    plt.bar(x_positions, capbuilt, bottom=startcap, label="Capacity Built")

    # Align x-axis labels with bars
    plt.xticks(ticks=x_positions, labels=x_labels, rotation=45, ha="right")

    plt.xlabel("Resource")
    plt.ylabel("Capacity (MW)")
    plt.title(f"Capacity for {resource_name}")
    plt.legend()
    plt.tight_layout()
    plt.show()


# for resource_type in resource_types:
#     if resource_type == "Wind":
#         plot_resource_capacity(wind_df, "Wind", "EndCap")
#         filename= os.path.join(save_path, f'{sim_id}_Capacity_Wind')
#         plt.savefig(filename, dpi = dpi)
#         plt.close()
#         print(f"Saved: {filename}")
#     elif resource_type == "Gas":
#         plot_resource_capacity(gas_df, "Gas", "EndCap")
#         filename= os.path.join(save_path, f'{sim_id}_Capacity_Gas')
#         plt.savefig(filename, dpi = dpi)
#         plt.close()
#         print(f"Saved: {filename}")
#     elif resource_type == "Hydro":
#         plot_resource_capacity(hydro_df, "Hydro", "EndCap")
#         filename= os.path.join(save_path, f'{sim_id}_Capacity_Hydro')
#         plt.savefig(filename, dpi = dpi)
#         plt.close()
#         print(f"Saved: {filename}")
#     elif resource_type == "Solar":
#         plot_resource_capacity(solar_df, "Solar", "EndCap")
#         filename= os.path.join(save_path, f'{sim_id}_Capacity_Solar')
#         plt.savefig(filename, dpi = dpi)
#         plt.close()
#         print(f"Saved: {filename}")
#     elif resource_type == "Nuclear":
#         plot_resource_capacity(nuclear_df, "Nuclear", "EndCap")
#         filename= os.path.join(save_path, f'{sim_id}_Capacity_Nuclear')
#         plt.savefig(filename, dpi = dpi)
#         plt.close()
#         print(f"Saved: {filename}")
#     elif resource_type == "Transmission":
#         plot_resource_capacity(trans_df, "Transmission", "EndCap")
#         filename= os.path.join(save_path, f'{sim_id}_Capacity_Transmission')
#         plt.savefig(filename, dpi = dpi)
#         plt.close()
#         print(f"Saved: {filename}")
#     elif resource_type == "Biomass":
#         plot_resource_capacity(biomass_df, "Biomass", "EndCap")
#         filename= os.path.join(save_path, f'{sim_id}_Capacity_Biomass')
#         plt.savefig(filename, dpi = dpi)
#         plt.close()
#         print(f"Saved: {filename}")
#     elif resource_type == "Distributed":
#         plot_resource_capacity(distributed_df, "Distributed", "EndCap")
#         filename= os.path.join(save_path, f'{sim_id}_Capacity_Distributed')
#         plt.savefig(filename, dpi = dpi)
#         plt.close()
#         print(f"Saved: {filename}")

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

for resource_type in resources:
    if resource_type == "wind":
        plot_retired_capacity(wind_df, "Wind", plot_aggregation, tech_types, zones)
    elif resource_type == "gas":
        plot_retired_capacity(gas_df, "Gas", plot_aggregation, tech_types, zones)
    elif resource_type == "hydro":
        plot_retired_capacity(hydro_df, "Hydro", plot_aggregation, tech_types, zones)
    elif resource_type in ["utilitypv", "photovoltaic"]:
        plot_retired_capacity(solar_df, "Solar", plot_aggregation, tech_types, zones)
    elif resource_type == "nuclear":
        plot_retired_capacity(nuclear_df, "Nuclear", plot_aggregation, tech_types, zones)
    elif resource_type == "trans":
        plot_retired_capacity(trans_df, "Transmission", plot_aggregation, tech_types, zones)
    elif resource_type == "biomass":
        plot_retired_capacity(biomass_df, "Biomass", plot_aggregation, tech_types, zones)
    elif resource_type == "distributed":
        plot_retired_capacity(distributed_df, "Distributed", plot_aggregation, tech_types, zones)  
        