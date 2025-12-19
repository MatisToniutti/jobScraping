from playwright.sync_api import sync_playwright
import time
import random


def run_scraper():
    #liste des mots qu'on ne veut pas dans une offre
    banned_words = ["confirmé","product owner","stage","internship","alternance","stagiaire","intern","alternant","interim","freelance","docteur","phd","senior","expert","consultant","annotator","data engineer"]
    #liste des mots qui permettent de considérer une offre
    needed_words = ["ia", "ai","data", "ml", "cv", "nlp", "llm", "agent"]

    # Le "with" garantit que le navigateur se ferme proprement même s'il y a une erreur (pas de processus fantomes)
    with sync_playwright() as p:
        # headless=False pour voir chromium en live et les actions de playwright
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()

        offers_link = "https://www.linkedin.com/jobs/search/?currentJobId=4343539070&f_TPR=r604800&geoId=105015875&keywords=ia&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true"
        page.goto(offers_link)

        next_page = True

        while next_page:
            #on attend qu'au moins une offre ait chargée
            page.wait_for_selector('[data-job-id]')
            
            # on récupère un "locator" qui pointe vers toutes les div ayant l'attribut data-job-id (les offres)
            offres_locator = page.locator('div[data-job-id]')

            # on récupère la barre de scroll permettant de scroller les offres sinon on ne peut pas toutes les récupérer
            conteneur_scroll = offres_locator.first.locator('xpath=./../../../..')
            scroll_element(conteneur_scroll,distance=3000)
            
            print(f"Nombre d'offres trouvées : {offres_locator.count()}")
            
            for offre in offres_locator.all():

                job_id = offre.get_attribute("data-job-id")
                
                title_locator = offre.locator("strong").first
                title = title_locator.inner_text().strip()

                is_banned = any(word in title.lower() for word in banned_words)
                is_needed = any(word in title.lower() for word in needed_words)

                if not is_banned and is_needed:
                    print(f"Acceptée : ID: {job_id} | Titre: {title}")
                    #offre.click()
                    #time.sleep(1)
                else:
                    print(f"Refusée : ID: {job_id} | Titre: {title}")

            next_button = page.locator('button[aria-label="View next page"]')
            
            if next_button.count()>0:
                next_button.click()
                # Attendre que la nouvelle page charge
                page.wait_for_load_state("networkidle")
            else:
                next_page=False

        browser.close()

#enregistre les informations de connexion/cookies pour ne plus avoir à se connecter
def save_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://www.linkedin.com/")

        #met en pause le code et nous laisse intéragir avec la page
        page.pause()

        #enregistre le contexte
        context.storage_state(path="state.json")

        browser.close()

def scroll(page, direction="down", sleep_min = 1, sleep_max = 2):
    for i in range(5):
        # distance de scroll aléatoire pour plus de réalisme
        distance = random.randint(600, 900)
        if(direction=="down"):
            page.mouse.wheel(0, distance)
        elif(direction=="up"):
            page.mouse.wheel(0, -distance)
        else:
            print("La direction définie est incorrecte, doit être 'up' ou 'down'.")
            break
        
        time.sleep(random.uniform(sleep_min, sleep_max))

def scroll_element(element, distance=1000):
    pixels_parcourus = 0
    while pixels_parcourus < distance:
        # On fait des sauts de 40 pixels (unité de coup de molette)
        step = 40
        # chaque accoup avec le doigt
        for i in range(random.randint(4,7)):
            element.evaluate(f"el => el.scrollTop += {step}")
            pixels_parcourus += step
            
            time.sleep(random.uniform(0.02, 0.06))
        time.sleep(random.uniform(0.1,0.3))

if __name__ == "__main__":
    run_scraper()