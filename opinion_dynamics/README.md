# Zhang Opinion Dynamics Simulation Project

This project simulates the generalized Zhang et al.-style opinion dynamics model

```math
\dot v_i = (I - v_i v_i^T) \sum_j A_{ij} U_{k-1}(v_i^T v_j) v_j
```

where each opinion state satisfies `v_i in S^{d-1}`.

For `d = 2`, it also solves the corresponding scalar k-harmonic Kuramoto model

```math
\dot\theta_i = \sum_j A_{ij}\sin(k(\theta_j - \theta_i)).
```

## Folder structure

```text
input/
  settings.json
  graph.json
src/
  main.py
  dynamics.py
  graph_utils.py
  plot_functions.py
output/
  <timestamp>/
```

## How to run

From the project root:

```bash
python src/main.py
```

A timestamped folder will be created under `output/` with plots, adjacency files,
solution CSVs, initial conditions, and a copy of the settings used.

## Important settings

In `input/settings.json`:

- `d`: dimension of the ambient opinion vector space
- `k`: harmonic parameter
- `initial_condition.type`: one of
  - `random`
  - `random_sphere`
  - `random_angles` for d=2
  - `two_cluster` for d=2
  - `k_cluster` for d=2

In `input/graph.json`:

- `graph_type`: one of
  - `path`
  - `cycle`
  - `complete`
  - `star`
  - `erdos_renyi`
  - `from_edges`
  - `from_adjacency_csv`

## Examples

For a 6-node path graph:

```json
{
  "graph_type": "path",
  "num_nodes": 6
}
```

For a custom edge list:

```json
{
  "graph_type": "from_edges",
  "num_nodes": 4,
  "weighted": false,
  "edges": [[0, 1], [1, 2], [2, 3]]
}
```
