# This is the main file you need to run

import json
import os 
import numpy as np 
import pandas as pd
from plot_functions import emissions_plot
import datetime



if __name__ == "__main__":
    print("This function is running")

 # Load inputs
    
    #################################
    ### Load Simulation Settings ###
    #################################
    sim_settings_path = "input/simulation_settings.json"
    sim_settings_json_file = open(sim_settings_path, 'rb')
    simulation_settings = json.load(sim_settings_json_file)
    sim_settings_json_file.close()

    #################################
    ### Load Plot Settings ###
    #################################
    plot_settings_path = "input/plot_settings"


    # Emissions Plot Settings
    emissions_json_path = os.path.join(plot_settings_path, "emissions.json")
    with open(emissions_json_path, 'r') as f: #text
        emissions_settings = json.load(f)     #dict


    
    #################################
    ### Load CSV files ###
    #################################
    emissions_csv = pd.read_csv("input/GenX_results/20250611_test/emissions.csv")



 

# Run simulation and save results


   #################################
   ### Save Simulation Results ###
   #################################

    sim_id = datetime.datetime.now().strftime("%Y%m%d%H%M")
    save_path = simulation_settings["save_path"]

    # Create a subfolder named after id_string inside the output directory
    id_folder = os.path.basename(sim_id)
    save_path = os.path.join(save_path, id_folder)
    os.makedirs(save_path, exist_ok=True)
    

   #################################
        ### Create Plots ###
   #################################
    if simulation_settings["emissions_plot"] == 1:
        emissions_plot(emissions_csv, simulation_settings, emissions_settings, save_path, sim_id)
        




   
    

   

    
    
    
    