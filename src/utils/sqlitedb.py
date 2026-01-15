import sqlite3
import os

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

if __name__ == "__main__":
    conn = get_connection()
    create_offers_table(conn)
    conn.close()