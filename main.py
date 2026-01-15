import linkedin_scraping
import apec_scraping
import france_travail_scraping
from job_interest import give_interest_to_jobs
from test import export_links

def main():
    apec_scraping.run_scraper()
    print("Apec scraping effectué")
    france_travail_scraping.run_scraper()
    print("france travail scraping effectué")
    linkedin_scraping.run_scraper()
    print("linkedin scraping effectué")
    
    give_interest_to_jobs()
    export_links()

if __name__ == "__main__":
    main()