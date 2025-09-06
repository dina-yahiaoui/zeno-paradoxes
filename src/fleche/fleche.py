# src/fleche/fleche.py
def run_fleche(distance=10.0, speed=2.0, dt=1.0):
    print("=== Paradoxe de la Flèche ===")
    print(f"Distance = {distance} m | Vitesse = {speed} m/s\n")

    t = 0.0
    pos = 0.0

    while pos < distance:
        print(f"t={t:.1f}s | position = {pos:.2f} m")
        t += dt
        pos += speed * dt

    print(f"\nLa flèche atteint {distance} m en {t:.1f} s.")
    print("Explication : à chaque instant la flèche a une position fixe,")
    print("mais la suite de ces positions montre bien un mouvement réel.")
    

if __name__ == "__main__":
    run_fleche()
