# Land Use Analysis

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

s1_path_2030 = 'NYS-Land-Use/output/202512092100-PG-2030-B/s1/results/capacity.csv'
s2_path = 'NYS-Land-Use/output/202512092100-PG-2030-B/s2/results/capacity.csv'
s3_path = 'NYS-Land-Use/output/202512092100-PG-2030-B/s3/results/capacity.csv'
s1_path_2040 = 'NYS-Land-Use/output/202512161939-PG-2040-B/s1/results/capacity.csv'
s4_path = 'NYS-Land-Use/output/202512161939-PG-2040-B/s4/results/capacity.csv'
s5_path = 'NYS-Land-Use/output/202512161939-PG-2040-B/s5/results/capacity.csv'
s6_path = 'NYS-Land-Use/output/202512161939-PG-2040-B/s6/results/capacity.csv'
s7_path = 'NYS-Land-Use/output/202512161939-PG-2040-B/s7/results/capacity.csv'

def get_solar_dataframe(pathname):
    df = pd.read_csv(pathname)


    resources = ["hydro", "gas", "wind", "utilitypv", "nuclear", "trans", "biomass", "distributed", "photovoltaic"]

    pattern = "|".join(resources)

    df["ResourceType"] = (
        df["Resource"]
        .str.lower()
        .str.extract("(" + pattern + ")", expand=False)
    )

    solar_df = df[df["ResourceType"].isin(["utilitypv"])]

    return solar_df

# Agricultural land accounts for 84% of (med/good) suitable land for solar development in NYS

# Farmland Assignments
z_A = 144472
z_B = 41378
z_C = 69229
z_D = 5998
z_E = 62753
z_F = 61401
z_G = 55729
z_H = 0
z_I = 3804
z_J = 61
z_K = 20732

farmland = [z_A, z_B, (z_C+z_E), z_D, z_F, (z_G+z_H+z_I), z_J, z_K]

total_farm = z_A + z_B + z_C + z_D + z_E + z_F + z_G + z_H + z_I + z_J + z_K
print("Total Farmland Area (acres): ", total_farm)
# 465556

solar_density = 6.49 # acres per MW
agvol_density = 11.75 # acres per MW

# 640 acres in a square mile

# These are acording to the study by Vanktesh et al. 2021
# base case: 
bc_unsuitable = 26538 * 640
bc_poor = 13045	* 640
bc_medium = 6816 * 640
bc_good = 2515 * 640


# no prime farmland: 
np_unsuitable = 37413 * 640
np_poor = 2218 * 640
np_medium = 4045 * 640
np_good = 2486 * 640

# Evenly distributed across NY zones:

# Not using zones

# Percent agvol vs solar
agvol_dev_scenario_1 = 0.25
agvol_dev_scenario_2 = 0.50
agvol_dev_scenario_3 = 0.75
agvol_dev_scenario_4 = 1.00


def land_use_analysis(capacity_dataframe, agvol_share, zones, zone_labels, scenario_name):
    capacity_to_develop = capacity_dataframe["NewCap"].sum()
    
    total_land_needed = capacity_to_develop * solar_density * (1 - agvol_share)
    agvol_land_needed = capacity_to_develop * agvol_density * agvol_share

    print("Total Land Needed (acres): ", total_land_needed)
    print("Agvol Land Needed (acres): ", agvol_land_needed)
    print()

    percents_by_zone = []
    capacity_by_zone = []   # <-- NEW

    for i in range(len(zones)):
        zone = zones[i]

        mw_needed = capacity_dataframe.loc[
            capacity_dataframe["Zone"] == zone, "NewCap"
        ].sum()

        capacity_by_zone.append(mw_needed)   # <-- NEW

        land_needed = (
            mw_needed * (1 - agvol_share) * solar_density +
            mw_needed * agvol_share * agvol_density
        )

        percent_farm_used = land_needed / farmland[i]
        percents_by_zone.append(percent_farm_used)

    # --------- Plot 1: Percent Farmland Used ---------
    plt.figure(figsize=(10, 5))
    plt.bar(zones, percents_by_zone, color='green')
    plt.xticks(ticks=zones, labels=zone_labels, rotation=45, ha="right")
    plt.xlabel("Zone")
    plt.ylabel("Percent of Farmland Developed")
    plt.title(f"Land Used in Scenario {scenario_name}")
    plt.tight_layout()

    plt.savefig(
        f"NYS-Land-Use/Land Analysis/Figures/land_use_{scenario_name}.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

    # --------- Plot 2: Solar Capacity Needed ---------
    plt.figure(figsize=(10, 5))
    plt.bar(zones, capacity_by_zone, color='green')
    plt.xticks(ticks=zones, labels=zone_labels, rotation=45, ha="right")
    plt.xlabel("Zone")
    plt.ylabel("Solar Capacity Needed (MW)")
    plt.title(f"Solar Capacity by Zone – Scenario {scenario_name}")
    plt.ylim(0, 24000)
    plt.tight_layout()

    plt.savefig(
        f"NYS-Land-Use/Land Analysis/Figures/solar_capacity_{scenario_name}.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

def capacity_grouped_by_zone(capacity_dataframe, zones):
    capacity_by_zone = []

    for i in range(len(zones)):
        zone = zones[i]

        mw_needed = capacity_dataframe.loc[
            capacity_dataframe["Zone"] == zone, "NewCap"
        ].sum()

        capacity_by_zone.append(mw_needed)

    return capacity_by_zone


# How much land for each scenario
def land_per_scenario(capacity_dataframe, solar_density):
    land_needed = (capacity_dataframe["NewCap"].sum()) * solar_density
    return land_needed
    



# What percent of good land is farmland
zones = [2,3,4,5,6,7,8,9]
agvol_share = 0.25
zone_labels = ['Zone A', 'Zone B', 'Zone C&E', 'Zone D', 'Zone F', 'Zone G-I', 'Zone J', 'Zone K']


pathnames = [s1_path_2030, s2_path, s3_path, s1_path_2040, s4_path, s5_path, s6_path, s7_path]
scenario_names = ['s1 2030', 's2', 's3', 's1 2040', 's4', 's5', 's6', 's7']
land = []
cap_by_zone = pd.DataFrame()

for i in range(len(pathnames)):
    solar_df = get_solar_dataframe(pathnames[i])
    land_use_analysis(solar_df, agvol_share, zones, zone_labels, scenario_names[i])
    land_add = land_per_scenario(solar_df, solar_density)
    land.append(land_add)
    cap_by_zone[f"{scenario_names[i]}"] = capacity_grouped_by_zone(solar_df, zones)

print(land)

#print(f"Land required for {scenario_name} is {land_needed} acres")

plt.figure(figsize=(12,6))
plt.bar(zones, land, label="Acres")
plt.xticks(ticks=zones, labels=scenario_names, rotation=45, ha="right")
plt.ylabel("Land Required (Acres)")
plt.xlabel("Scenario")
plt.title("Land Needed by Scenario")
plt.xticks(rotation=45, ha="right")
plt.legend(title="Generation Type")
plt.tight_layout()

save_path = "NYS-Land-Use/Land Analysis/Capacity Figures/Total_land_by_scenario.png"
plt.savefig(save_path, dpi=300, bbox_inches="tight")


###### Plot capacity by zone for each scenario ######

bar_width = 0.10
x = np.arange(len(zones))

plt.figure(figsize=(14, 6))

for i, scenario in enumerate(cap_by_zone.columns):
    plt.bar(
        x + i * bar_width,
        cap_by_zone[scenario],
        width=bar_width,
        label=scenario
    )

# Center x-ticks
plt.xticks(
    x + bar_width * (len(cap_by_zone.columns) - 1) / 2,
    zone_labels,
    rotation=45,
    ha="right"
)

plt.xlabel("Zone")
plt.ylabel("Solar Capacity Needed (MW)")
plt.title("Solar Capacity by Zone and Scenario")
plt.ylim(0, 24000)
plt.legend(title="Scenario", ncol=2)
plt.tight_layout()

save_path = "NYS-Land-Use/Land Analysis/Capacity Figures/solar_capacity_grouped_by_zone.png"
plt.savefig(save_path, dpi=300, bbox_inches="tight")


# ------- Table 1: Land Use Summary by Scenario -------
agland_share = 0.5 # land that is agricultural
agvol_share = 0.5 # percent of agricultural land that is used as agvol land


# print(table_1)
land_needed = []
ag_land_needed = []
agvol_land_needed = []
number_of_farms = []

for i in range(len(pathnames)):
    solar_df = get_solar_dataframe(pathnames[i])

    # capacity already handled
    cap_by_zone[f"{scenario_names[i]}"] = capacity_grouped_by_zone(solar_df, zones)

    total_capacity = solar_df["NewCap"].sum()

    land_needed.append(
        total_capacity * solar_density * (1 - agland_share)
    )

    ag_land_needed.append(
        total_capacity * solar_density * (1 - agland_share) * (1 - agvol_share)
    )

    agvol_land_needed.append(
        total_capacity * agvol_density * agland_share * agvol_share
    )

    number_of_farms.append(
        (total_capacity * agvol_density * agvol_share) / 78
    )


number_of_farms = [5849, 2879, 7161+6632, 560, 4846, 2006+108, 52, 607]
med_farm_size_per_zone = [64.375, 68.75, 84.5+102.8181818, 69.5, 73.90909091, 46.33333333+16, 0.6, 18.5]


farm_specs = pd.DataFrame({
    "Zones": zone_labels,
    "Number of Farms": number_of_farms,
    "Median Farm Size (acres)": med_farm_size_per_zone

})


def number_of_farms(capacity_by_zone, farm_size):
    # capacity by zone is a list of capacities for each zone for a given scenario run
    num_farms = 0

    for i in range(len(capacity_by_zone)):
        num_farms += (capacity_by_zone[i] * agvol_density * agvol_share * agland_share) / farm_size["Median Farm Size (acres)"][i]

    return num_farms

farms = []
for i in range(len(pathnames)):
    farms.append(
        number_of_farms(
            cap_by_zone[scenario_names[i]],
            farm_size=farm_specs
        )
    )

percent_of_farms = [
    (farms[i] / 30650) * 100 for i in range(len(farms))
]

table_1 = pd.DataFrame({
    "Scenario": scenario_names,
    "Capacity Needed (MW)": [cap_by_zone[col].sum() for col in cap_by_zone.columns],
    "Non-Agricultural Land Needed (acres)": land_needed,
    "Agricultural Land Needed (acres)": ag_land_needed,
    "Agvol Land Needed (acres)": agvol_land_needed,
    "Number of Farms Converted to AgVol": farms,
    "Percent of Farms Converted to AgVol (%)": percent_of_farms
})

table_1 = table_1.round(0).astype({
    "Capacity Needed (MW)": int,
    "Non-Agricultural Land Needed (acres)": int,
    "Agricultural Land Needed (acres)": int,
    "Agvol Land Needed (acres)": int,
    "Number of Farms Converted to AgVol": int,
    "Percent of Farms Converted to AgVol (%)": float
})
print(table_1)

table_1.to_csv("NYS-Land-Use/Land Analysis/land_use_summary_by_scenario.csv", index=False)