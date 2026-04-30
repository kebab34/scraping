"""
Script 2b : Récupère la catégorie depuis la page de chaque boutique
            (uniquement les boutiques classées 'Autre' par les mots-clés)
Input  : data/intermediate/boutiques_raw.csv + data/intermediate/centers.csv
Output : data/intermediate/boutiques_categories.csv
"""

import time
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

BOUTIQUES_CSV = "data/intermediate/boutiques_raw.csv"
CENTERS_CSV = "data/intermediate/centers.csv"
OUTPUT_CSV = "data/intermediate/boutiques_categories.csv"
DELAY = 2

KLEPIERRE_CATEGORIES = {
    "culture": "Culture, Loisirs & Cadeaux",
    "cadeaux": "Culture, Loisirs & Cadeaux",
    "loisirs": "Culture, Loisirs & Cadeaux",
    "divertissement": "Divertissement",
    "maison": "Maison & Décoration",
    "décoration": "Maison & Décoration",
    "decoration": "Maison & Décoration",
    "mode": "Mode",
    "restaurant": "Restauration",
    "alimentaire": "Restauration",
    "santé": "Santé & Beauté",
    "sante": "Santé & Beauté",
    "beauté": "Santé & Beauté",
    "beaute": "Santé & Beauté",
    "services": "Services",
    "supermarché": "Supermarchés & Alimentaire",
    "supermarche": "Supermarchés & Alimentaire",
    "grands magasins": "Supermarchés & Alimentaire",
}


def classify_keywords(name):
    """Classification par mots-clés (déjà dans script 03)."""
    from scripts_03_keywords import CATEGORIES
    name_lower = name.lower()
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in name_lower:
                return cat
    return None


def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    return uc.Chrome(options=options, version_main=142)


def extract_category_from_page(driver, url):
    try:
        driver.get(url)
        time.sleep(DELAY)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        text = soup.get_text(separator="|", strip=True).lower()

        for kw, cat in KLEPIERRE_CATEGORIES.items():
            pattern = r'\|' + re.escape(kw) + r'\|'
            if re.search(pattern, text):
                return cat
        return "Autre"
    except Exception as e:
        return "Autre"


def main():
    boutiques = pd.read_csv(BOUTIQUES_CSV)
    centers = pd.read_csv(CENTERS_CSV)

    # Construire la map slug → website_url
    center_map = dict(zip(centers["slug"], centers["website_url"].fillna("")))

    # Classification mots-clés d'abord
    sys_path_fix = __import__("sys"); sys_path_fix.path.insert(0, ".")
    import importlib, types

    # Importer les CATEGORIES depuis script 03 sans l'exécuter
    spec = importlib.util.spec_from_file_location("s03", "scripts/03_clean_classify.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    boutiques["category_kw"] = boutiques["boutique_name"].apply(mod.classify)

    # Identifier les "Autre" qui ont une URL de boutique valide
    autre = boutiques[
        (boutiques["category_kw"] == "Autre") &
        (boutiques["boutique_path"].notna()) &
        (boutiques["boutique_path"] != "")
    ].copy()
    autre["website_url"] = autre["center_slug"].map(center_map)
    autre = autre[autre["website_url"] != ""]
    autre["full_url"] = autre["website_url"].str.rstrip("/") + autre["boutique_path"]

    print(f"Boutiques à catégoriser via page web : {len(autre)}")
    print(f"Boutiques déjà classifiées : {len(boutiques) - len(autre)}\n")

    driver = init_driver()
    results = {}

    try:
        for i, (idx, row) in enumerate(autre.iterrows()):
            print(f"[{i+1}/{len(autre)}] {row['boutique_name']} ...", end=" ", flush=True)
            cat = extract_category_from_page(driver, row["full_url"])
            results[idx] = cat
            print(cat)
    finally:
        driver.quit()

    boutiques["category_final"] = boutiques["category_kw"]
    for idx, cat in results.items():
        boutiques.at[idx, "category_final"] = cat

    os.makedirs("data/intermediate", exist_ok=True)
    boutiques.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\nSauvegardé : {OUTPUT_CSV}")
    print(boutiques["category_final"].value_counts().to_string())


if __name__ == "__main__":
    main()
