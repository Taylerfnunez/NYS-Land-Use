# Land Use Analysis

import pandas as pd

df = pd.read_csv('capacity.csv')


resources = ["hydro", "gas", "wind", "utilitypv", "nuclear", "trans", "biomass", "distributed", "photovoltaic"]

pattern = "|".join(resources)

df["ResourceType"] = (
    df["Resource"]
    .str.lower()
    .str.extract("(" + pattern + ")", expand=False)
)

solar_df = df[df["ResourceType"].isin(["utilitypv", "photovoltaic"])]

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

total_farm = z_A + z_B + z_C + z_D + z_E + z_F + z_G + z_H + z_I + z_J + z_K
print("Total Farmland Area (acres): ", total_farm)
# 465556

solar_density = 13 # acres per MW
agvol_density = 15 # acres per MW

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



def land_use_analysis(capacity_dataframe, land_suitability_scenario, agvol_share, zones):
    capacity_to_develop = capacity_dataframe["NewCap"].sum()
    total_land_needed = capacity_to_develop * solar_density
    agvol_land_needed = total_land_needed * agvol_share * agvol_density
    
    print("Total Land Needed (acres): ", total_land_needed)
    print("Agvol Land Needed (acres): ", agvol_land_needed)

    if land_suitability_scenario == "base_case":



# What percent of good land is farmland