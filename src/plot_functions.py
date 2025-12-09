import matplotlib.pyplot as plt
import os
import pandas as pd

##########################################
          # EMISSIONS PLOT #
##########################################

def emissions_plot(df, sim_settings, plot_settings, save_path, sim_id):
    # Remove the 'AnnualSum' row 
    df = df[df['Zone'] != 'AnnualSum']

    # Set the time index
    df = df.set_index('Zone')

    # Convert all other columns to numeric
    df = df.apply(pd.to_numeric)

    fig_size = plot_settings["fig_size"]
    dpi = plot_settings["dpi"]
    zone_aggregation_method = plot_settings["zone_aggregation_method"]

    if zone_aggregation_method == 0: 
         plt.figure(figsize=fig_size)
         plt.xlabel("Time")
         plt.ylabel("Emissions (MW)")
         x_labels = df.index[::24]  # your tick labels (strings)
         x_positions = range(len(df.index))[::24]  # numeric positions for ticks
         plt.xticks(x_positions, x_labels, rotation=45)      # set labels as strings
         plt.title("Emission by Zone Over Time")
         plt.grid(False)
         for col in df.columns[:-1]:  # skip 'Total' 
            plt.plot(range(len(df.index)), df[col], label=f'Zone {col}')
         plt.legend()
         
         filename= os.path.join(save_path, f'{sim_id}_Emissions_by_Zone')
         plt.savefig(filename, dpi = dpi)
         plt.close()
         print(f"Saved: {filename}")

    if zone_aggregation_method == 1: 
         plt.figure(figsize=fig_size)
         plt.xlabel("Time")
         plt.ylabel("Emissions (MW)")
         x_labels = df.index[::24]  # your tick labels (strings)
         x_positions = range(len(df.index))[::24]  # numeric positions for ticks
         plt.xticks(x_positions, x_labels, rotation=45)   
         plt.title("Total Emissions Over Time")
         plt.grid(False)
         plt.plot(range(len(df.index)), df['Total'], color= 'black')
         
         filename= os.path.join(save_path, f'{sim_id}_Emissions_Total')
         plt.savefig(filename, dpi = dpi)
         plt.close()
         print(f"Saved: {filename}")

    if zone_aggregation_method == 2: 
         plt.figure(figsize=fig_size)
         plt.xlabel("Time")
         plt.ylabel("Emissions (MW)")
         x_labels = df.index[::24]  # your tick labels (strings)
         x_positions = range(len(df.index))[::24]  # numeric positions for ticks
         plt.xticks(x_positions, x_labels, rotation=45)   
         plt.title("Emission by Zone Over Time")
         plt.grid(False)
         for col in df.columns[:-1]:  # skip 'Total' 
            plt.plot(range(len(df.index)), df[col], label=f'Zone {col}')
         plt.legend()
         
         filename1= os.path.join(save_path, f'{sim_id}_Emissions_by_Zone')
         plt.savefig(filename1, dpi = dpi)
         plt.close()
  

         plt.figure(figsize=fig_size)
         plt.xlabel("Time")
         plt.ylabel("Emissions (MW)")
         x_labels = df.index[::24]  # your tick labels (strings)
         x_positions = range(len(df.index))[::24]  # numeric positions for ticks
         plt.xticks(x_positions, x_labels, rotation=45)   
         plt.title("Total Emissions Over Time")
         plt.grid(False)
         plt.plot(range(len(df.index)), df['Total'], color= 'black')
         
         filename2= os.path.join(save_path, f'{sim_id}_Emissions_Total')
         plt.savefig(filename2, dpi = dpi)
         plt.close()
         print(f"Saved: {filename1} and {filename2}")



##########################################
          # POWER PLOT #
##########################################

def power_plot(df, sim_settings, plot_settings, save_path, sim_id):
    """
    Create power plots from power.csv according to power.json settings.

    zone_aggregation_method:
      0: For each zone, one plot with one line per *unit* (zone-tech-unit).
      1: For each zone, one plot with one line per *technology* (units summed).
      2: For each zone, do both (so 2 plots per zone).

    """

    # --- 1. Clean and set time index ---

    # Drop the rows that are not time steps
    if "Resource" in df.columns:
        df = df[~df["Resource"].isin(["Zone", "AnnualSum"])]
        df = df.set_index("Resource")
    else:
        df = df.copy()

    # Convert remaining columns to numeric
    df = df.apply(pd.to_numeric, errors="coerce")

    fig_size = plot_settings["fig_size"]
    dpi = plot_settings["dpi"]
    zone_aggregation_method = plot_settings["zone_aggregation_method"]

    # Basic x-axis: integer positions, labels every 24 steps (or reasonable fallback)
    x_positions = range(len(df.index))
    tick_step = 24 if len(df.index) >= 24 else max(1, len(df.index) // 10 or 1)
    x_labels = df.index[::tick_step]
    x_ticks = list(range(len(df.index)))[::tick_step]

    # --- 2. Helper: parse column names into (zone, tech, unit) ---

    def parse_zone_tech(colname):
        """
        Parse column names of the form:
          NY_Z_A_conventional_hydroelectric_1
          NENG_Rest_utilitypv_class1_2
        into (zone, tech, unit).

        Heuristic tailored to the sample file:
          - If name starts with 'NY_Z_', zone = first 3 tokens, else first 2.
          - Last token after '_' is assumed to be the unit index.
        """
        if colname in ("Resource", "Total"):
            return None, None, None

        base, unit = colname.rsplit("_", 1)  # split off unit index
        parts = base.split("_")

        if parts[0] == "NY" and len(parts) >= 3:
            zone_parts = parts[:3]      # e.g. NY_Z_A, NY_Z_G-I, NY_Z_C&E
            tech_parts = parts[3:]
        else:
            zone_parts = parts[:2]      # e.g. NENG_Rest, PJM_EMAC, PJM_Rest
            tech_parts = parts[2:]

        zone = "_".join(zone_parts)
        tech = "_".join(tech_parts) if tech_parts else "Unknown"

        return zone, tech, unit

    # --- 3. Build mapping: zone -> list of (colname, tech, unit) ---

    zone_to_cols = {}

    for col in df.columns:
        if col == "Total":
            continue  # we don't treat Total as a zone/tech/unit column here
        zone, tech, unit = parse_zone_tech(col)
        if zone is None:
            continue
        zone_to_cols.setdefault(zone, []).append((col, tech, unit))

    # --- 4. For each zone, build dataframes for:
    #       - by_unit: original columns for that zone
    #       - by_tech: sum across units for each technology
    # -------------------------------------------------------

    for zone, cols_info in zone_to_cols.items():
        # All column names for this zone
        zone_cols = [c for (c, t, u) in cols_info]

        # Dataframe with only that zone's columns (by unit)
        df_zone_by_unit = df[zone_cols].copy()

        # Dataframe aggregated by technology (sum across units)
        tech_to_cols = {}
        for (col, tech, unit) in cols_info:
            tech_to_cols.setdefault(tech, []).append(col)

        df_zone_by_tech = pd.DataFrame(index=df.index)
        for tech, tech_cols in tech_to_cols.items():
            df_zone_by_tech[tech] = df[tech_cols].sum(axis=1)

        # --- 5. Plot according to zone_aggregation_method ---

        # 0) One plot per zone, one line per unit (no aggregation)
        if zone_aggregation_method in (0, 2):
            plt.figure(figsize=fig_size)
            plt.xlabel("Time")
            plt.ylabel("Power (MW)")
            plt.xticks(x_ticks, x_labels, rotation=45)
            plt.title(f"Power by Unit – Zone {zone}")
            plt.grid(False)

            for (col, tech, unit) in cols_info:
                label = f"{tech} (unit {unit})"
                plt.plot(x_positions, df[col], label=label)

            plt.legend(fontsize="small", ncol=2)
            filename = os.path.join(save_path, f"{sim_id}_Power_Zone-{zone}_ByUnit")
            plt.savefig(filename, dpi=dpi, bbox_inches="tight")
            plt.close()
            print(f"Saved: {filename}")

        # 1) One plot per zone, one line per technology (aggregated over units)
        if zone_aggregation_method in (1, 2):
            plt.figure(figsize=fig_size)
            plt.xlabel("Time")
            plt.ylabel("Power (MW)")
            plt.xticks(x_ticks, x_labels, rotation=45)
            plt.title(f"Power by Technology – Zone {zone}")
            plt.grid(False)

            for tech in df_zone_by_tech.columns:
                plt.plot(x_positions, df_zone_by_tech[tech], label=tech)

            plt.legend(fontsize="small", ncol=2)
            filename = os.path.join(save_path, f"{sim_id}_Power_Zone-{zone}_ByTech")
            plt.savefig(filename, dpi=dpi, bbox_inches="tight")
            plt.close()
            print(f"Saved: {filename}")


        

##########################################
# CAPACITY PLOT FUNCTIONS
##########################################


def capacity_plot(capacity_csv, sim_settings, plot_settings, save_path, sim_id):

# want to plot by zone and by resource for the zones called
    zones_specific = plot_settings["zones_specific"]
    fig_size = plot_settings["fig_size"]
    dpi = plot_settings["dpi"]
    resource_types = plot_settings["Recource Types"]

    df = capacity_csv.copy()

    resources = ["hydro", "gas", "wind", "utilitypv", "nuclear", "trans", "biomass", "distributed", "photovoltaic"]

    import re

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

    start_cap = resource_df["StartCap"]
    end_cap = resource_df["EndCap"]
    cap_added = end - start

    def plot_resource_capacity(resource_df, resource_name, x_axis_name):
        x_axis = resource_df[x_axis_name]

        plt.figure(figsize=fig_size)
        plt.xlabel("Time")
        plt.ylabel("Capacity (MW)")
        plt.title(f"Capacity Over Time for {resource_name}")
        plt.grid(False)

        # Create tick positions and labels
        x_labels = resource_df
        x_positions = range(len(resource_df.index))[::24]  # numeric positions for ticks

        plt.xticks(x_positions, x_labels, rotation=45)

        plt.bar(
            x=range(len(resource_df.index)),   # numeric x positions
            height=x_axis,                     # y values
            width=1.0,                         # bar width (adjust if needed)
            label=x_axis_name
        )

        plt.legend()

    
    for resource_type in resource_types:
        if resource_type == "Wind":
            plot_resource_capacity(wind_df, "Wind", "EndCap")
            filename= os.path.join(save_path, f'{sim_id}_Capacity_Wind')
            plt.savefig(filename, dpi = dpi)
            plt.close()
            print(f"Saved: {filename}")
        elif resource_type == "Gas":
            plot_resource_capacity(gas_df, "Gas", "EndCap")
            filename= os.path.join(save_path, f'{sim_id}_Capacity_Gas')
            plt.savefig(filename, dpi = dpi)
            plt.close()
            print(f"Saved: {filename}")
        elif resource_type == "Hydro":
            plot_resource_capacity(hydro_df, "Hydro", "EndCap")
            filename= os.path.join(save_path, f'{sim_id}_Capacity_Hydro')
            plt.savefig(filename, dpi = dpi)
            plt.close()
            print(f"Saved: {filename}")
        elif resource_type == "Solar":
            plot_resource_capacity(solar_df, "Solar", "EndCap")
            filename= os.path.join(save_path, f'{sim_id}_Capacity_Solar')
            plt.savefig(filename, dpi = dpi)
            plt.close()
            print(f"Saved: {filename}")
        elif resource_type == "Nuclear":
            plot_resource_capacity(nuclear_df, "Nuclear", "EndCap")
            filename= os.path.join(save_path, f'{sim_id}_Capacity_Nuclear')
            plt.savefig(filename, dpi = dpi)
            plt.close()
            print(f"Saved: {filename}")
        elif resource_type == "Transmission":
            plot_resource_capacity(trans_df, "Transmission", "EndCap")
            filename= os.path.join(save_path, f'{sim_id}_Capacity_Transmission')
            plt.savefig(filename, dpi = dpi)
            plt.close()
            print(f"Saved: {filename}")
        elif resource_type == "Biomass":
            plot_resource_capacity(biomass_df, "Biomass", "EndCap")
            filename= os.path.join(save_path, f'{sim_id}_Capacity_Biomass')
            plt.savefig(filename, dpi = dpi)
            plt.close()
            print(f"Saved: {filename}")
        elif resource_type == "Distributed":
            plot_resource_capacity(distributed_df, "Distributed", "EndCap")
            filename= os.path.join(save_path, f'{sim_id}_Capacity_Distributed')
            plt.savefig(filename, dpi = dpi)
            plt.close()
            print(f"Saved: {filename}")
