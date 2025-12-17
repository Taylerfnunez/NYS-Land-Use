import re
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

tech_types = ["hydro", "gas", "wind", "solar", "nuclear"]
zones = [2,3,4,5,6,7,8,9]

s1_path_2030 = 'NYS-Land-Use/output/202512092100-PG-2030-B/s1/results/capacity.csv'
s2_path = 'NYS-Land-Use/output/202512092100-PG-2030-B/s2/results/capacity.csv'
s3_path = 'NYS-Land-Use/output/202512092100-PG-2030-B/s3/results/capacity.csv'
# s1_path_2040 = 'output/202512092232-PG-2040-B/s1/results/capacity.csv'
# s4_path = 'output/202512092232-PG-2040-B/s4/results/capacity.csv'
# s5_path = 'output/202512092232-PG-2040-B/s5/results/capacity.csv'
# s6_path = 'output/202512092232-PG-2040-B/s6/results/capacity.csv'
# s7_path = 'output/202512092232-PG-2040-B/s7/results/capacity.csv'
s1_path_2040 = 'NYS-Land-Use/output/202512161939-PG-2040-B/s1/results/capacity.csv'
s4_path = 'NYS-Land-Use/output/202512161939-PG-2040-B/s4/results/capacity.csv'
s5_path = 'NYS-Land-Use/output/202512161939-PG-2040-B/s5/results/capacity.csv'
s6_path = 'NYS-Land-Use/output/202512161939-PG-2040-B/s6/results/capacity.csv'
s7_path = 'NYS-Land-Use/output/202512161939-PG-2040-B/s7/results/capacity.csv'

pathnames = [s1_path_2030, s2_path, s3_path, s1_path_2040, s4_path, s5_path, s6_path, s7_path]
scenario_names = ['s1 2030', 's2', 's3', 's1 2040', 's4', 's5', 's6', 's7']

# plot aggregation levels: 1 - by tech, 2 - by tech with specific zones only, 3 - all techs and specific zones
plot_aggregation = 1

def get_data_from_csv(pathname):
    capacity = pd.read_csv(pathname)
    df = capacity.copy()
    resources = ["hydro", "gcf", "ccs", "wind", "utilitypv", "nuclear", "trans", "biomass", "distributed", "photovoltaic"]

    pattern = "|".join(resources)

    df["ResourceType"] = (
        df["Resource"]
        .str.lower()
        .str.extract("(" + pattern + ")", expand=False)
    )

    data = {
        "wind": df[df["ResourceType"] == "wind"],
        "gas": df[df["ResourceType"] == "gcf"],
        "ccs": df[df["ResourceType"] == "ccs"],
        "hydro": df[df["ResourceType"] == "hydro"],
        "solar": df[df["ResourceType"] == "utilitypv"],
        "roof-top": df[df["ResourceType"] == "photovoltaic"],
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
    #startcap = to_plot["StartCap"].values
    capbuilt = to_plot["NewCap"].values
    x_labels = to_plot["Resource"].values

    # Plot
    plt.figure(figsize=(10,5))
    #plt.bar(x_positions, startcap, label="StartCap").       bottom=startcap,
    plt.bar(x_positions, capbuilt, label="Capacity Built")

    # Align x-axis labels with bars
    plt.xticks(ticks=x_positions, labels=x_labels, rotation=45, ha="right")

    plt.xlabel("Resource")
    plt.ylabel("Capacity (MW)")
    plt.title(f"Capacity for {resource_name} {scenario_name}")
    plt.legend()
    plt.tight_layout()

    save_path = f"NYS-Land-Use/Land Analysis/Capacity Figures/capacity_{scenario_name}.png"   # <-- update this
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    
    #plt.show()


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
        

for i in range(len(pathnames)):
    data = get_data_from_csv(pathnames[i])
    solar_data = data["solar"]    

    resource_name = 'solar'
    tech_types = ["solar"]
    zones = [2,3,4,5,6,7,8,9]
    plot_aggregation = 2
    scenario = scenario_names[i]

    plot_resource_capacity(solar_data, resource_name, tech_types, zones, plot_aggregation, scenario)


def plot_stacked_newcap(all_scenario_data, scenario_names, zones_to_include):

    tech_order = ["ccs", "solar", "wind", "gas", "hydro", "nuclear", "roof-top"]
    tech_colors = {
    "ccs": "#5e8b23",        # gray
    "solar": "#1f77b4",      # yellow
    "wind": "#FDB813",       # blue
    "gas": "#d62728",        # red
    "hydro": "#2c9795",      # teal
    "nuclear": "#9467bd",    # purple
    "roof-top": "#6c5336"    # green
}
    df_list = []

    for scenario_name, data in zip(scenario_names, all_scenario_data):
        for tech in tech_order:
            tech_df = data[tech]

            # ---- NEW: filter by zones ----
            if zones_to_include is not None:
                tech_df = tech_df[tech_df["Zone"].isin(zones_to_include)]

            # sum capacity for selected zones
            newcap_val = tech_df["NewCap"].sum()

            df_list.append({
                "Scenario": scenario_name,
                "Tech": tech,
                "NewCap": newcap_val
            })

    df = pd.DataFrame(df_list)

    # Pivot to wide format for plotting
    pivot = df.pivot(index="Scenario", columns="Tech", values="NewCap").fillna(0)

    # Plot
    plt.figure(figsize=(12,6))
    pivot.plot(kind="bar", stacked=True, figsize=(12,6), color=[tech_colors[t] for t in pivot.columns])

    plt.ylabel("Added Capacity (MW)")
    plt.xlabel("Scenario")
    plt.title("New Installed Capacity by Scenario")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Generation Type")
    plt.tight_layout()

    save_path = "NYS-Land-Use/Land Analysis/Capacity Figures/NewCap_Bars.png"
    plt.savefig(save_path, dpi=300, bbox_inches="tight")

    # plt.show()


# Collect data for all scenarios
all_scenario_data = []

for path in pathnames:
    all_scenario_data.append(get_data_from_csv(path))

zones = [2,3,4,5,6,7,8,9]

# Create the stacked bar plot
plot_stacked_newcap(all_scenario_data, scenario_names, zones)
