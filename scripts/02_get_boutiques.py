"""
Script 2 : Pour chaque centre, scrape la liste des boutiques
Input  : data/intermediate/centers.csv
Output : data/intermediate/boutiques_raw.csv + sources HTML dans sources/boutiques/
"""

import time
import os
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

CENTERS_CSV = "data/intermediate/centers.csv"
OUTPUT_CSV = "data/intermediate/boutiques_raw.csv"
SOURCES_DIR = "sources/boutiques"
DELAY = 4


def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    return uc.Chrome(options=options, version_main=142)


def save_source(slug, html):
    os.makedirs(SOURCES_DIR, exist_ok=True)
    path = os.path.join(SOURCES_DIR, f"{slug}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def parse_boutiques(html, center_name, center_slug, country):
    soup = BeautifulSoup(html, "html.parser")
    tiles = soup.find_all("div", class_=lambda c: c and "shop-tile" in c and "basic-tile" in c)

    boutiques = []
    for tile in tiles:
        name_tag = tile.find("h2", class_=lambda c: c and "basic-tile_title" in c)
        name = name_tag.get_text(strip=True) if name_tag else ""
        if not name:
            continue

        link_tag = tile.find("a", href=True)
        href = link_tag.get("href", "") if link_tag else ""

        status_tag = tile.find("div", class_=lambda c: c and "ShopDetails_status" in c)
        status = ""
        if status_tag:
            span = status_tag.find("span")
            status = span.get_text(strip=True) if span else ""

        has_deals = bool(tile.find("div", class_=lambda c: c and "deals-tag" in c))

        boutiques.append({
            "center_name": center_name,
            "center_slug": center_slug,
            "country": country,
            "boutique_name": name,
            "status": status,
            "has_deals": has_deals,
            "boutique_path": href,
        })

    return boutiques


def scrape_center(driver, row):
    url = row["boutiques_url"]
    slug = row["slug"]

    try:
        driver.get(url)
        time.sleep(DELAY)

        html = driver.page_source
        soup_check = BeautifulSoup(html, "html.parser")
        title = soup_check.find("title")
        title_text = title.text.strip() if title else ""

        # Détecter si la page est une erreur ou Cloudflare
        if "cloudflare" in title_text.lower() or "404" in title_text or "not found" in title_text.lower():
            return [], f"Page non accessible : {title_text}"

        save_source(slug, html)
        boutiques = parse_boutiques(html, row["name"], slug, row["country"])
        return boutiques, None

    except Exception as e:
        return [], str(e)


def main():
    if not os.path.exists(CENTERS_CSV):
        print(f"[ERREUR] Fichier introuvable : {CENTERS_CSV}")
        return

    centers = pd.read_csv(CENTERS_CSV)
    # Garder uniquement les centres avec une URL boutiques
    centers = centers[centers["boutiques_url"].notna() & (centers["boutiques_url"] != "")]
    print(f"{len(centers)} centres à scraper\n")

    driver = init_driver()
    all_boutiques = []
    errors = []

    for i, row in centers.iterrows():
        print(f"[{i+1}/{len(centers)+1}] {row['name']} ({row['country']}) ...", end=" ", flush=True)

        boutiques, error = scrape_center(driver, row)

        if error:
            print(f"ERREUR : {error}")
            errors.append({"center": row["name"], "url": row["boutiques_url"], "error": error})
        else:
            print(f"{len(boutiques)} boutiques")
            all_boutiques.extend(boutiques)

        time.sleep(DELAY)

    driver.quit()

    os.makedirs("data/intermediate", exist_ok=True)
    df = pd.DataFrame(all_boutiques)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\nTotal : {len(all_boutiques)} boutiques → {OUTPUT_CSV}")

    if errors:
        errors_path = "data/intermediate/errors_script2.csv"
        pd.DataFrame(errors).to_csv(errors_path, index=False)
        print(f"{len(errors)} erreurs → {errors_path}")

    if not df.empty:
        print("\nAperçu :")
        print(df.groupby(["center_name", "country"]).size().reset_index(name="nb_boutiques").to_string())


if __name__ == "__main__":
    main()
