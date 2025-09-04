# src/achille/achille_tortue.py

def simulate(v_achille=5.0, v_tortue=2.0, lead=20.0, dt=0.1, t_max=60.0):
    """
    Simule le paradoxe d'Achille et la tortue.
    Retourne une liste de tuples (t, xA, xT) + info rattrapage.
    """
    t = 0.0
    x_a = 0.0
    x_t = lead
    data = []

    while t <= t_max:
        data.append((t, x_a, x_t))
        if x_a >= x_t:
            return data, (True, t, x_a)
        x_a += v_achille * dt
        x_t += v_tortue * dt
        t   += dt

    return data, (False, t_max, x_a)

# exécution directe = version terminal
if __name__ == "__main__":
    results, (caught, t_hit, x_hit) = simulate()
    print("t (s) | Achille (m) | Tortue (m)")
    print("-" * 30)
    for t, xa, xt in results:
        print(f"{t:5.1f} | {xa:11.2f} | {xt:9.2f}")
    if caught:
        print(f"\n✅ Achille rattrape la tortue à t ≈ {t_hit:.2f}s, x ≈ {x_hit:.2f}m.")
    else:
        print("\n❌ Achille n'a pas rattrapé la tortue dans le temps imparti.")
