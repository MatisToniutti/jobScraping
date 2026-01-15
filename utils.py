from bs4 import BeautifulSoup

def clean_html(raw_html):
    # On "parse" le HTML
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # On récupère uniquement le texte
    # separator=" " permet d'éviter que deux mots collés par des balises se rejoignent (ex: </b>Bonjour)
    text = soup.get_text(separator=" ")
    
    # On nettoie les espaces en trop
    clean_text = " ".join(text.split())
    
    return clean_text