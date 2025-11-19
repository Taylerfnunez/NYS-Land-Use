import matplotlib.pyplot as plt
import os
import pandas as pd



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
