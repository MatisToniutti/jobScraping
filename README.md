# Job Scraping : Automated Filtering Pipeline

Job Hunter AI est un assistant de recherche d'emploi local conçu pour automatiser la collecte et le tri intelligent d'offres. Le projet utilise du scraping et un modèle de langage (LLM) local pour identifier les opportunités correspondant à un profil junior en IA (moi).

🛠️ **Stack Technique**
Scraping : Playwright (LinkedIn), Requests/JSON (APEC), BeautifulSoup.

Cerveau IA : Qwen 3 4B Instruct (via Hugging Face Transformers).

Base de données : SQLite.

💡 **Fonctionnement**
Extraction : Le pipeline scrape des offres multi-sources (LinkedIn, APEC, France Travail) et les stocke dans une base SQLite structurée.

Nettoyage : Les descriptions HTML sont converties en texte brut via BeautifulSoup pour optimiser le traitement par l'IA.

Filtrage Intelligent : Un modèle Qwen local analyse chaque offre selon des critères stricts (Technos, CDI, Expérience < 2 ans).

Export : Les liens validés par l'IA sont exportés dans un même fichier.


🚀 **Installation & Usage**
Pas prévus pour l'instant