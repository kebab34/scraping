"""
Script 3 : Nettoyage et classification des boutiques
Input  : data/intermediate/boutiques_raw.csv
Output : data/final/boutiques_final.csv
"""

import os
import pandas as pd

INPUT_CSV = "data/intermediate/boutiques_categories.csv"
OUTPUT_CSV = "data/final/boutiques_final.csv"

# Classification par mots-clés dans le nom de l'enseigne
CATEGORIES = {
    "Mode": [
        "h&m", "zara", "pull", "mango", "celio", "bershka", "etam", "caroll",
        "armand thiery", "promod", "kiabi", "jules", "gap", "uniqlo", "lacoste",
        "tommy", "nike", "adidas", "foot locker", "courir", "footkorner",
        "new balance", "puma", "reebok", "devred", "cyrillus", "jacadi",
        "tape", "cache cache", "kaporal", "sinequanone", "morgan", "jennyfer",
        "pimkie", "burton", "chaussea", "deichmann", "geox", "bocage",
        "andre", "eram", "naf naf", "kookai", "sandro", "maje", "ba&sh",
        "calzedonia", "intimissimi", "undiz", "dim", "orchestr", "sergent",
        "dpam", "catimini", "bonpoint", "bonton", "okaidi", "kiplay",
        "petit bateaux", "izac", "paul & joe", "esprit", "levi", "wrangler",
        "bonton", "cotton", "chic", "mode", "fashion", "cloth", "wear",
        "sport", "running", "fitness", "gym", "tennis", "ski",
        "darjeeling", "aubade", "lise charmel", "triumph", "hunkemoller",
        "c&a", "primark", "la halle", "grain de malice", "maison 123",
        "antonelle", "bleu cerise", "balabooste", "genevieve lethu",
    ],
    "Restauration": [
        "burger king", "mcdonald", "kfc", "subway", "pizza", "sushi",
        "brioche doree", "paul", "eric kayser", "starbucks", "costa",
        "hippopotamus", "flunch", "casino cafe", "courtepaille",
        "five guys", "big fernand", "leon", "popeyes", "quick",
        "bagelstein", "pitaya", "creperie", "crepe", "wok", "noodle",
        "thai", "indien", "japonais", "chinois", "libanais", "grec",
        "amorino", "haagen", "glace", "patisserie", "chocolat", "maison",
        "cafe", "coffee", "tea", "salon de the", "boulangerie", "bakery",
        "restaurant", "brasserie", "bistro", "grill", "food", "kitchen",
        "brendy", "baboo", "babeco", "black and white burger", "chik",
        "everwood", "exo soleil",
    ],
    "Santé & Beauté": [
        "pharmacie", "parapharmacie", "optique", "alain afflelou",
        "atol", "grand optical", "generale d optique", "krys", "lynx",
        "vision", "coiffeur", "franck provost", "jean louis david",
        "dessange", "fabio salsa", "olivier sassoon", "tchip",
        "bleu libellule", "beauty", "beaute", "parfumerie", "sephora",
        "marionnaud", "nocibe", "yves rocher", "l occitane", "lush",
        "body shop", "aroma", "adopt", "kiko", "nyx", "mac ", "clinique",
        "body minute", "manucure", "institut", "spa", "soleil", "uv",
        "centre auditif", "audika", "amplifon", "biotech", "nutri",
        "diet", "herboristerie",
    ],
    "Maison & Décoration": [
        "maisons du monde", "home", "ikea", "but", "conforama",
        "la redoute", "becquet", "deco", "decoration", "mobilier",
        "canape", "cuisine", "salle de bain", "linge de maison",
        "habitat", "jardin", "fleurs", "plantes", "bougie", "parfum maison",
        "du bruit dans la cuisine", "draeger", "saint maclou", "point p",
        "leroy merlin", "castorama", "bricolage", "outillage",
    ],
    "Culture, Loisirs & Cadeaux": [
        "fnac", "darty", "boulanger", "micromania", "game", "cultura",
        "gibert", "librairie", "livre", "presse", "relay", "maison de la presse",
        "jouet", "king jouet", "toys", "lego", "games", "escape",
        "cinema", "cine", "bowling", "laser", "karting", "patinoire",
        "musee", "galerie", "photo", "kodak", "minit", "bijou",
        "agatha", "histoire d or", "cleor", "or", "bijouterie",
        "horlogerie", "montre", "swarovski", "pandora", "thalie",
        "cadeaux", "souvenirs", "virginies", "claire s", "claire's",
    ],
    "Services": [
        "banque", "bnp", "credit", "societe generale", "lcl", "bred",
        "cic", "caisse d epargne", "la banque postale", "boursorama",
        "assurance", "agence", "voyage", "fram", "thomas cook", "havas",
        "nouvelles frontieres", "carrefour voyages",
        "pressing", "5 a sec", "nettoyage", "cordonnerie", "clef",
        "retouche", "couture", "clic", "photographie",
        "free", "sfr", "orange", "bouygues", "sosh", "virgin mobile",
        "telephone", "mobile", "numericable",
        "la poste", "dpd", "fedex", "ups", "chronopost",
        "parking", "auto", "moto", "velo",
        "gym", "fitness", "sport club", "elite club", "fitness park",
        "coworking", "bureau", "formation",
    ],
    "Supermarchés & Alimentaire": [
        "carrefour", "auchan", "leclerc", "intermarche", "super u",
        "monoprix", "casino", "franprix", "picard", "biocoop",
        "naturalia", "bio", "organic", "primeur", "boucherie",
        "poissonnier", "fromagerie", "epicerie", "cave", "vin",
        "nicolas", "lavinia", "beer", "biere",
        "marche", "halle", "alimentaire", "alimentation",
    ],
}


def classify(name):
    name_lower = name.lower()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in name_lower:
                return category
    return "Autre"


def main():
    if not os.path.exists(INPUT_CSV):
        print(f"[ERREUR] Fichier introuvable : {INPUT_CSV}")
        return

    df = pd.read_csv(INPUT_CSV)
    print(f"{len(df)} boutiques chargées")

    # Nettoyage
    df["boutique_name"] = df["boutique_name"].str.strip()
    df = df.drop_duplicates(subset=["center_slug", "boutique_name"])
    df = df[df["boutique_name"].str.len() > 0]
    print(f"{len(df)} boutiques après dédoublonnage")

    # Classification : utiliser category_final si disponible, sinon mots-clés
    # "Services" depuis 02b est peu fiable (faux positifs via menu nav) → on re-classifie
    if "category_final" in df.columns:
        df["category"] = df.apply(
            lambda r: classify(r["boutique_name"]) if r["category_final"] == "Services"
            else r["category_final"],
            axis=1
        )
    else:
        df["category"] = df["boutique_name"].apply(classify)

    # Statut normalisé
    df["is_open"] = df["status"].str.lower().str.contains("ouvert|open|aperto|abierto|open", na=False)

    # Colonne date (non disponible sur la source — à enrichir manuellement)
    df["date_ouverture"] = ""
    df["date_fermeture"] = ""

    # Sélection et ordre des colonnes finales
    cols = ["center_name", "center_slug", "country",
            "boutique_name", "category", "is_open", "has_deals",
            "date_ouverture", "date_fermeture", "boutique_path"]
    df_final = df[[c for c in cols if c in df.columns]]

    os.makedirs("data/final", exist_ok=True)
    df_final.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\nSauvegardé : {OUTPUT_CSV}")

    print("\n=== Répartition par catégorie ===")
    print(df_final["category"].value_counts().to_string())

    print("\n=== Boutiques par centre ===")
    print(df_final.groupby(["center_name", "country"]).size().reset_index(name="nb_boutiques").to_string())


if __name__ == "__main__":
    main()
