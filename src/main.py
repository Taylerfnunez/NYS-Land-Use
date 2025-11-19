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
    genx_inputs_dir = project_root / genx_cfg["genx_inputs_dir"]
    scenarios = genx_cfg["scenarios"]

    for scen in scenarios:
        case_dir = (genx_inputs_dir / scen).resolve()
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
      'system', 'settings', 'resources', 'policies', 'TDR_results'.
    - That way we grab outputs like:
      - emissions.csv
      - results.csv
      - extra_outputs/
      - any other output CSVs GenX writes.
    """
    ignore_dirs = {"system", "settings", "resources", "policies"}

    for item in case_dir.iterdir():
        # Skip known input-like directories
        if item.is_dir() and item.name in ignore_dirs:
            continue

        # Optionally skip specific files you don't want to copy
        if item.is_file() and item.name == "powergenome_case_settings.yml":
            continue

        dest = scenario_save_dir / item.name

        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        elif item.is_file():
            shutil.copy(item, dest)
        else:
            # symlinks or weird stuff – skip
            print(f"Skipping non-regular item: {item}")


def write_metadata(simulation_settings, timestamp_root: Path):
    """
    Write a metadata.txt file containing the contents of simulation_settings.json
    into the timestamped run directory.
    """
    metadata_path = timestamp_root / "metadata.txt"
    with metadata_path.open("w") as f:
        # Pretty-print the JSON so it's easy to read / diff
        json.dump(simulation_settings, f, indent=2)
    print(f"Metadata written to {metadata_path}")


def main():
    # 1) Load settings + project root
    simulation_settings, project_root = load_settings()
    run_genx_flag = simulation_settings.get("run_genx", 1)

    # 2) Optionally run GenX for all scenarios
    if run_genx_flag == 1:
        print("run_genx = 1 → Running GenX cases before plotting.")
        run_genx_cases(simulation_settings, project_root)
    else:
        print("run_genx = 0 → Skipping GenX runs and using existing outputs.")

    # 3) Load plot settings
    emissions_settings = load_plot_settings(project_root)

    # 4) Make a timestamped parent directory in output/
    sim_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    base_output_root = project_root / simulation_settings["save_path"]
    timestamp_root = base_output_root / sim_timestamp
    os.makedirs(timestamp_root, exist_ok=True)

    # 4b) Write metadata for this run
    write_metadata(simulation_settings, timestamp_root)

    # 5) Determine where to read scenario outputs from
    genx_cfg = simulation_settings["genx"]
    scenarios = genx_cfg["scenarios"]
    emissions_rel_path = Path(genx_cfg.get("emissions_file", "emissions.csv"))

    if run_genx_flag == 1:
        # When we just ran GenX, outputs are in the case directories
        base_case_dir = project_root / genx_cfg["genx_inputs_dir"]
    else:
        # When not running GenX, use precomputed outputs
        genx_outputs_dir_rel = simulation_settings.get("genx_outputs_dir")
        if genx_outputs_dir_rel is None:
            raise KeyError(
                "run_genx is 0 but 'genx_outputs_dir' is not set in simulation_settings.json."
            )
        base_case_dir = project_root / genx_outputs_dir_rel

    # 6) Loop over scenarios: copy results & create plots
    for scen in scenarios:
        print(f"\n=== Processing scenario {scen} ===")

        # The directory that contains the outputs for this scenario
        case_dir = (base_case_dir / scen).resolve()
        if not case_dir.exists():
            raise FileNotFoundError(
                f"Expected case directory for scenario '{scen}' not found at:\n"
                f"  {case_dir}\n"
                f"Check 'genx_inputs_dir' / 'genx_outputs_dir' and scenario names."
            )

        # Where we want to store this run's organized outputs:
        # output/<timestamp>/s1, s2, s3, ...
        scenario_save_dir = timestamp_root / scen
        os.makedirs(scenario_save_dir, exist_ok=True)

        # Copy all outputs for this scenario into the output structure
        print(f"Copying results from {case_dir} -> {scenario_save_dir}")
        copy_genx_results_to_output(case_dir, scenario_save_dir)

        # ---- DELETE ORIGINAL OUTPUT FOLDERS ----
        genx_output_dirs = ["results", "extra_outputs","TDR_results"]
        
        for folder in genx_output_dirs:
            folder_path = case_dir / folder
            if folder_path.exists() and folder_path.is_dir():
                print(f"Deleting GenX output folder: {folder_path}")
                shutil.rmtree(folder_path)


        # Load emissions from the COPIED location
        emissions_csv_path = scenario_save_dir / emissions_rel_path
        print(f"Loading emissions from {emissions_csv_path}")
        emissions_csv = pd.read_csv(emissions_csv_path)

        # 7) Create plots (saved in the same scenario folder)
        if simulation_settings.get("generate_emissions_plot", 0) == 1:
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
