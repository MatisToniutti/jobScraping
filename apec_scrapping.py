import requests
import json
from sqlitedb import get_connection, insert_offer
from bs4 import BeautifulSoup

def run_scraper():
    conn = get_connection()
    #liste des mots qu'on ne veut pas dans une offre
    banned_words = ["confirmé","product owner","stage","internship","alternance","stagiaire","intern","alternant","interim","freelance","docteur","phd","senior","expert","consultant","annotator","data engineer"]
    #liste des mots qui permettent de considérer une offre
    needed_words = ["ia", "ai","data", "ml", "cv", "nlp", "llm", "agent"]

    keywords = ["ia", "data scientist"]
    offers_url = "https://www.apec.fr/cms/webservices/rechercheOffre"
    offer_url = "https://www.apec.fr/cms/webservices/offre/public?numeroOffre="
    payload = {
        "lieux": [],
        "fonctions": [],
        "statutPoste": [],
        "typesContrat": [
            "101888"
        ],
        "typesConvention": [
            "143684",
            "143685",
            "143686",
            "143687",
            "143706"
        ],
        "niveauxExperience": [
            "101881"
        ],
        "idsEtablissement": [],
        "secteursActivite": [],
        "typesTeletravail": [],
        "idNomZonesDeplacement": [],
        "positionNumbersExcluded": [],
        "typeClient": "CADRE",
        "sorts": [
            {
            "type": "SCORE",
            "direction": "DESCENDING"
            }
        ],
        "pagination": {
            "range": 20,
            "startIndex": 0
        },
        "activeFiltre": True,
        "pointGeolocDeReference": {
            "distance": 0
        },
        "motsCles": "ia"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Content-Type":"application/json"
    }
    for keyword in keywords:
        payload["motsCles"] = keyword
        current_count = 0
        nb_offers = 20
        while (nb_offers > current_count):
            response = requests.post(offers_url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                for offer in data["resultats"]:
                    is_banned = any(word in offer["intitule"].lower() for word in banned_words)
                    is_needed = any(word in offer["intitule"].lower() for word in needed_words)
                    if not is_banned and is_needed:
                        response_offer = requests.get(offer_url+offer["numeroOffre"], headers=headers)
                        offer_details = response_offer.json()
                        description = offer_details["texteHtml"]+offer_details["texteHtmlProfil"]+offer_details["texteHtmlEntreprise"]
                        description = clean_html(description)
                        link = "https://www.apec.fr/candidat/recherche-emploi.html/emploi/detail-offre/" + offer_details["numeroOffre"]
                        insert_offer(conn,
                                        job_id="apec-"+offer_details["numeroOffre"],
                                        website="apec",
                                        company=offer_details["nomCompteEtablissement"],
                                        description=description,
                                        city= "",
                                        state="",
                                        country="",
                                        name=offer_details["intitule"],
                                        link=link)
            else:
                print(f"Erreur : {response.status_code}")

            nb_offers = data["totalCount"]
            payload["pagination"]["startIndex"] += 20
            current_count+=20


def clean_html(raw_html):
    # On "parse" le HTML
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # On récupère uniquement le texte
    # separator=" " permet d'éviter que deux mots collés par des balises se rejoignent (ex: </b>Bonjour)
    text = soup.get_text(separator=" ")
    
    # On nettoie les espaces en trop
    clean_text = " ".join(text.split())
    
    return clean_text

if __name__ == "__main__":
    run_scraper()