import requests
import os
from dotenv import load_dotenv

def get_access_token(client_ID, client_secret):
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
        print(f"❌ Erreur Token - Status: {response.status_code}")
        print(f"Détail: {response.text}")
        return None

def fetch_france_travail_jobs(token):
    url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        # 👇 AJOUT CRUCIAL : La pagination est souvent obligatoire ou recommandée
        # Cela demande les 50 premiers résultats (l'API limite souvent à 150 max par appel)
        "range": "0-49" 
    }
    
    params = {
        "motsCles": "IA", # "IA" en majuscules est parfois mieux interprété, mais "ia" marche aussi
        # Optionnel : ajouter un filtre de date pour ne pas avoir de vieux trucs
        # "minCreationDate": "2024-01-01T00:00:00Z" 
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200: # OK
        return response.json().get("resultats", [])
    elif response.status_code == 206: # Partial Content (C'est normal avec le Range, ça veut dire "Succès")
        return response.json().get("resultats", [])
    elif response.status_code == 204: # Pas d'offres
        print("ℹ️ Aucune offre trouvée pour ces critères.")
        return []
    else:
        print(f"❌ Erreur API : {response.status_code}")
        # On essaie d'afficher le message d'erreur JSON propre s'il existe
        try:
            error_detail = response.json()
            print(f"Message API : {error_detail}")
        except:
            print(f"Raw Response : {response.text}")
        return []

if __name__ == "__main__":
    load_dotenv()
    CLIENT_ID = os.getenv("ID_client_FT")
    CLIENT_SECRET = os.getenv("Key_FT")

    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERREUR : Les clés ne sont pas chargées depuis le .env")
    else:
        token = get_access_token(client_ID=CLIENT_ID, client_secret=CLIENT_SECRET)
        
        if token:
            print(f"✅ Token généré (début) : {token}")
            jobs = fetch_france_travail_jobs(token=token)
            print(f"Nombre d'offres trouvées : {len(jobs)}")
            # Afficher juste le titre de la première offre pour vérifier
            if jobs:
                print(f"Exemple : {jobs[0].get('intitule')}")