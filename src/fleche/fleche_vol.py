def simulate(v=5.0, t_max=5.0, dt=0.5):
    """
    Simule le paradoxe de la flèche en vol.
    Retourne une liste de tuples (t, x).
    """
    t = 0.0
    x = 0.0
    data = []

    while t <= t_max:
        data.append((t, x))
        x += v * dt
        t += dt

    return data


if __name__ == "__main__":
    results = simulate()
    print("t (s) | Flèche (m)")
    print("-" * 20)
    for t, x in results:
        print(f"{t:5.1f} | {x:9.2f}")
    print(f"\n✅ La flèche a parcouru {results[-1][1]:.2f} m en {results[-1][0]:.2f}s.")