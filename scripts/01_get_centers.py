"""
Script 1 : Récupère la liste des centres commerciaux Klépierre (européens)
Output : data/intermediate/centers.csv + sources HTML dans sources/
"""

import time
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

BASE_URL = "https://www.klepierre.com"
LISTING_URL = f"{BASE_URL}/nos-centres-leaders-678f6e8467070"
SOURCES_DIR = "sources"
OUTPUT_CSV = "data/intermediate/centers.csv"
DELAY = 3


def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    return uc.Chrome(options=options, version_main=142)


def save_source(filename, html):
    os.makedirs(SOURCES_DIR, exist_ok=True)
    path = os.path.join(SOURCES_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [source] {path}")


def get_center_links(driver):
    print(f"Chargement listing : {LISTING_URL}")
    driver.get(LISTING_URL)
    time.sleep(4)
    html = driver.page_source
    save_source("klepierre_listing.html", html)

    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=lambda h: h and "/nos-centres-leaders-" in h and h != LISTING_URL.replace(BASE_URL, ""))

    seen = set()
    centers = []
    for l in links:
        href = l.get("href", "")
        full_url = href if href.startswith("http") else BASE_URL + href
        slug = full_url.split("/")[-1]
        # Exclure la page listing elle-même et les liens sans slug valide
        if full_url not in seen and slug and slug != "nos-centres-leaders-678f6e8467070":
            seen.add(full_url)
            name = slug.replace("-", " ").title()
            centers.append({"name": name, "slug": slug, "klepierre_url": full_url})
    return centers


def get_center_details(driver, center):
    url = center["klepierre_url"]
    print(f"  Détails : {center['name']} ...", end=" ", flush=True)
    driver.get(url)
    time.sleep(DELAY)

    html = driver.page_source
    save_source(f"center_{center['slug']}.html", html)

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="|", strip=True)

    # Récupérer le vrai nom depuis le titre de la page
    title_tag = soup.find("title")
    if title_tag:
        raw_title = title_tag.text.strip()
        real_name = raw_title.replace("Klépierre", "").replace("–", "").strip()
        if real_name:
            center["name"] = real_name

    # Extraire pays
    country_match = re.search(r'\|\s*(France|Italie|Espagne|Suède|Danemark|Norvège|Pays-Bas|République tchèque|Tchéquie|Belgique|Pologne|Allemagne|Portugal|Italy|Spain|Sweden|Denmark|Norway|Netherlands|Czech|Belgium)\s*\|', text, re.IGNORECASE)
    country = country_match.group(1).strip() if country_match else ""

    # Extraire URL du site officiel du centre
    website_link = soup.find("a", href=lambda h: h and "klepierre.fr" in h and "boutiques" not in h)
    website_url = website_link.get("href", "") if website_link else ""

    # Construire URL boutiques depuis le site officiel du centre
    boutiques_url = website_url.rstrip("/") + "/boutiques-restaurants" if website_url else ""

    # Extraire stats clés
    nb_enseignes = re.search(r'(\d+)\s*\|?\s*enseignes', text)
    nb_visitors = re.search(r'([\d,.]+)\s*\|?\s*millions de visiteurs', text)

    print(f"{country} | {website_url}")
    return {
        **center,
        "country": country,
        "website_url": website_url,
        "boutiques_url": boutiques_url,
        "nb_enseignes": nb_enseignes.group(1) if nb_enseignes else "",
        "nb_visitors_M": nb_visitors.group(1) if nb_visitors else "",
    }


def main():
    driver = init_driver()
    try:
        center_links = get_center_links(driver)
        print(f"\n{len(center_links)} centres trouvés\n")

        centers = []
        for c in center_links:
            details = get_center_details(driver, c)
            centers.append(details)
            time.sleep(DELAY)

        df = pd.DataFrame(centers)
        os.makedirs("data/intermediate", exist_ok=True)
        df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
        print(f"\nSauvegardé : {OUTPUT_CSV}")
        print(df[["name", "country", "boutiques_url"]].to_string())

    except Exception as e:
        print(f"\n[ERREUR] {e}")
        raise
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
