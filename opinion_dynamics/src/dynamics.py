"""Dynamics for Zhang et al.-style generalized Kuramoto opinion model.

The main vector model is
    vdot_i = (I - v_i v_i^T) sum_j A_ij U_{k-1}(v_i^T v_j) v_j
where v_i is in R^d and has unit norm.

When d=2 and v_i = [cos(theta_i), sin(theta_i)], this reduces to
    theta_dot_i = sum_j A_ij sin(k(theta_j - theta_i)).
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp


def chebyshev_U(n: int, x: float | np.ndarray) -> float | np.ndarray:
    """Chebyshev polynomial of the second kind U_n(x).

    Uses the recurrence:
        U_0(x) = 1
        U_1(x) = 2x
        U_n(x) = 2x U_{n-1}(x) - U_{n-2}(x)

    This works for any nonnegative integer n.
    """
    if n < 0:
        raise ValueError("n must be nonnegative")
    if n == 0:
        return np.ones_like(x) if isinstance(x, np.ndarray) else 1.0
    if n == 1:
        return 2 * x

    u_prev2 = np.ones_like(x) if isinstance(x, np.ndarray) else 1.0
    u_prev1 = 2 * x
    for _ in range(2, n + 1):
        u_curr = 2 * x * u_prev1 - u_prev2
        u_prev2, u_prev1 = u_prev1, u_curr
    return u_curr


def normalize_rows(X: np.ndarray) -> np.ndarray:
    """Normalize each row of X to unit Euclidean norm."""
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("Cannot normalize a zero vector")
    return X / norms


def theta_to_v(theta: np.ndarray) -> np.ndarray:
    """Convert d=2 angles to flattened vector states."""
    V = np.column_stack([np.cos(theta), np.sin(theta)])
    return V.reshape(-1)


def v_to_theta(v: np.ndarray) -> np.ndarray:
    """Recover d=2 angles from flattened vector states."""
    V = v.reshape((-1, 2))
    return np.arctan2(V[:, 1], V[:, 0])


def wrap_angle(angle: np.ndarray) -> np.ndarray:
    """Wrap angles to [-pi, pi)."""
    return (angle + np.pi) % (2 * np.pi) - np.pi


def initial_conditions(
    n: int,
    d: int,
    init_cfg: dict,
    rng: np.random.Generator,
) -> np.ndarray:
    """Create flattened initial vector state of shape (n*d,)."""
    init_type = init_cfg.get("type", "random")
    noise = float(init_cfg.get("noise", 0.05))

    if d == 2 and init_type == "random_angles":
        theta0 = rng.uniform(-np.pi, np.pi, size=n)
        return theta_to_v(theta0)

    if d == 2 and init_type == "two_cluster":
        theta0 = np.zeros(n)
        theta0[: n // 2] = 0.0
        theta0[n // 2 :] = np.pi
        theta0 += noise * rng.standard_normal(n)
        theta0 = wrap_angle(theta0)
        return theta_to_v(theta0)

    if d == 2 and init_type == "k_cluster":
        k = int(init_cfg.get("k", 3))
        theta0 = np.array([(2 * np.pi / k) * (i % k) for i in range(n)])
        theta0 += noise * rng.standard_normal(n)
        theta0 = wrap_angle(theta0)
        return theta_to_v(theta0)

    if init_type in {"random", "random_sphere"}:
        X = rng.standard_normal((n, d))
        return normalize_rows(X).reshape(-1)

    if init_type == "from_file":
        filename = init_cfg["filename"]
        X = np.loadtxt(filename, delimiter=",")
        if X.shape != (n, d):
            raise ValueError(f"Expected initial condition shape {(n, d)}, got {X.shape}")
        return normalize_rows(X).reshape(-1)

    raise ValueError(f"Unknown initial condition type: {init_type}")


def rhs_vector_model(t: float, v: np.ndarray, A: np.ndarray, d: int, k: int) -> np.ndarray:
    """Right-hand side for the generalized vector model on S^{d-1}."""
    n = A.shape[0]
    V = v.reshape((n, d))
    dV = np.zeros_like(V)
    I = np.eye(d)

    for i in range(n):
        vi = V[i]
        neighbor_sum = np.zeros(d)

        for j in range(n):
            if A[i, j] != 0:
                vj = V[j]
                x_ij = float(np.dot(vi, vj))
                # Clip for numerical safety; theoretically x_ij in [-1,1].
                x_ij = np.clip(x_ij, -1.0, 1.0)
                weight = chebyshev_U(k - 1, x_ij)
                neighbor_sum += A[i, j] * weight * vj

        projection = I - np.outer(vi, vi)
        dV[i] = projection @ neighbor_sum

    return dV.reshape(-1)


def rhs_angle_model(t: float, theta: np.ndarray, A: np.ndarray, k: int) -> np.ndarray:
    """d=2 scalar angle model: theta_dot_i = sum_j A_ij sin(k(theta_j-theta_i))."""
    n = A.shape[0]
    dtheta = np.zeros_like(theta)
    for i in range(n):
        for j in range(n):
            if A[i, j] != 0:
                dtheta[i] += A[i, j] * np.sin(k * (theta[j] - theta[i]))
    return dtheta


def solve_vector_model(A: np.ndarray, settings: dict, v0: np.ndarray):
    """Solve the generalized vector model."""
    d = int(settings["d"])
    k = int(settings["k"])
    t_eval = np.linspace(
        float(settings["t_start"]),
        float(settings["t_end"]),
        int(settings["num_time_points"]),
    )
    return solve_ivp(
        fun=lambda t, y: rhs_vector_model(t, y, A, d=d, k=k),
        t_span=(float(settings["t_start"]), float(settings["t_end"])),
        y0=v0,
        t_eval=t_eval,
        rtol=float(settings.get("rtol", 1e-9)),
        atol=float(settings.get("atol", 1e-9)),
    )


def solve_angle_model_if_d2(A: np.ndarray, settings: dict, v0: np.ndarray):
    """Solve scalar angle model only when d=2."""
    if int(settings["d"]) != 2:
        return None
    theta0 = v_to_theta(v0)
    k = int(settings["k"])
    t_eval = np.linspace(
        float(settings["t_start"]),
        float(settings["t_end"]),
        int(settings["num_time_points"]),
    )
    return solve_ivp(
        fun=lambda t, y: rhs_angle_model(t, y, A, k=k),
        t_span=(float(settings["t_start"]), float(settings["t_end"])),
        y0=theta0,
        t_eval=t_eval,
        rtol=float(settings.get("rtol", 1e-9)),
        atol=float(settings.get("atol", 1e-9)),
    )
