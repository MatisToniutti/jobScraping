from playwright.sync_api import sync_playwright
from sqlitedb import get_connection, create_offers_table, insert_offer
import time
import random


def run_scraper():
    #liste des mots qu'on ne veut pas dans une offre
    banned_words = ["confirmé","product owner","stage","internship","alternance","stagiaire","intern","alternant","interim","freelance","docteur","phd","senior","expert","consultant","annotator","data engineer"]
    #liste des mots qui permettent de considérer une offre
    needed_words = ["ia", "ai","data", "ml", "cv", "nlp", "llm", "agent"]

    offers_links = [
             "https://www.linkedin.com/jobs/search/?currentJobId=4343539070&f_TPR=r604800&geoId=105015875&keywords=ia&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
            # "https://www.linkedin.com/jobs/search/?currentJobId=4328840036&f_TPR=r604800&geoId=105015875&keywords=data%20scientist&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",           
            # "https://www.linkedin.com/jobs/search/?currentJobId=4268215805&f_TPR=r604800&geoId=104738515&keywords=ai&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            # "https://www.linkedin.com/jobs/search/?currentJobId=4328649541&f_TPR=r604800&geoId=103819153&keywords=ai&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            # "https://www.linkedin.com/jobs/search/?currentJobId=4328720114&f_TPR=r604800&geoId=105117694&keywords=ai&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            # "https://www.linkedin.com/jobs/search/?currentJobId=4327998636&f_TPR=r604800&geoId=100456013&keywords=ai&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            # "https://www.linkedin.com/jobs/search/?currentJobId=4268215805&f_TPR=r604800&geoId=104738515&keywords=data%20scientist&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            # "https://www.linkedin.com/jobs/search/?currentJobId=4328649541&f_TPR=r604800&geoId=103819153&keywords=data%20scientist&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            # "https://www.linkedin.com/jobs/search/?currentJobId=4328720114&f_TPR=r604800&geoId=105117694&keywords=data%20scientist&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            # "https://www.linkedin.com/jobs/search/?currentJobId=4327998636&f_TPR=r604800&geoId=100456013&keywords=data%20scientist&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
        ]

    conn = get_connection()

    # Le "with" garantit que le navigateur se ferme proprement même s'il y a une erreur (pas de processus fantomes)
    with sync_playwright() as p:
        # headless=False pour voir chromium en live et les actions de playwright
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()
        
        for offers_link in offers_links:
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
                
                # print(f"Nombre d'offres trouvées : {offres_locator.count()}")
                
                for offre in offres_locator.all():

                    job_id = offre.get_attribute("data-job-id")
                    
                    title_locator = offre.locator("strong").first
                    title = title_locator.inner_text().strip()

                    is_banned = any(word in title.lower() for word in banned_words)
                    is_needed = any(word in title.lower() for word in needed_words)

                    if not is_banned and is_needed:
                        link = f"https://www.linkedin.com/jobs/view/{job_id}/"
                        # print(f"Acceptée : ID: {job_id} | Titre: {title}")
                        offre.click()
                        time.sleep(1)
                        offer_details = page.locator(".jobs-search__job-details")
                        company_selector = ".job-details-jobs-unified-top-card__company-name a"
                        company_name = offer_details.locator(company_selector).first.inner_text().strip()
                        location_selector = ".job-details-jobs-unified-top-card__primary-description-container span span"
                        location = offer_details.locator(location_selector).first.inner_text().strip()
                        location = location.split(',')
                        location = [s.strip() for s in location]
                        description_selector = ".jobs-description__container div div div p"
                        description = offer_details.locator(description_selector).first.inner_text().strip()
                        # print(f"Entreprise trouvée : {company_name}")
                        # print(f"Emplacement : {location}")
                        # print(f"Description : {description}")
                        # page.pause()
                        
                        insert_offer(conn,
                                    job_id="linkedin-"+job_id,
                                    website="linkedin",
                                    company=company_name,
                                    description=description,
                                    city=location[0] if len(location) >2 else "",
                                    state=location[1] if len(location) >2 else "",
                                    country=location[2] if len(location) >2 else "",
                                    name=title,
                                    link=link)
                    # else:
                    #     print(f"Refusée : ID: {job_id} | Titre: {title}")

                next_button = page.locator('button[aria-label="View next page"]')
                
                if next_button.count()>0:
                    next_button.click()
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