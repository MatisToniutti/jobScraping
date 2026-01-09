import linkedin_scrapping
import apec_scrapping
from job_interest import give_interest_to_jobs
from test import export_links

def main():
    linkedin_scrapping.run_scraper()
    apec_scrapping.run_scraper()
    give_interest_to_jobs()
    export_links()

if __name__ == "__main__":
    main()