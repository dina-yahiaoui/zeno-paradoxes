# src/dichotomie/dichotomie.py
def simulate_pierre_vers_arbre(distance_totale=8.0, epsilon=1e-4, max_steps=10_000):
    """
    Simule le lancer d'une pierre vers un arbre à distance 'distance_totale' (en mètres)
    en appliquant la règle de Zénon : à chaque étape, on parcourt la moitié de la
    distance restante. Affiche, à chaque étape, la position de la pierre PAR RAPPORT
    À L'ARBRE (i.e., la distance restante à l'arbre).
    """
    reste = float(distance_totale)   # distance pierre -> arbre
    parcouru = 0.0                   # distance depuis le point de départ
    etape = 0

    print("=== Simulation : Paradoxe de la Dichotomie (pierre -> arbre) ===")
    print(f"Distance initiale pierre-arbre : {distance_totale:.4f} m\n")
    print("Étape |  +Δ (m)   |  parcouru (m)  |  reste à l'arbre (m)")
    print("----- | ---------- | -------------- | ---------------------")

    while reste > epsilon and etape < max_steps:
        etape += 1
        delta = reste / 2.0      # on fait la moitié du reste
        parcouru += delta
        reste -= delta           # ou: reste = distance_totale - parcouru

        print(f"{etape:5d} | {delta:10.6f} | {parcouru:14.6f} | {reste:21.6f}")

    print("\n--- Résultats ---")
    print(f"Étapes effectuées : {etape}")
    print(f"Position finale (depuis départ) ~ {parcouru:.6f} m")
    print(f"Distance restante à l'arbre     ~ {reste:.6f} m (<= epsilon={epsilon})")
    print("Conclusion : même si le nombre d'étapes est potentiellement infini,")
    print("la somme des distances converge et la pierre atteint l'arbre (limite).")


# Exécution directe depuis le terminal
if __name__ == "__main__":
    simulate_pierre_vers_arbre(distance_totale=8.0, epsilon=1e-4)
