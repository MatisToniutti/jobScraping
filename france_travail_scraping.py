import requests
import os
from dotenv import load_dotenv
from sqlitedb import get_connection, insert_offer
from utils import clean_html

def get_access_token():
    client_ID = os.getenv("ID_client_FT")
    client_secret = os.getenv("Key_FT")
    url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
    scope = "o2dsoffre api_offresdemploiv2"

    payload = {
            "grant_type": "client_credentials",
            "client_id": client_ID,
            "client_secret": client_secret,
            "scope": scope
        }    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Erreur Token - Status: {response.status_code}")
        print(f"Détail: {response.text}")
        return None

def run_scraper():
    conn = get_connection()
    #liste des mots qu'on ne veut pas dans une offre
    banned_words = ["confirmé","product owner","stage","internship","alternance","stagiaire","intern","alternant","interim","freelance","docteur","phd","senior","expert","consultant","annotator","annotation", "expérimenté", "data engineer"]
    #liste des mots qui permettent de considérer une offre
    needed_words = [" ia", "ia ", " ai", "ai ","data", "ml", "cv", "nlp", "llm", "agent"]

    keywords = ["ia", "data"]
    load_dotenv()
    token = get_access_token()

    url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        
    }
    
    params = {
        "motsCles": "IA",
        "publieeDepuis": 1,
        "range": "0-149",
        "typeContrat": "CDI"
    }
    
    for keyword in keywords:
        range =  0
        offresVues = 0
        params["motsCles"] = keyword

        while range==offresVues:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 204: #pas d'offres
                break
            range += 150
            offresVues += len(response.json()["resultats"])
            for offer in response.json()["resultats"]:
                is_banned = any(word in offer["intitule"].lower() for word in banned_words)
                is_needed = any(word in offer["intitule"].lower() for word in needed_words)
                if not is_banned and is_needed:
                    #si entreprise n'existe pas on a un dictionnaire vide et non une erreur
                    entreprise = offer.get("entreprise", {})
                    nom_entreprise = entreprise.get("nom", "")
                    insert_offer(conn,
                                        job_id="ft-"+offer["id"],
                                        website="france_travail",
                                        company=nom_entreprise,
                                        description=offer["description"],
                                        city= "",
                                        state="",
                                        country="",
                                        name=offer["intitule"],
                                        link="https://candidat.francetravail.fr/offres/recherche/detail/"+offer["id"])    
    

if __name__ == "__main__":
    run_scraper()