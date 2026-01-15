import src.scrapers.linkedin_scraping as linkedin
import src.scrapers.apec_scraping as apec
import src.scrapers.france_travail_scraping as ft
from src.models.job_interest import give_interest_to_jobs
from src.utils.utils import export_links

def main():
    apec.run_scraper()
    print("Apec scraping effectué")
    ft.run_scraper()
    print("france travail scraping effectué")
    linkedin.run_scraper()
    print("linkedin scraping effectué")
    
    give_interest_to_jobs()
    export_links()

if __name__ == "__main__":
    main()