
import matplotlib.pyplot as plt
import os
import pandas as pd
from collections import defaultdict


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
          # POWER PLOTS #
##########################################



# POWER PLOT – HELPERS

def infer_technology(tokens):
    """
    Given the tail tokens of a resource name (after region/zone),
    infer a high-level technology label like 'solar', 'nuclear', etc.
    """
    tokens_lower = [t.lower() for t in tokens]
    joined = "_".join(tokens_lower)

    # Solar: utilitypv, distpv, solar_pv, photovoltaic, etc.
    if (
        any("solar" in t for t in tokens_lower)
        or "pv" in joined          # catches utilitypv, distpv, etc.
        or "photovoltaic" in joined
    ):
        return "solar"

    # Land-based / onshore wind
    if any("landbasedwind" in t or "landbased_wind" in t for t in tokens_lower):
        return "land_based_wind"
    if "onshore" in joined and "wind" in joined:
        return "land_based_wind"

    # Offshore wind
    if "offshore" in joined and "wind" in joined:
        return "offshore_wind"

    # Hydro / hydroelectric, including small_hydroelectric
    if any("hydro" in t or "hydroelectric" in t for t in tokens_lower):
        return "hydroelectric"

    # Nuclear
    if any("nuclear" in t for t in tokens_lower):
        return "nuclear"

    # Natural gas
    if ("gas" in joined) or ("ngcc" in joined) or ("ngct" in joined):
        return "natural_gas"

    # Coal
    if "coal" in joined:
        return "coal"

    # Storage / battery
    if "battery" in joined or "storage" in joined:
        return "storage"

    # Biomass
    if "biomass" in joined:
        return "biomass"

    # Fallback: first token
    return tokens_lower[0] if tokens_lower else None


def parse_resource_name(name):
    """
    Parse a PowerGenome-style resource name into region, zone, technology.

    Examples:
      NY_Z_A_landbasedwind_class1_advanced_1
      NY_Z_D_small_hydroelectric_1
      PJM_EMAC_utilitypv_class1_advanced_1

    Returns:
      {"region": ..., "zone": ..., "technology": ...}
    """
    parts = name.split("_")
    if not parts:
        return {"region": None, "zone": None, "technology": None}

    region = parts[0]
    idx = 1
    zone = None

    # Special handling for NY with explicit 'Z'
    if region == "NY" and idx < len(parts) and parts[idx] == "Z":
        idx += 1
        if idx < len(parts):
            zone = parts[idx]
            idx += 1
    else:
        # For PJM, NENG, etc.: decide if second token is zone or tech
        if idx < len(parts):
            second = parts[idx]
            second_l = second.lower()

            tech_like_keywords = (
                "solar", "wind", "hydro", "hydroelectric",
                "nuclear", "gas", "coal", "battery", "storage",
                "pv", "biomass", "diesel", "geothermal", "oil"
            )

            if any(k in second_l for k in tech_like_keywords):
                # second token is actually technology
                pass
            else:
                # treat second token as zone (e.g. EMAC, Rest)
                zone = second
                idx += 1

    # Everything after region/zone is tech-related
    tech_tokens = parts[idx:]
    technology = infer_technology(tech_tokens)

    return {
        "region": region,
        "zone": zone,
        "technology": technology,
    }


def compute_zone_label(meta):
    """
    Turn region + zone into a label like:
      NY + A      -> 'NY_A'
      PJM + EMAC  -> 'PJM_EMAC'
      NENG + Rest -> 'NENG_Rest'
    If zone is None, returns just the region.
    """
    region = meta.get("region")
    zone = meta.get("zone")
    if region is None:
        return None
    if zone is None:
        return region
    return f"{region}_{zone}"


def build_index_from_power_df(df):
    """
    Given the raw power.csv DataFrame, build an index dictionary:
      index = {
        "parsed": {resource_name: {"region": ..., "zone": ..., "technology": ...}},
        "by_technology": {tech: [resource_names...]},
      }
    Only uses column names that look like resources.
    """
    parsed = {}
    for col in df.columns:
        if col in ("Resource", "Zone", "AnnualSum", "Total"):
            continue
        meta = parse_resource_name(col)
        parsed[col] = meta

    by_technology = defaultdict(list)
    for resource, meta in parsed.items():
        tech = meta.get("technology")
        if tech is not None:
            by_technology[tech].append(resource)

    return {
        "parsed": parsed,
        "by_technology": dict(by_technology),
    }


def build_tech_zone_mapping(index):
    """
    From the `index` dict, build:
      mapping[technology][zone_label] = [resource_name1, resource_name2, ...]
    """
    mapping = defaultdict(lambda: defaultdict(list))
    parsed = index["parsed"]

    for resource, meta in parsed.items():
        tech = meta.get("technology")
        zone_label = compute_zone_label(meta)

        if tech is None or zone_label is None:
            continue

        mapping[tech][zone_label].append(resource)

    return mapping


# CORE PLOTTING LOGIC 

def _plot_power_by_zone_df(
    df,
    index,
    fig_size,
    dpi,
    save_path,
    sim_id,
    technologies=None,
    zones_order=None,
    include_external_zones=True,
    external_zones=None,
    max_xticks=10,
):
    """
    Create one plot per zone.

    For each zone:
      - x-axis: time steps (t1, t2, ...)
      - lines: technologies (solar, nuclear, biomass, etc.), each aggregated
               over all units/resources in that zone & tech.
    """

    # Normalize technologies argument
    if isinstance(technologies, str):
        technologies = [technologies]

    if external_zones is None:
        external_zones = ["PJM_EMAC", "PJM_Rest", "NENG_Rest"]

    # Expect a 'Resource' column with 't1', 't2', ... rows
    if "Resource" not in df.columns:
        raise ValueError("Expected a 'Resource' column in power.csv")

    # Keep only time rows (t1, t2, ...)
    time_mask = df["Resource"].str.startswith("t")
    time_rows = df.loc[time_mask].copy()
    time_labels = time_rows["Resource"].tolist()
    n_points = len(time_labels)

    if n_points == 0:
        print("No time rows (t1, t2, ...) found in power.csv. Skipping zone plots.")
        return

    # x positions are numeric; labels are t1, t2, ...
    x_positions = list(range(n_points))

    # Tick thinning
    if max_xticks is not None and max_xticks > 0:
        step = max(1, n_points // max_xticks)
        tick_positions = x_positions[::step]
        tick_labels = [time_labels[i] for i in tick_positions]
    else:
        tick_positions = x_positions
        tick_labels = time_labels

    # Build zone -> tech -> [resources] mapping
    zone_tech_map = defaultdict(lambda: defaultdict(list))
    for resource, meta in index["parsed"].items():
        tech = meta.get("technology")
        zone_label = compute_zone_label(meta)

        if tech is None or zone_label is None:
            continue

        zone_tech_map[zone_label][tech].append(resource)

    # Determine which zones we will plot
    all_zones = list(zone_tech_map.keys())
    if zones_order is not None:
        zone_list = [z for z in zones_order if z in zone_tech_map]
    else:
        zone_list = sorted(all_zones)

    # Optionally drop external zones
    if not include_external_zones:
        zone_list = [z for z in zone_list if z not in external_zones]

    if not zone_list:
        print("No zones to plot in zone-based power plots.")
        return

    os.makedirs(save_path, exist_ok=True)

    for zone_label in zone_list:
        tech_to_resources = zone_tech_map[zone_label]

        # Restrict to specific technologies if requested
        if technologies is not None:
            tech_list = [t for t in technologies if t in tech_to_resources]
        else:
            tech_list = sorted(tech_to_resources.keys())

        if not tech_list:
            print(f"No technologies to plot for zone {zone_label}. Skipping.")
            continue

        print(f"\nPlotting zone: {zone_label}")
        print("Technologies in this zone:", tech_list)

        fig, ax = plt.subplots(figsize=fig_size)

        # Add extra space on the right for the legend
        plt.subplots_adjust(right=0.75)

        any_plotted = False

        for tech in tech_list:
            resources = tech_to_resources[tech]
            # Only keep columns that exist in df
            cols = [r for r in resources if r in time_rows.columns]
            if not cols:
                print(f"  Tech {tech}: no matching columns in power.csv, skipping.")
                continue

            # Sum across all resources for this zone & tech at each time step
            tech_series = time_rows[cols].sum(axis=1).to_numpy()

            ax.plot(x_positions, tech_series, label=tech)
            any_plotted = True
            print(f"  Tech {tech}: plotted {len(cols)} resources.")

        if not any_plotted:
            print(f"  No data plotted for zone {zone_label}, closing figure.")
            plt.close(fig)
            continue

        ax.set_xlabel("Time step")
        ax.set_ylabel("Power (MW)")
        ax.set_title(f"{zone_label} Power by technology")

        # Sparse x-axis labels
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45)

        # Legend outside
        ax.legend(
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            borderaxespad=0.0,
        )

        plt.tight_layout()

        filename = os.path.join(save_path, f"{sim_id}_Power_Zone-{zone_label}_ByTech")
        fig.savefig(filename, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {filename}")


def _plot_power_by_technology_df(
    df,
    index,
    fig_size,
    dpi,
    save_path,
    sim_id,
    technologies=None,
    zones_order=None,
    include_external_zones=True,
    external_zones=None,
    max_xticks=10,
):
    """
    Internal helper: create one plot per technology.

    df is the raw power.csv DataFrame (as read in main.py).
    """

    # Normalize technologies argument
    if isinstance(technologies, str):
        technologies = [technologies]

    if external_zones is None:
        external_zones = ["PJM_EMAC", "PJM_Rest", "NENG_Rest"]

    # Expect a 'Resource' column with 't1', 't2', ... rows
    if "Resource" not in df.columns:
        raise ValueError("Expected a 'Resource' column in power.csv")

    # Keep only time rows (t1, t2, ...)
    time_mask = df["Resource"].str.startswith("t")
    time_rows = df.loc[time_mask].copy()
    time_labels = time_rows["Resource"].tolist()
    n_points = len(time_labels)

    if n_points == 0:
        print("No time rows (t1, t2, ...) found in power.csv. Skipping power plots.")
        return

    # x positions are numeric; labels are t1, t2, ...
    x_positions = list(range(n_points))

    # Tick thinning
    if max_xticks is not None and max_xticks > 0:
        step = max(1, n_points // max_xticks)
        tick_positions = x_positions[::step]
        tick_labels = [time_labels[i] for i in tick_positions]
    else:
        tick_positions = x_positions
        tick_labels = time_labels

    tech_zone_map = build_tech_zone_mapping(index)

    # Determine which technologies to plot
    if technologies is None:
        technologies = sorted(tech_zone_map.keys())

    # Ensure output dir exists
    os.makedirs(save_path, exist_ok=True)

    for tech in technologies:
        if tech not in tech_zone_map:
            print(f"Skipping {tech}: no resources found in tech_zone_map.")
            continue

        zone_to_resources = tech_zone_map[tech]

        # Determine plotting order for zones
        if zones_order is not None:
            zone_list = [z for z in zones_order if z in zone_to_resources]
        else:
            zone_list = sorted(zone_to_resources.keys())

        # Optionally drop external zones
        if not include_external_zones:
            zone_list = [z for z in zone_list if z not in external_zones]

        if not zone_list:
            print(f"No zones to plot for technology {tech}.")
            continue

        print(f"\nPlotting technology: {tech}")
        print("Zones in this tech:", zone_list)

        fig, ax = plt.subplots(figsize=fig_size)

        # Add extra space on the right for the legend
        plt.subplots_adjust(right=0.75)

        any_plotted = False

        for zone_label in zone_list:
            resources = zone_to_resources[zone_label]
            # Only keep columns that exist in df
            cols = [r for r in resources if r in time_rows.columns]
            if not cols:
                print(f"  Zone {zone_label}: no matching columns in power.csv, skipping.")
                continue

            # Sum across all resources for this tech & zone at each time step
            zone_series = time_rows[cols].sum(axis=1).to_numpy()

            ax.plot(x_positions, zone_series, label=zone_label)
            any_plotted = True
            print(f"  Zone {zone_label}: plotted {len(cols)} resources.")

        if not any_plotted:
            print(f"  No data plotted for technology {tech}, closing figure.")
            plt.close(fig)
            continue

        ax.set_xlabel("Time step")
        ax.set_ylabel("Power (MW)")
        ax.set_title(f"{tech} Power by zone")

        # Sparse x-axis labels
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45)

        # Legend outside
        ax.legend(
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            borderaxespad=0.0,
        )

        plt.tight_layout()

        filename = os.path.join(save_path, f"{sim_id}_Power_{tech}_ByZone")
        fig.savefig(filename, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {filename}")





def _plot_power_total_by_technology_df(
    df,
    index,
    fig_size,
    dpi,
    save_path,
    sim_id,
    technologies=None,
    include_external_zones=True,
    external_zones=None,
    max_xticks=10,
):
    """
    Create a single plot where each line is a technology (solar, nuclear, etc.)
    and the value is the TOTAL power across all zones for that technology
    at each time step.

    If include_external_zones is False, we drop resources whose zone is in
    external_zones (e.g. PJM_EMAC, NENG_Rest, etc.).
    """

    # Normalize technologies argument
    if isinstance(technologies, str):
        technologies = [technologies]

    if external_zones is None:
        external_zones = ["PJM_EMAC", "PJM_Rest", "NENG_Rest"]

    # Expect a 'Resource' column with 't1', 't2', ... rows
    if "Resource" not in df.columns:
        raise ValueError("Expected a 'Resource' column in power.csv")

    # Keep only time rows (t1, t2, ...)
    time_mask = df["Resource"].str.startswith("t")
    time_rows = df.loc[time_mask].copy()
    time_labels = time_rows["Resource"].tolist()
    n_points = len(time_labels)

    if n_points == 0:
        print("No time rows (t1, t2, ...) found in power.csv. Skipping total-by-tech plot.")
        return

    # x positions are numeric; labels are t1, t2, ...
    x_positions = list(range(n_points))

    # Tick thinning
    if max_xticks is not None and max_xticks > 0:
        step = max(1, n_points // max_xticks)
        tick_positions = x_positions[::step]
        tick_labels = [time_labels[i] for i in tick_positions]
    else:
        tick_positions = x_positions
        tick_labels = time_labels

    # Build tech -> [resources] (optionally dropping external zones)
    tech_to_resources = defaultdict(list)
    for resource, meta in index["parsed"].items():
        tech = meta.get("technology")
        zone_label = compute_zone_label(meta)

        if tech is None or zone_label is None:
            continue

        if (not include_external_zones) and (zone_label in external_zones):
            continue

        tech_to_resources[tech].append(resource)

    # Restrict to specific technologies if requested
    if technologies is not None:
        tech_list = [t for t in technologies if t in tech_to_resources]
    else:
        tech_list = sorted(tech_to_resources.keys())

    if not tech_list:
        print("No technologies to plot in total-by-technology plot.")
        return

    os.makedirs(save_path, exist_ok=True)

    print("\nPlotting TOTAL power by technology (all zones aggregated).")
    print("Technologies:", tech_list)

    fig, ax = plt.subplots(figsize=fig_size)

    # Add extra space on the right for the legend
    plt.subplots_adjust(right=0.75)

    any_plotted = False

    for tech in tech_list:
        resources = tech_to_resources[tech]
        cols = [r for r in resources if r in time_rows.columns]
        if not cols:
            print(f"  Tech {tech}: no matching columns in power.csv, skipping.")
            continue

        # Sum across all resources for this technology at each time step
        tech_series = time_rows[cols].sum(axis=1).to_numpy()

        ax.plot(x_positions, tech_series, label=tech)
        any_plotted = True
        print(f"  Tech {tech}: plotted {len(cols)} resources.")

    if not any_plotted:
        print("No data plotted in total-by-technology figure, closing.")
        plt.close(fig)
        return

    ax.set_xlabel("Time step")
    ax.set_ylabel("Power (MW)")
    ax.set_title("Total power by technology (all zones)")

    # Sparse x-axis labels
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45)

    # Legend outside
    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        borderaxespad=0.0,
    )

    plt.tight_layout()

    filename = os.path.join(save_path, f"{sim_id}_Power_Total_ByTechnology")
    fig.savefig(filename, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {filename}")



def _plot_power_total_by_zone_df(
    df,
    index,
    fig_size,
    dpi,
    save_path,
    sim_id,
    zones_order=None,
    include_external_zones=True,
    external_zones=None,
    max_xticks=10,
):
    """
    Create a single plot where each line is a zone
    (NY_A, NY_B, PJM_EMAC, etc.) and the value is the TOTAL power
    across all technologies in that zone at each time step.

    If include_external_zones is False, we drop resources whose zone is in
    external_zones (e.g. PJM_EMAC, NENG_Rest, etc.).
    """

    if external_zones is None:
        external_zones = ["PJM_EMAC", "PJM_Rest", "NENG_Rest"]

    # Expect a 'Resource' column with 't1', 't2', ... rows
    if "Resource" not in df.columns:
        raise ValueError("Expected a 'Resource' column in power.csv")

    # Keep only time rows (t1, t2, ...)
    time_mask = df["Resource"].str.startswith("t")
    time_rows = df.loc[time_mask].copy()
    time_labels = time_rows["Resource"].tolist()
    n_points = len(time_labels)

    if n_points == 0:
        print("No time rows (t1, t2, ...) found in power.csv. "
              "Skipping total-by-zone plot.")
        return

    # x positions are numeric; labels are t1, t2, ...
    x_positions = list(range(n_points))

    # Tick thinning
    if max_xticks is not None and max_xticks > 0:
        step = max(1, n_points // max_xticks)
        tick_positions = x_positions[::step]
        tick_labels = [time_labels[i] for i in tick_positions]
    else:
        tick_positions = x_positions
        tick_labels = time_labels

    # Build zone -> [resources] mapping (optionally drop external zones)
    from collections import defaultdict
    zone_to_resources = defaultdict(list)
    for resource, meta in index["parsed"].items():
        zone_label = compute_zone_label(meta)
        if zone_label is None:
            continue
        if (not include_external_zones) and (zone_label in external_zones):
            continue
        zone_to_resources[zone_label].append(resource)

    if not zone_to_resources:
        print("No zones/resources to plot in total-by-zone plot.")
        return

    # Determine which zones to plot and order
    all_zones = list(zone_to_resources.keys())
    if zones_order is not None:
        zone_list = [z for z in zones_order if z in zone_to_resources]
    else:
        zone_list = sorted(all_zones)

    if not zone_list:
        print("No zones to plot in total-by-zone plot after filtering/order.")
        return

    os.makedirs(save_path, exist_ok=True)

    print("\nPlotting TOTAL power by zone (all technologies aggregated).")
    print("Zones:", zone_list)

    fig, ax = plt.subplots(figsize=fig_size)

    # Add extra space on the right for the legend
    plt.subplots_adjust(right=0.75)

    any_plotted = False

    for zone_label in zone_list:
        resources = zone_to_resources[zone_label]
        cols = [r for r in resources if r in time_rows.columns]
        if not cols:
            print(f"  Zone {zone_label}: no matching columns in power.csv, skipping.")
            continue

        # Sum across all resources for this zone at each time step
        zone_series = time_rows[cols].sum(axis=1).to_numpy()

        ax.plot(x_positions, zone_series, label=zone_label)
        any_plotted = True
        print(f"  Zone {zone_label}: plotted {len(cols)} resources.")

    if not any_plotted:
        print("No data plotted in total-by-zone figure, closing.")
        plt.close(fig)
        return

    ax.set_xlabel("Time step")
    ax.set_ylabel("Power (MW)")
    ax.set_title("Total power by zone (all technologies)")

    # Sparse x-axis labels
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45)

    # Legend outside
    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        borderaxespad=0.0,
    )

    plt.tight_layout()

    filename = os.path.join(save_path, f"{sim_id}_Power_Total_ByZone")
    fig.savefig(filename, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {filename}")





# POWER PLOT --(called by main.py)



def power_plot(df, sim_settings, plot_settings, save_path, sim_id):
    """
    Create power plots from power.csv according to power.json settings.

    Modes (plot_settings["mode"]):
      - "by_technology": one plot per technology; lines = zones
      - "by_zone":       one plot per zone;       lines = technologies
      - "both":          do both sets of plots

    Additional summary options:
      - total_by_technology (0/1): if 1, make ONE plot with lines = technologies,
                                   totals across all zones.
      - total_by_zone (0/1):       if 1, make ONE plot with lines = zones,
                                   totals across all technologies.
    """

    # Figure size & DPI from power.json
    fig_size = plot_settings.get("fig_size", [10, 6])
    dpi = plot_settings.get("dpi", 150)

    # Which plotting mode(s)?
    mode = plot_settings.get("mode", "by_technology")  # "by_technology", "by_zone", "both"

    # Technologies to plot (None = all detected)
    technologies = plot_settings.get("technologies", None)

    # Zone display order (optional)
    zones_order = plot_settings.get("zones_order", None)

    # External zone handling
    include_external_zones = bool(plot_settings.get("include_external_zones", 1))
    external_zones = plot_settings.get(
        "external_zones", ["PJM_EMAC", "PJM_Rest", "NENG_Rest"]
    )

    # X-axis label density
    max_xticks = int(plot_settings.get("max_xticks", 10))

    # Summary plot flags
    total_by_technology_flag = bool(plot_settings.get("total_by_technology", 1))
    total_by_zone_flag = bool(plot_settings.get("total_by_zone", 1))

    # Build index (region/zone/technology) from column names
    index = build_index_from_power_df(df)

    # 1) Technology-based plots: one figure per technology, lines = zones
    if mode in ("by_technology", "both"):
        _plot_power_by_technology_df(
            df=df,
            index=index,
            fig_size=fig_size,
            dpi=dpi,
            save_path=save_path,
            sim_id=sim_id,
            technologies=technologies,
            zones_order=zones_order,
            include_external_zones=include_external_zones,
            external_zones=external_zones,
            max_xticks=max_xticks,
        )

    # 2) Zone-based plots: one figure per zone, lines = technologies
    if mode in ("by_zone", "both"):
        _plot_power_by_zone_df(
            df=df,
            index=index,
            fig_size=fig_size,
            dpi=dpi,
            save_path=save_path,
            sim_id=sim_id,
            technologies=technologies,
            zones_order=zones_order,
            include_external_zones=include_external_zones,
            external_zones=external_zones,
            max_xticks=max_xticks,
        )

    # 3) SINGLE global plot: lines = technologies, totals across all zones
    if total_by_technology_flag:
        _plot_power_total_by_technology_df(
            df=df,
            index=index,
            fig_size=fig_size,
            dpi=dpi,
            save_path=save_path,
            sim_id=sim_id,
            technologies=technologies,
            include_external_zones=include_external_zones,
            external_zones=external_zones,
            max_xticks=max_xticks,
        )

    # 4) SINGLE global plot: lines = zones, totals across all technologies
    if total_by_zone_flag:
        _plot_power_total_by_zone_df(
            df=df,
            index=index,
            fig_size=fig_size,
            dpi=dpi,
            save_path=save_path,
            sim_id=sim_id,
            zones_order=zones_order,
            include_external_zones=include_external_zones,
            external_zones=external_zones,
            max_xticks=max_xticks,
        )


        



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
