# This is the main file you need to run

import json
import os
import subprocess
from pathlib import Path
import datetime

import numpy as np
import pandas as pd

from plot_functions import emissions_plot


def load_settings():
    """
    Load simulation_settings.json and return (settings, project_root_path).
    Assumes this file lives in NYS-LAND-USE/src/main.py.
    """
    project_root = Path(__file__).resolve().parents[1]  # NYS-LAND-USE/
    sim_settings_path = project_root / "input" / "simulation_settings.json"
    with sim_settings_path.open("r") as f:
        settings = json.load(f)
    return settings, project_root


def load_plot_settings(project_root):
    """
    Load plot settings (currently only emissions.json).
    """
    plot_settings_path = project_root / "input" / "plot_settings"
    emissions_json_path = plot_settings_path / "emissions.json"
    with emissions_json_path.open("r") as f:
        emissions_settings = json.load(f)
    return emissions_settings


def run_genx_cases(settings, project_root):
    """
    Run GenX for all scenarios specified in settings["genx"]["scenarios"].
    """
    genx_cfg = settings["genx"]

    julia_exe = genx_cfg["julia_executable"]
    julia_project = genx_cfg["project"]
    base_results_dir = project_root / genx_cfg["base_results_dir"]
    scenarios = genx_cfg["scenarios"]

    for scen in scenarios:
        case_dir = (base_results_dir / scen).resolve()
        print("\n==============================")
        print(f"Running GenX scenario: {scen}")
        print(f"Case directory: {case_dir}")
        print("==============================\n")

        # Command:
        # julia --project=<env> -e 'using GenX; run_genx_case!(abspath(ARGS[1]))' <case_dir>
        cmd = [
            julia_exe,
            f"--project={julia_project}",
            "-e",
            'using GenX; run_genx_case!(abspath(ARGS[1]))',
            str(case_dir),
        ]

        subprocess.run(cmd, check=True)


def main():
    # 1) Load settings + project root
    simulation_settings, project_root = load_settings()

    # 2) Run GenX for all scenarios
    run_genx_cases(simulation_settings, project_root)

    # 3) Load plot settings
    emissions_settings = load_plot_settings(project_root)

    # 4) Prepare base output folder
    sim_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    base_save_path = project_root / simulation_settings["save_path"]

    # 5) Loop over scenarios again: read emissions and make plots
    genx_cfg = simulation_settings["genx"]
    base_results_dir = project_root / genx_cfg["base_results_dir"]
    scenarios = genx_cfg["scenarios"]
    emissions_rel_path = genx_cfg.get("emissions_file", "emissions.csv")

    for scen in scenarios:
        # Where GenX wrote results for this scenario
        case_dir = (base_results_dir / scen).resolve()
        emissions_csv_path = case_dir / emissions_rel_path

        print(f"\nLoading emissions for scenario {scen}: {emissions_csv_path}")
        emissions_csv = pd.read_csv(emissions_csv_path)

        # Create a per-scenario output folder, e.g. output/s1/202511181530/
        scenario_save_dir = base_save_path / scen / sim_timestamp
        os.makedirs(scenario_save_dir, exist_ok=True)

        # 6) Create plots if requested
        if simulation_settings.get("emissions_plot", 0) == 1:
            print(f"Creating emissions plot for scenario {scen}...")
            # You can pass scen into the plot via sim_id if you like
            sim_id = f"{sim_timestamp}_{scen}"
            emissions_plot(
                emissions_csv,
                simulation_settings,
                emissions_settings,
                scenario_save_dir,
                sim_id,
            )

    print("\nAll scenarios complete.")


if __name__ == "__main__":
    main()
