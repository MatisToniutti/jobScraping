from bs4 import BeautifulSoup
import sqlite3
from utils.sqlitedb import get_connection
def clean_html(raw_html):
    # On "parse" le HTML
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # On récupère uniquement le texte
    # separator=" " permet d'éviter que deux mots collés par des balises se rejoignent (ex: </b>Bonjour)
    text = soup.get_text(separator=" ")
    
    # On nettoie les espaces en trop
    clean_text = " ".join(text.split())
    
    return clean_text

def export_links():
    conn = get_connection()
    cursor = conn.cursor()

    # On récupère les liens des offres intéressantes (value = 1)
    cursor.execute("""
        SELECT link 
        FROM offers 
        WHERE interest = 1 
        AND date_added >= date('now', '-2 hours')
    """)
    links = cursor.fetchall()

    # Écriture dans le fichier
    with open('liens.txt', 'w', encoding='utf-8') as f:
        for link in links:
            if link[0]: # Vérifie que le lien n'est pas vide
                f.write(f"{link[0]}\n")

    conn.close()
    print(f"Export terminé : {len(links)} liens extraits dans liens.txt")

if __name__ == "__main__":
    export_links()