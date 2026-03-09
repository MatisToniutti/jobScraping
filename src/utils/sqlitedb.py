import sqlite3
import os
from datetime import datetime, timedelta

def get_connection(db_name="jobs_scraping.db"):
    """Crée ou récupère la connexion à la base de données."""
    # 1. On récupère le dossier où se trouve CE fichier (src/utils/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. On remonte de deux niveaux pour atteindre la racine du projet
    # (utils -> src -> racine)
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    # 3. On construit le chemin vers le dossier data
    data_dir = os.path.join(project_root, "src/database")
    conn = sqlite3.connect(os.path.join(data_dir, db_name))
    # Cette ligne permet d'accéder aux colonnes par leur nom (ex: row['name'])
    conn.row_factory = sqlite3.Row 
    return conn

def create_offers_table(conn):
    """Crée spécifiquement la table des annonces si elle n'existe pas."""
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS offers')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS offers (
            id TEXT PRIMARY KEY,
            website TEXT,
            description TEXT,
            name TEXT,
            company TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            link TEXT,
            interest INTEGER DEFAULT 0, --0 = non traitée, 1 = pas intéressante, 2 = intéressante
            applied INTEGER DEFAULT 0, --0 = pas postulé, 1 = postulé
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

def insert_offer(conn, job_id, website="", description="", name="", company="",city="",state="",country="",link="", interest=0, applied=0):
    """Insère une annonce en ignorant les doublons."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO offers (id, website, description, name, company, city, state, country, link, interest, applied)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (job_id, website, description, name, company, city, state, country, link, interest, applied))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
    return cursor.rowcount > 0

def get_unprocessed_offers(conn):
    """Retourne les offres qu'on a pas encore définies comme intéressantes ou non"""
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
                   Select * 
                   from offers
                   where interest = 0
                   ''')
    
    return cursor.fetchall()

def set_interest_offer(conn, id, value):
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
                    UPDATE offers
                    SET interest = ?
                    WHERE id = ?
                   ''', (value, id))
    conn.commit()

def create_test_snapshot(hours=5):
    # Chemins des bases de données
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    source_path = os.path.join(root, "src","database", "jobs_scraping.db")
    test_path = os.path.join(root, "src", "database","test","jobs_scraping_test.db")

    if not os.path.exists(source_path):
        print(f"❌ Erreur : La base source n'existe pas ({source_path})")
        return

    # 1. Calculer la date limite (Heure actuelle - X heures)
    # SQLite utilise le format 'YYYY-MM-DD HH:MM:SS'
    limit_date = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"🔍 Recherche des offres ajoutées depuis : {limit_date}")

    # 2. Connexion aux deux bases
    # Si offers_test.db n'existe pas, SQLite va le créer
    src_conn = sqlite3.connect(source_path)
    test_conn = sqlite3.connect(test_path)
    
    src_cursor = src_conn.cursor()
    test_cursor = test_conn.cursor()

    try:
        # 3. Créer la structure de la table dans la base de test si elle n'existe pas
        # On récupère le schéma de la table 'offers' de la source
        schema = src_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='offers'").fetchone()[0]
        test_cursor.execute(schema)

        # 5. Récupérer les offres récentes depuis la source
        src_cursor.execute("SELECT * FROM offers WHERE date_added >= ?", (limit_date,))
        recent_offers = src_cursor.fetchall()

        if not recent_offers:
            print("⚠️ Aucune offre trouvée dans les dernières 5 heures.")
            return

        # 6. Insérer dans la base de test (avec IGNORE pour éviter les doublons si on relance)
        # On récupère le nombre de colonnes pour préparer les '?'
        column_count = len(recent_offers[0])
        placeholders = ", ".join(["?"] * column_count)
        
        # Note: On insère dans toutes les colonnes d'origine
        query = f"INSERT OR IGNORE INTO offers VALUES ({placeholders})"
        
        test_cursor.executemany(query, recent_offers)
        test_conn.commit()

        print(f"✅ Succès : {len(recent_offers)} offres copiées dans '{test_path}'.")
        print(f"🚀 Tu peux maintenant uploader 'offers_test.db' ou l'utiliser pour ton labeling.")

    except Exception as e:
        print(f"❌ Une erreur est survenue : {e}")
    
    finally:
        src_conn.close()
        test_conn.close()
    
if __name__ == "__main__":
    create_test_snapshot(hours=5)