import sqlite3
import webbrowser
import os
import sys

def label_offers():
    # 1. Configuration du chemin (ajuste le nom du fichier si besoin)
    # On cherche dans le dossier 'data' à la racine du projet
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(root, "src","database","test", "jobs_scraping_test.db")

    if not os.path.exists(db_path):
        print(f"❌ Erreur : Base de données introuvable ici : {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Permet d'accéder aux colonnes par nom
    cursor = conn.cursor()

    # 2. Vérification / Création de la colonne 'applied'
    try:
        # On tente d'ajouter la colonne si elle n'existe pas
        cursor.execute("ALTER TABLE offers ADD COLUMN applied INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        # La colonne existe déjà, on continue
        pass

    # 3. Récupération des offres non traitées (applied = 0)
    # On peut ajouter un ORDER BY date_added DESC pour voir les plus récentes
    cursor.execute("SELECT * FROM offers WHERE applied = 0")
    offers = cursor.fetchall()

    if not offers:
        print("✅ Aucune offre en attente de traitement (toutes sont notées != 0).")
        conn.close()
        return

    print(f"\n🎯 Session de Labeling : {len(offers)} offres à traiter.")
    print("Commandes : Entrez 1, 2 ou 3 pour noter. Ctrl+C pour quitter.")
    print("-" * 50)

    try:
        for index, offer in enumerate(offers):
            # Affichage console clair
            print(f"\n[{index + 1}/{len(offers)}] 🏢 {offer['company']} - {offer['name']}")
            print(f"📍 {offer['city']} | 🔗 Lien : {offer['link']}")
            
            # Ouverture automatique du navigateur
            try:
                webbrowser.open_new_tab(offer['link'])
            except Exception:
                print("⚠️ Impossible d'ouvrir le navigateur automatiquement.")

            # Boucle de validation de l'entrée utilisateur
            valid_input = False
            while not valid_input:
                try:
                    user_input = input(">>> Note (1=Non, 2=Peut-être, 3=Oui) : ").strip()
                    
                    if user_input in ['1', '2', '3']:
                        # Mise à jour de la base de données
                        cursor.execute(
                            "UPDATE offers SET applied = ? WHERE id = ?", 
                            (int(user_input), offer['id'])
                        )
                        conn.commit() # Sauvegarde immédiate (très important)
                        valid_input = True
                        print("✅ Enregistré.")
                    else:
                        print("❌ Entrée invalide. Tapez 1, 2 ou 3 (ou Ctrl+C pour sortir).")
                
                except ValueError:
                     print("❌ Erreur de format.")

    except KeyboardInterrupt:
        print("\n\n🛑 Interruption utilisateur (Ctrl+C).")
        print("💾 Toutes les modifications précédentes ont été sauvegardées.")
        print("Fermeture du programme...")
    
    finally:
        conn.close()

if __name__ == "__main__":
    label_offers()