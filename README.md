# NYS-Land-Use
This repo is meant to store all of our analyses and figures for the NY Land Use project under the 2040 clean energy targets. 

# Simulation Workflow
There are three main folders in this repo: 
- input
- output
- src


Every simulation starts by generating a **simulation ID** using the `get_sim_id.py` file.  
You **don’t need to modify** this file — just run it and copy the printed output.  
This ID will uniquely identify all files, plots, and outputs from your run.

Below is the step-by-step workflow for running one complete simulation:

###  Src Folder

#### Step 1 — Generate Simulation ID
 * Run `get_sim_id.py`

---
###  Input Folder
#### Step 2 — Add GenX Results
* Copy the GenX results you want to analyze into the GenX_results folder
* Rename this folder to match your simulation ID.


#### Step 3 — Update simulation settings
* Open simulation_settings.json.
* Paste your new simulation ID into the "simulation_id" field.
* Update any other settings as needed.

#### Step 4 — Configure plot settings 
* Go to the plot_settings folder.
Open the file that matches the plot type you want (e.g, emissions_plot_settings.json).
* Adjust any parameters for your analysis.
---

### Src Folder 
#### Step 5 - Run simulation
* run `main.py`

---

### Output folder
#### Step 6 - View your results
* Each simulation run will have its own output folder, named using your simulation ID.
* Inside, you’ll find plots, data summaries, and other generated outputs.

---

# User Settings

### simulation_settings 
The simulation_settings.json file lets you control what your simulation run will do — which plots to create, how to aggregate data, and how to label your outputs.

* simulation_id: Insert the datetime of your simulation run. This will be used to label plots and any output files associated to your model run. To get the datetime, run the python file "get_sim_id.py" in the src folder and paste that result into this section of the  simultation_settings.json file. 

* emissions_plot: Set to 1 to generate an emissions plot for your analysis, or 0 to skip it.

* demand_plot: Set to 1 to generate a demand plot for your analysis, or 0 to skip it.

* capacity_plot: Set to 1 to generate an capacity plot for your analysis, or 0 to skip it.

* zone_aggregation_method: Choose how plots aggregate data across zones:
    * 0: Disaggregate by zone
    * 1: Aggregate all zones together
    * 2: Generate both disaggregated and aggregated analyses