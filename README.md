# NYS-Land-Use

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