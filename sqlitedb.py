import sqlite3

def get_connection(db_name="jobs_scraping.db"):
    """Crée ou récupère la connexion à la base de données."""
    conn = sqlite3.connect(db_name)
    # Cette ligne permet d'accéder aux colonnes par leur nom (ex: row['name'])
    conn.row_factory = sqlite3.Row 
    return conn

def create_offers_table(conn):
    """Crée spécifiquement la table des annonces si elle n'existe pas."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS offers (
            id TEXT PRIMARY KEY,
            website TEXT,
            name TEXT,
            company TEXT,
            city TEXT,
            country TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

def insert_offer(conn, job_id, website, name):
    """Insère une annonce en ignorant les doublons."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO offers (id, website, name)
            VALUES (?, ?, ?)
        ''', (job_id, website, name))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")

if __name__ == "__main__":
    conn = get_connection()
    create_offers_table(conn)
    conn.close()