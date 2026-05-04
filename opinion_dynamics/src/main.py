"""Main entry point for config-driven Zhang opinion dynamics simulations."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from dynamics import initial_conditions, solve_angle_model_if_d2, solve_vector_model
from graph_utils import adjacency_matrix, build_graph_from_config, save_graph_outputs
from plot_functions import make_all_plots


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


#def create_run_dir(root: Path) -> Path:
#    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
 #   out_dir = root / "output" / timestamp
 #   out_dir.mkdir(parents=True, exist_ok=False)
 #   return out_dir


def create_run_dir(root: Path, simulation_name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{simulation_name}_{timestamp}"
    out_dir = root / "output" / folder_name
    out_dir.mkdir(parents=True, exist_ok=False)
    return out_dir

def save_settings_copy(settings: dict, graph_cfg: dict, output_dir: Path) -> None:
    combined = {"settings": settings, "graph": graph_cfg}
    with open(output_dir / "settings_used.json", "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)

    with open(output_dir / "metadata.txt", "w", encoding="utf-8") as f:
        f.write("Zhang-style generalized Kuramoto opinion dynamics simulation\n")
        f.write("=" * 70 + "\n\n")
        f.write(json.dumps(combined, indent=2))
        f.write("\n")


def save_solution_csv(sol_v, output_dir: Path, n: int, d: int) -> None:
    columns = ["time"]
    data = {"time": sol_v.t}
    for i in range(n):
        for coord in range(d):
            col = f"node_{i}_coord_{coord}"
            columns.append(col)
            data[col] = sol_v.y[i * d + coord, :]
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(output_dir / "vector_solution.csv", index=False)


def main() -> None:
    root = project_root()
    input_dir = root / "input"

    settings = load_json(input_dir / "settings.json")
    graph_cfg = load_json(input_dir / "graph.json")

    # For k-cluster initial conditions, inherit k from settings unless specified.
    settings.setdefault("initial_condition", {})
    settings["initial_condition"].setdefault("k", settings["k"])

    simulation_name = settings["simulation_name"]

    output_dir = create_run_dir(root, simulation_name)
    save_settings_copy(settings, graph_cfg, output_dir)

    G = build_graph_from_config(graph_cfg)
    A = adjacency_matrix(G)
    save_graph_outputs(G, output_dir)

    rng = np.random.default_rng(settings.get("random_seed", None))
    n = G.number_of_nodes()
    d = int(settings["d"])
    v0 = initial_conditions(n=n, d=d, init_cfg=settings["initial_condition"], rng=rng)
    np.savetxt(output_dir / "initial_condition.csv", v0.reshape((n, d)), delimiter=",", fmt="%.10f")

    sol_v = solve_vector_model(A=A, settings=settings, v0=v0)
    if not sol_v.success:
        raise RuntimeError(f"Vector model solve failed: {sol_v.message}")

    sol_theta = solve_angle_model_if_d2(A=A, settings=settings, v0=v0)
    if sol_theta is not None and not sol_theta.success:
        raise RuntimeError(f"Angle model solve failed: {sol_theta.message}")

    if settings.get("save_solution_csv", True):
        save_solution_csv(sol_v, output_dir, n=n, d=d)
        if sol_theta is not None:
            pd.DataFrame({"time": sol_theta.t, **{f"theta_{i}": sol_theta.y[i] for i in range(n)}}).to_csv(
                output_dir / "angle_solution_d2.csv", index=False
            )

    make_all_plots(G=G, sol_v=sol_v, sol_theta=sol_theta, settings=settings, output_dir=output_dir)
    print(f"Simulation complete. Outputs saved to: {output_dir}")


if __name__ == "__main__":
    main()
