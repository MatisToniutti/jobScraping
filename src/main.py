import scrapers.linkedin_scraping as linkedin
import scrapers.apec_scraping as apec
import scrapers.france_travail_scraping as ft
import scrapers.WTTJ_scraping as wttj
from models.job_interest import give_interest_to_jobs
from utils.utils import export_links
from utils.vector_db import get_vector_collection, clear_vector_collection

def main():
    # collection = get_vector_collection()
    # clear_vector_collection(collection)
    # apec.run_scraper()
    # print("Apec scraping effectué")
    # ft.run_scraper()
    # print("france travail scraping effectué")
    # wttj.run_scraper()
    # print("welcome to the jungle scraping effectué")
    linkedin.run_scraper()
    print("linkedin scraping effectué")
    
    give_interest_to_jobs()
    export_links()

if __name__ == "__main__":
    main()