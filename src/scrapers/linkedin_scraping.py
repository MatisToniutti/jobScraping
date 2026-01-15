from playwright.sync_api import sync_playwright
from utils.sqlitedb import get_connection, create_offers_table, insert_offer
import time
import random

LAST_DAY = "r86400"
LAST_WEEK = "r604800"

def run_scraper():
    #liste des mots qu'on ne veut pas dans une offre
    banned_words = ["confirmé","product owner","stage","internship","alternance","stagiaire","intern","alternant","interim","freelance","docteur","phd","senior","expert","consultant","annotator","annotation", "expérimenté", "data engineer"]
    #liste des mots qui permettent de considérer une offre
    needed_words = [" ia", "ia ", " ai", "ai ","data", "ml", "cv", "nlp", "llm", "agent"]

    date_posted = LAST_DAY
    offers_links = [
            f"https://www.linkedin.com/jobs/search/?f_TPR={date_posted}&geoId=105015875&keywords=ia&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
            f"https://www.linkedin.com/jobs/search/?f_TPR={date_posted}&geoId=105015875&keywords=data%20scientist&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",           
            f"https://www.linkedin.com/jobs/search/?f_TPR={date_posted}&geoId=104738515&keywords=ai&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            f"https://www.linkedin.com/jobs/search/?f_TPR={date_posted}&geoId=103819153&keywords=ai&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            f"https://www.linkedin.com/jobs/search/?f_TPR={date_posted}&geoId=105117694&keywords=ai&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            f"https://www.linkedin.com/jobs/search/?f_TPR={date_posted}&geoId=100456013&keywords=ai&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            f"https://www.linkedin.com/jobs/search/?f_TPR={date_posted}&geoId=104738515&keywords=data%20scientist&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            f"https://www.linkedin.com/jobs/search/?f_TPR={date_posted}&geoId=103819153&keywords=data%20scientist&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            f"https://www.linkedin.com/jobs/search/?f_TPR={date_posted}&geoId=105117694&keywords=data%20scientist&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
            f"https://www.linkedin.com/jobs/search/?f_TPR={date_posted}&geoId=100456013&keywords=data%20scientist&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true",
        ]

    conn = get_connection()

    # Le "with" garantit que le navigateur se ferme proprement même s'il y a une erreur (pas de processus fantomes)
    with sync_playwright() as p:
        # headless=False pour voir chromium en live et les actions de playwright
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()
        
        for offers_link in offers_links:
            try:
                print(f"Ouverture de : {offers_link}")
                page.goto(offers_link)

                next_page = True

                while next_page:
                    try:
                        #on attend qu'au moins une offre ait chargée
                        page.wait_for_selector('[data-job-id]', timeout=10000)
                    except:
                        print("Aucune offre trouvée sur cette page ou chargement trop lent.")
                        break
                    
                    # on récupère un "locator" qui pointe vers toutes les div ayant l'attribut data-job-id (les offres)
                    offres_locator = page.locator('div[data-job-id]')

                    # on récupère la barre de scroll permettant de scroller les offres sinon on ne peut pas toutes les récupérer
                    conteneur_scroll = offres_locator.first.locator('xpath=./../../../..')
                    scroll_element(conteneur_scroll,distance=3000)
                    
                    # print(f"Nombre d'offres trouvées : {offres_locator.count()}")
                    
                    for offre in offres_locator.all():

                        try:

                            title_locator = offre.locator("strong").first
                            if title_locator.count() == 0: continue
                            title = title_locator.inner_text(timeout=2000).strip()

                            is_banned = any(word in title.lower() for word in banned_words)
                            is_needed = any(word in title.lower() for word in needed_words)

                            if not is_banned and is_needed:
                                job_id = offre.get_attribute("data-job-id")
                                link = f"https://www.linkedin.com/jobs/view/{job_id}/"
                                # print(f"Acceptée : ID: {job_id} | Titre: {title}")
                                offre.click()
                                time.sleep(0.1)

                                offer_details = page.locator(".jobs-search__job-details")
                                offer_details.wait_for(state="visible", timeout=5000)

                                company_selector = ".job-details-jobs-unified-top-card__company-name a"
                                company_locator = offer_details.locator(company_selector).first
                                # count() est instantané, il ne force pas d'attente
                                if company_locator.count() > 0:
                                    company_name = company_locator.inner_text().strip()
                                else:
                                    company_name = "Inconnu"

                                loc_locator = offer_details.locator(".job-details-jobs-unified-top-card__primary-description-container span span").first
                                location_raw = loc_locator.inner_text(timeout=2000).strip() if loc_locator.count() > 0 else ""
                                location = [s.strip() for s in location_raw.split(',')]

                                desc_locator = offer_details.locator(".jobs-description__container div div div p").first
                                if desc_locator.count() > 0:
                                    description = desc_locator.inner_text(timeout=2000).strip()
                                else:
                                    continue
                                
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

                        except TimeoutError:
                            print(f"Erreur : L'offre a mis trop de temps à charger. Passage à la suivante.")
                            continue
                        except Exception as e:
                            print(f"Une erreur imprévue est survenue : {e}")
                            continue
                            

                    next_button = page.locator('button[aria-label="View next page"]')
                    
                    if next_button.count()>0:
                        next_button.click()
                    else:
                        next_page=False
            except Exception as e:
                # Ici on attrape les erreurs au niveau de la PAGE/LIEN
                print(f"Erreur critique sur le lien {offers_link} : {e}")
                continue

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

def scroll(page, direction="down", sleep_min = 0.7, sleep_max = 1):
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
        for i in range(random.randint(7,10)):
            element.evaluate(f"el => el.scrollTop += {step}")
            pixels_parcourus += step
            
            time.sleep(random.uniform(0.02, 0.04))
        time.sleep(random.uniform(0.05,0.15))

if __name__ == "__main__":
    run_scraper()