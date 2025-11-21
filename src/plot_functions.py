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
    zone_aggregation_method = sim_settings["zone_aggregation_method"]

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

    df = capacity_csv[['Resource', 'Zone', 'EndCap']].copy()
    df['EndCap'] = pd.to_numeric(df['EndCap'], errors='coerce').fillna(0.0)
    df = df.sort_values('EndCap', ascending=True)

    one_zone = plot_settings["all zones"]
    multiple_zones = plot_settings["zones_specific"]

    if one_zone == 1:
        for zone in df['Zone'].unique():
            zone_df = df[df['Zone'] == zone]
            plt.figure(figsize=(10, max(4, len(zone_df) * 0.15)))
            plt.barh(zone_df['Resource'], zone_df['EndCap'], color='tab:blue')
            plt.xlabel('EndCap')
            plt.title(f'Capacity by Resource in Zone {zone}')
            plt.tight_layout()
            filename = os.path.join(save_path, f'{sim_id}_Capacity_by_Resource_Zone_{zone}.png')
            plt.savefig(filename, dpi=150)
            plt.close()
            print(f"Saved: {filename}")

            filename= os.path.join(save_path, f'{sim_id}_Capacity_by_Zone')
            plt.savefig(filename, dpi = dpi)
            plt.close()
            print(f"Saved: {filename}")

    else:
        for zone in len(multiple_zones):
            which_zone = multiple_zones[zone]
            zone_df = df[df['Zone'] == which_zone]
            plt.figure(figsize=(10, max(4, len(zone_df) * 0.15)))
            plt.barh(zone_df['Resource'], zone_df['EndCap'], color='tab:blue')
            plt.xlabel('EndCap')
            plt.title(f'Capacity by Resource in Zone {zone}')
            plt.tight_layout()
            filename = os.path.join(save_path, f'{sim_id}_Capacity_by_Resource_Zone_{zone}.png')
            plt.savefig(filename, dpi=150)
            plt.close()
            print(f"Saved: {filename}")

            