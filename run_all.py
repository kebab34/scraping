"""
Pipeline complet : collecte des boutiques des centres commerciaux Klépierre
Exécute les 4 scripts dans l'ordre avec gestion des erreurs
"""

import subprocess
import sys

SCRIPTS = [
    ("01_get_centers.py",      "Collecte la liste des centres commerciaux"),
    ("02_get_boutiques.py",    "Scrape les boutiques de chaque centre"),
    ("02b_get_categories.py",  "Récupère les catégories des boutiques"),
    ("03_clean_classify.py",   "Nettoyage et génération du CSV final"),
]

def run_script(filename, description):
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"  → scripts/{filename}")
    print(f"{'='*60}")

    result = subprocess.run(
        [sys.executable, f"scripts/{filename}"],
        capture_output=False
    )

    if result.returncode != 0:
        print(f"\n[ERREUR] Le script {filename} a échoué (code {result.returncode})")
        print("Vérifiez les logs ci-dessus et relancez manuellement.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    print("PIPELINE SCRAPING CENTRES COMMERCIAUX KLÉPIERRE")
    print(f"{'='*60}")

    for filename, description in SCRIPTS:
        run_script(filename, description)

    print(f"\n{'='*60}")
    print("  Pipeline terminé avec succès !")
    print("  Résultats disponibles dans : data/final/boutiques_final.csv")
    print(f"{'='*60}\n")
