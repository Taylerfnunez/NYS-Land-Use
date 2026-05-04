"""Plotting functions for Zhang-style opinion dynamics simulations."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from dynamics import v_to_theta, wrap_angle


def _solution_as_array(sol_v, n: int, d: int) -> np.ndarray:
    """Return solution as array with shape (time, node, dim)."""
    return sol_v.y.T.reshape((-1, n, d))


def plot_graph(G: nx.Graph, output_dir: Path, dpi: int = 200) -> None:
    plt.figure(figsize=(6, 5))
    pos = nx.spring_layout(G, seed=0)
    nx.draw_networkx(G, pos=pos, node_color="white", edgecolors="black", with_labels=True)
    plt.title("Interaction graph")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_dir / "graph.png", dpi=dpi)
    plt.close()


def plot_vector_components(sol_v, n: int, d: int, output_dir: Path, dpi: int = 200) -> None:
    V = _solution_as_array(sol_v, n, d)
    t = sol_v.t
    for coord in range(d):
        plt.figure(figsize=(10, 5))
        for i in range(n):
            plt.plot(t, V[:, i, coord], label=f"node {i}")
        plt.xlabel("Time")
        plt.ylabel(f"component {coord}")
        plt.title(f"Opinion vector component {coord}")
        if n <= 12:
            plt.legend(loc="best")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / f"vector_component_{coord}.png", dpi=dpi)
        plt.close()


def plot_norms(sol_v, n: int, d: int, output_dir: Path, dpi: int = 200) -> None:
    V = _solution_as_array(sol_v, n, d)
    norms = np.linalg.norm(V, axis=2)
    plt.figure(figsize=(10, 5))
    for i in range(n):
        plt.plot(sol_v.t, norms[:, i], label=f"node {i}")
    plt.xlabel("Time")
    plt.ylabel(r"$\|v_i\|$")
    plt.title("Unit-norm preservation")
    if n <= 12:
        plt.legend(loc="best")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "norms.png", dpi=dpi)
    plt.close()


def plot_angles_if_d2(sol_v, sol_theta, n: int, output_dir: Path, dpi: int = 200) -> None:
    theta_from_v = np.zeros((n, len(sol_v.t)))
    for idx in range(len(sol_v.t)):
        theta_from_v[:, idx] = v_to_theta(sol_v.y[:, idx])

    fig, axes = plt.subplots(3 if sol_theta is not None else 1, 1, figsize=(10, 11), sharex=True)
    if sol_theta is None:
        axes = [axes]

    ax = axes[0]
    for i in range(n):
        ax.plot(sol_v.t, theta_from_v[i], label=f"node {i}")
    ax.set_title("Angles recovered from vector model")
    ax.set_ylabel("Angle (rad)")
    if n <= 12:
        ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    if sol_theta is not None:
        ax = axes[1]
        for i in range(n):
            ax.plot(sol_theta.t, sol_theta.y[i], label=f"node {i}")
        ax.set_title("Scalar k-harmonic Kuramoto angle model")
        ax.set_ylabel("Angle (rad)")
        if n <= 12:
            ax.legend(loc="best")
        ax.grid(True, alpha=0.3)

        ax = axes[2]
        angle_error = wrap_angle(theta_from_v - sol_theta.y)
        for i in range(n):
            ax.plot(sol_v.t, angle_error[i], label=f"node {i}")
        ax.set_title("Wrapped angle error: vector model vs angle model")
        ax.set_ylabel("Error (rad)")
        if n <= 12:
            ax.legend(loc="best")
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Time")
    plt.tight_layout()
    plt.savefig(output_dir / "angles_d2.png", dpi=dpi)
    plt.close()


def plot_circle_if_d2(sol_v, n: int, output_dir: Path, dpi: int = 200) -> None:
    plt.figure(figsize=(6, 6))
    circle = np.linspace(0, 2 * np.pi, 400)
    plt.plot(np.cos(circle), np.sin(circle), "k-", alpha=0.35)
    for i in range(n):
        x = sol_v.y[2 * i, :]
        y = sol_v.y[2 * i + 1, :]
        plt.plot(x, y, label=f"node {i}")
        plt.scatter(x[0], y[0], marker="o", s=30)
        plt.scatter(x[-1], y[-1], marker="x", s=50)
    plt.axis("equal")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Vector trajectories on unit circle")
    if n <= 12:
        plt.legend(loc="best")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "circle_trajectories_d2.png", dpi=dpi)
    plt.close()


def plot_sphere_if_d3(sol_v, n: int, output_dir: Path, dpi: int = 200) -> None:
    V = _solution_as_array(sol_v, n, 3)
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection="3d")

    # light sphere wireframe
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 15)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(xs, ys, zs, alpha=0.12, linewidth=0.5)

    for i in range(n):
        ax.plot(V[:, i, 0], V[:, i, 1], V[:, i, 2], label=f"node {i}")
        ax.scatter(V[0, i, 0], V[0, i, 1], V[0, i, 2], marker="o", s=30)
        ax.scatter(V[-1, i, 0], V[-1, i, 1], V[-1, i, 2], marker="x", s=50)

    ax.set_title("Vector trajectories on unit sphere")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    if n <= 10:
        ax.legend(loc="best")
    plt.tight_layout()
    plt.savefig(output_dir / "sphere_trajectories_d3.png", dpi=dpi)
    plt.close()


def make_all_plots(G, sol_v, sol_theta, settings: dict, output_dir: Path) -> None:
    n = G.number_of_nodes()
    d = int(settings["d"])
    plot_cfg = settings.get("plots", {})
    dpi = int(plot_cfg.get("dpi", 200))

    plot_graph(G, output_dir, dpi=dpi)

    if plot_cfg.get("plot_vector_components", True):
        plot_vector_components(sol_v, n, d, output_dir, dpi=dpi)
    if plot_cfg.get("plot_norms", True):
        plot_norms(sol_v, n, d, output_dir, dpi=dpi)
    if d == 2 and plot_cfg.get("plot_angles_if_d2", True):
        plot_angles_if_d2(sol_v, sol_theta, n, output_dir, dpi=dpi)
    if d == 2 and plot_cfg.get("plot_circle_if_d2", True):
        plot_circle_if_d2(sol_v, n, output_dir, dpi=dpi)
    if d == 3 and plot_cfg.get("plot_sphere_if_d3", True):
        plot_sphere_if_d3(sol_v, n, output_dir, dpi=dpi)
