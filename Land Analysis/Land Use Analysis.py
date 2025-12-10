# Land Use Analysis

import pandas as pd
import matplotlib.pyplot as plt

s1_path_2030 = 'output/202512092100-PG-2030-B/s1/results/capacity.csv'
s2_path = 'output/202512092100-PG-2030-B/s2/results/capacity.csv'
s3_path = 'output/202512092100-PG-2030-B/s3/results/capacity.csv'
s1_path_2040 = 'output/202512092232-PG-2040-B/s1/results/capacity.csv'
s4_path = 'output/202512092232-PG-2040-B/s4/results/capacity.csv'
s5_path = 'output/202512092232-PG-2040-B/s5/results/capacity.csv'
s6_path = 'output/202512092232-PG-2040-B/s6/results/capacity.csv'
s7_path = 'output/202512092232-PG-2040-B/s7/results/capacity.csv'



def get_solar_dataframe(pathname):
    df = pd.read_csv(pathname)


    resources = ["hydro", "gas", "wind", "utilitypv", "nuclear", "trans", "biomass", "distributed", "photovoltaic"]

    pattern = "|".join(resources)

    df["ResourceType"] = (
        df["Resource"]
        .str.lower()
        .str.extract("(" + pattern + ")", expand=False)
    )

    solar_df = df[df["ResourceType"].isin(["utilitypv", "photovoltaic"])]

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

    for i in range(len(zones)):
        zone = zones[i]

        # capacity needed for this zone
        mw_needed = capacity_dataframe.loc[
            capacity_dataframe["Zone"] == zone, "NewCap"
        ].sum()

        print(f"MW Needed in Zone {zone}: {mw_needed}")

        # land needed for this zone
        land_needed = (
            mw_needed * (1 - agvol_share) * solar_density +
            mw_needed * agvol_share * agvol_density
        )

        print(f"Land Needed in Zone {zone}: {land_needed}")

        percent_farm_used = land_needed / farmland[i]
        print(f"Percent of Farmland Used in Zone {zone}: {percent_farm_used}")
        print("------------------------------------------")
        percents_by_zone.append(percent_farm_used)

    
    plt.figure(figsize=(10,5))

    plt.bar(zones, percents_by_zone, label="Percent Farmland by Zone")
    plt.xticks(ticks=zones, labels=zone_labels, rotation=45, ha="right")
    plt.xlabel("Zone")
    plt.ylabel("Percent of Farmland Developed")
    plt.title(f"Land Used in Scenario {scenario_name}")
    plt.legend()
    plt.tight_layout()

    save_path = f"Land Analysis/Figures/land_use_{scenario_name}.png"   # <-- update this
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    #print(f"Figure saved to: {save_path}")

    plt.show()





# What percent of good land is farmland
zones = [2,3,4,5,6,7,8,9]
agvol_share = 0.25
zone_labels = ['Zone A', 'Zone B', 'Zone C&E', 'Zone D', 'Zone F', 'Zone G-I', 'Zone J', 'Zone K']


pathnames = [s1_path_2030, s2_path, s3_path, s1_path_2040, s4_path, s5_path, s6_path, s7_path]
scenario_names = ['s1 2030', 's2', 's3', 's1 2040', 's4', 's5', 's6', 's7']

for i in range(len(pathnames)):
    solar_df = get_solar_dataframe(pathnames[i])
    land_use_analysis(solar_df, agvol_share, zones, zone_labels, scenario_names[i])

