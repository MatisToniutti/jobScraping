from playwright.sync_api import sync_playwright
import time
import random

def run_scraper():
    # Le "with" garantit que le navigateur se ferme proprement même s'il y a une erreur (pas de processus fantomes)
    with sync_playwright() as p:
        # headless=False pour voir chromium en live et les actions de playwright
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()

        offers_link = "https://www.linkedin.com/jobs/search/?currentJobId=4343539070&f_TPR=r604800&geoId=105015875&keywords=ia&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true"
        page.goto(offers_link)

        #on attend qu'au moins une offre ait chargée
        page.wait_for_selector('[data-job-id]')
        
        # on récupère un "locator" qui pointe vers toutes les div ayant l'attribut data-job-id (les offres)
        offres_locator = page.locator('div[data-job-id]')

        # on récupère la barre de scroll permettant de scroller les offres sinon on ne peut pas toutes les récupérer
        conteneur_scroll = offres_locator.first.locator('xpath=./../../../..')

        for i in range(10):
            # descendre la div de 500 pixels
            conteneur_scroll.evaluate("el => el.scrollTop += 500")
            time.sleep(1)

        
        print(f"Nombre d'offres trouvées : {offres_locator.count()}")
        
        for index, offre in enumerate(offres_locator.all()):

            job_id = offre.get_attribute("data-job-id")
            
            print(f"Offre n°{index} [ID:{job_id}] ")


        page.pause()

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

if __name__ == "__main__":
    run_scraper()