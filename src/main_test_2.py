# main.py

import json
import os
import subprocess
import shutil
from pathlib import Path
import datetime

import numpy as np
import pandas as pd

from plot_functions import emissions_plot


def load_settings():
    """
    Load simulation_settings.json and return (settings, project_root_path).
    Assumes this file lives in NYS-Land-Use/src/main.py.
    """
    project_root = Path(__file__).resolve().parents[1]  # NYS-Land-Use/
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
    if "genx" not in settings:
        raise KeyError(
            "simulation_settings.json is missing the 'genx' section."
        )

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

        cmd = [
            julia_exe,
            f"--project={julia_project}",
            "-e",
            'using GenX; run_genx_case!(abspath(ARGS[1]))',
            str(case_dir),
        ]

        print("Running command:", " ".join(cmd))
        subprocess.run(cmd, check=True)


def copy_genx_results_to_output(case_dir: Path, scenario_save_dir: Path):
    """
    Copy GenX result files from the scenario folder into the scenario_save_dir.

    Strategy:
    - Copy everything in case_dir EXCEPT known input subfolders:
      'system', 'settings', 'resources', 'policies'.
    - That way we grab outputs like:
      - emissions.csv
      - results.csv
      - extra_outputs/
      - any other output CSVs GenX writes.
    """
    ignore_dirs = {"system", "settings", "resources", "policies", "TDR_results", "extra_outputs", "powergenome_case_settings.yml"}

    for item in case_dir.iterdir():
        if item.name in ignore_dirs:
            continue

        dest = scenario_save_dir / item.name

        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        elif item.is_file():
            shutil.copy(item, dest)
        else:
            # symlinks or weird stuff – skip
            print(f"Skipping non-regular item: {item}")


def main():
    # 1) Load settings + project root
    simulation_settings, project_root = load_settings()

    # 2) Run GenX for all scenarios (writes results into scenario folders)
    run_genx_cases(simulation_settings, project_root)

    # 3) Load plot settings
    emissions_settings = load_plot_settings(project_root)

    # 4) Make a timestamped parent directory in output/
    sim_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    base_output_root = project_root / simulation_settings["save_path"]
    timestamp_root = base_output_root / sim_timestamp
    os.makedirs(timestamp_root, exist_ok=True)

    # 5) Loop over scenarios: copy results & create plots
    genx_cfg = simulation_settings["genx"]
    base_results_dir = project_root / genx_cfg["base_results_dir"]
    scenarios = genx_cfg["scenarios"]
    emissions_rel_path = genx_cfg.get("emissions_file", "emissions.csv")

    for scen in scenarios:
        print(f"\n=== Processing scenario {scen} ===")

        # The original GenX case directory (inputs + outputs)
        case_dir = (base_results_dir / scen).resolve()

        # Where we want to store this run's organized outputs:
        # output/<timestamp>/s1, s2, s3, ...
        scenario_save_dir = timestamp_root / scen
        os.makedirs(scenario_save_dir, exist_ok=True)

        # Copy all outputs for this scenario into the output structure
        print(f"Copying results from {case_dir} -> {scenario_save_dir}")
        copy_genx_results_to_output(case_dir, scenario_save_dir)

        # Load emissions from the COPIED location
        emissions_csv_path = scenario_save_dir / emissions_rel_path
        print(f"Loading emissions from {emissions_csv_path}")
        emissions_csv = pd.read_csv(emissions_csv_path)

        # 6) Create plots (saved in the same scenario folder)
        if simulation_settings.get("emissions_plot", 0) == 1:
            sim_id = f"{sim_timestamp}_{scen}"
            print(f"Creating emissions plot for {scen}...")
            emissions_plot(
                emissions_csv,
                simulation_settings,
                emissions_settings,
                scenario_save_dir,
                sim_id,
            )

    print(f"\nAll scenarios complete. Results in: {timestamp_root}")


if __name__ == "__main__":
    main()
