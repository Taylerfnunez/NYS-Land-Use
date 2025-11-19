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

    This function:
      - drops the 'Zone' and 'AnnualSum' rows,
      - sets 'Resource' as the index (time steps),
      - plots either:
          0: by resource/zone (all columns except 'Total'),
          1: total only,
          2: both.
    """

    # Drop rows that are not actual time steps
    if "Resource" in df.columns:
        df = df[~df["Resource"].isin(["Zone", "AnnualSum"])]
        df = df.set_index("Resource")
    else:
        # If the structure ever changes, fall back gracefully
        df = df.copy()

    # Convert all other columns to numeric (coerce errors to NaN)
    df = df.apply(pd.to_numeric, errors="coerce")

    fig_size = plot_settings["fig_size"]
    dpi = plot_settings["dpi"]
    zone_aggregation_method = plot_settings["zone_aggregation_method"]

    # X-axis: positions 0..N-1, labels from index
    x_positions = range(len(df.index))
    # Choose tick step similar to your emissions plot (24 hours) if long enough
    tick_step = 24 if len(df.index) >= 24 else max(1, len(df.index) // 10 or 1)
    x_labels = df.index[::tick_step]
    x_ticks = list(range(len(df.index)))[::tick_step]

    # 0) Plot by resource/zone (all columns except 'Total')
    if zone_aggregation_method == 0:
        plt.figure(figsize=fig_size)
        plt.xlabel("Time")
        plt.ylabel("Power (MW)")
        plt.xticks(x_ticks, x_labels, rotation=45)
        plt.title("Power by Resource Over Time")
        plt.grid(False)

        for col in df.columns:
            if col == "Total":
                continue
            plt.plot(x_positions, df[col], label=col)

        plt.legend()
        filename = os.path.join(save_path, f"{sim_id}_Power_by_Resource")
        plt.savefig(filename, dpi=dpi, bbox_inches="tight")
        plt.close()
        print(f"Saved: {filename}")

    # 1) Plot total only
    if zone_aggregation_method == 1:
        if "Total" not in df.columns:
            print("Warning: 'Total' column not found in power.csv for total plot.")
        else:
            plt.figure(figsize=fig_size)
            plt.xlabel("Time")
            plt.ylabel("Power (MW)")
            plt.xticks(x_ticks, x_labels, rotation=45)
            plt.title("Total Power Over Time")
            plt.grid(False)
            plt.plot(x_positions, df["Total"], color="black")

            filename = os.path.join(save_path, f"{sim_id}_Power_Total")
            plt.savefig(filename, dpi=dpi, bbox_inches="tight")
            plt.close()
            print(f"Saved: {filename}")

    # 2) Plot both: by resource and total
    if zone_aggregation_method == 2:
        # By resource
        plt.figure(figsize=fig_size)
        plt.xlabel("Time")
        plt.ylabel("Power (MW)")
        plt.xticks(x_ticks, x_labels, rotation=45)
        plt.title("Power by Resource Over Time")
        plt.grid(False)

        for col in df.columns:
            if col == "Total":
                continue
            plt.plot(x_positions, df[col], label=col)

        plt.legend()
        filename1 = os.path.join(save_path, f"{sim_id}_Power_by_Resource")
        plt.savefig(filename1, dpi=dpi, bbox_inches="tight")
        plt.close()

        # Total
        if "Total" not in df.columns:
            print("Warning: 'Total' column not found in power.csv for total plot.")
            filename2 = None
        else:
            plt.figure(figsize=fig_size)
            plt.xlabel("Time")
            plt.ylabel("Power (MW)")
            plt.xticks(x_ticks, x_labels, rotation=45)
            plt.title("Total Power Over Time")
            plt.grid(False)
            plt.plot(x_positions, df["Total"], color="black")

            filename2 = os.path.join(save_path, f"{sim_id}_Power_Total")
            plt.savefig(filename2, dpi=dpi, bbox_inches="tight")
            plt.close()

        if filename2:
            print(f"Saved: {filename1} and {filename2}")
        else:
            print(f"Saved: {filename1} (no Total column found)")


        

##########################################
# CAPACITY PLOT FUNCTIONS
##########################################


def capacity_plot(capacity_csv, sim_settings, plot_settings, save_path, sim_id):

    df = capacity_csv[['Resource', 'EndCap']].copy()
    df['EndCap'] = pd.to_numeric(df['EndCap'], errors='coerce').fillna(0.0)
    df = df.sort_values('EndCap', ascending=True)

    plt.figure(figsize=(10, max(4, len(df) * 0.15)))
    plt.barh(df['Resource'], df['EndCap'], color='tab:blue')
    plt.xlabel('EndCap')
    plt.title(title or 'NY resources: EndCap by Resource')
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()
    print(f"Saved: {outpath}")


def plot_start_vs_end_topn(df: pd.DataFrame, outpath: str, top_n: int = 30) -> None:
    # Compare StartCap and EndCap for top N resources by EndCap
    cols = ['Resource', 'StartCap', 'EndCap']
    sub = df[cols].copy()
    for c in ['StartCap', 'EndCap']:
        sub[c] = pd.to_numeric(sub[c], errors='coerce').fillna(0.0)

    top = sub.sort_values('EndCap', ascending=False).head(top_n)
    if top.empty:
        print('No NY resources found to plot for Start vs End.')
        return

    ind = range(len(top))
    width = 0.35

    plt.figure(figsize=(10, max(4, len(top) * 0.25)))
    plt.bar(ind, top['StartCap'], width, label='StartCap', color='tab:gray')
    plt.bar([i + width for i in ind], top['EndCap'], width, label='EndCap', color='tab:green')
    plt.xticks([i + width / 2 for i in ind], top['Resource'], rotation=90)
    plt.ylabel('Capacity')
    plt.title(f'StartCap vs EndCap (top {len(top)} NY resources by EndCap)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()
    print(f"Saved: {outpath}")


def main() -> None:
    parser = argparse.ArgumentParser(description='Plot NY resources from a GenX capacity.csv')
    parser.add_argument('--csv', default='input/GenX_results/test1/capacity.csv', help='Path to capacity.csv')
    parser.add_argument('--outdir', default='output/plots_ny', help='Directory to save plots')
    parser.add_argument('--top', type=int, default=30, help='Top N resources (by EndCap) for the Start vs End plot')

    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    df = load_capacity(args.csv)
    ny = filter_ny(df)
    if ny.empty:
        print(f'No resources starting with "NY" found in {args.csv}')
        return

    endcap_path = os.path.join(args.outdir, 'ny_endcap_by_resource.png')
    start_end_path = os.path.join(args.outdir, f'ny_start_vs_end_top{args.top}.png')

    plot_endcap_bar(ny, endcap_path, title=f'NY resources EndCap ({os.path.basename(args.csv)})')
    plot_start_vs_end_topn(ny, start_end_path, top_n=args.top)


if __name__ == '__main__':
    main()
