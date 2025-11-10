# NYS-Land-Use
This repo is meant to store all of our analyses and figures for the NY Land Use project under the 2040 clean energy targets. 

# Simulation Workflow
There are three main folders in this repo: 
- final_project
- input
- output
- src

Below is the step-by-step workflow for running one complete simulation:

---
###  Input Folder
#### Step 1 — Add GenX Results
* Copy the GenX results you want to analyze into the GenX_results folder
* Rename this folder 


#### Step 2 — Update simulation settings
* Open simulation_settings.json.
* Paste the name of your GenX results folder into the GenX_results_folder key.
* Update any other settings as needed.

#### Step 3 — Configure plot settings 
* Go to the plot_settings folder.
Open the file that matches the plot type you want (e.g, emissions.json).
* Adjust any parameters for your analysis.
---

### Src Folder 
#### Step 4 - Run simulation
* run `main.py`

---

### Output folder
#### Step 5 - View your results
* Each simulation run will have its own output folder, named after the date and time you ran the main.py.
* Inside, you’ll find plots, data summaries, and other generated outputs.

---

###  Final Project Folder
The final_project folder will contain any other additional content you would like to save as it pertains to this project. This can include presentations, data, reports, sub-anaylses, images, etc. 

# User Settings

### simulation_settings 
The simulation_settings.json file lets you control what your simulation run will do — which plots to create, how to aggregate data, and how to label your outputs.

* GenX_results_folder: Insert the name of the GenX results folder you would like to use for your analysis

* emissions_plot: Set to 1 to generate an emissions plot for your analysis, or 0 to skip it.

* demand_plot: Set to 1 to generate a demand plot for your analysis, or 0 to skip it.

* capacity_plot: Set to 1 to generate an capacity plot for your analysis, or 0 to skip it.

* power_plot: Set to 1 to generate an power plot for your analysis, or 0 to skip it.

* zone_aggregation_method: Choose how plots aggregate data across zones:
    * 0: Disaggregate by zone
    * 1: Aggregate all zones together
    * 2: Generate both disaggregated and aggregated analyses


### plot_settings
The plot_settings folder contains JSON files for each plot you would like to create. Each plot will have the following settings to decide:

*  fig_size: Figure size (e.g. [12, 6])
*  dpi: Plot resolution (e.g. 150)
*  title_all_zones: If you selected to have a plot for all zones aggregated, here's where you would define the title
* x_label_all_zones: If you selected to have a plot for all zones aggregated, here's where you would define the x-axis label
* y_label_all_zones: If you selected to have a plot for all zones aggregated, here's where you would define the y-axis label
* title_by_zone: If you selected to have a plot for all zones disaggregated, here's where you would define the title
* x_label_by_zone: If you selected to have a plot for all zones disaggregated, here's where you would define the x-axis label
* y_label_by_zone: If you selected to have a plot for all zones disaggregated, here's where you would define the y-axis label