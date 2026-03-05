import pandas as pd
import os
from lead_processor import process_lead_files

def analyser_leads(fichiers, fichier_sortie):
    
    if not fichiers:
        print("Aucun fichier d'entrée n'a été fourni.")
        return
    
    print(f"--- Début de l'analyse pour {len(fichiers)} fichiers ---\n")

    # Appel de la fonction de traitement centralisée
    df_final = process_lead_files(fichiers)

    if df_final is None or df_final.empty:
        print("Aucune donnée n'a été traitée. Fin du script.")
        return

    print(f"--- Leads restants après nettoyage : {len(df_final)} ---")

    # 5. Export du fichier final
    try:
        df_final.to_excel(fichier_sortie, index=False)
        print(f"\n✅ Fichier consolidé et classifié sauvegardé sous : {fichier_sortie}")
        
        # --- NOUVEAUTÉ : Tri Sélectif Automatique ---
        try:
            # Conversion pour le filtrage
            df_final['Score_num'] = pd.to_numeric(df_final['note google'], errors='coerce')
            df_final['Views_num'] = pd.to_numeric(df_final['review_count'], errors='coerce')
            
            # Filtre : Score >= 4.0 ou populaire, avec téléphone (ou score très élevé)
            has_phone = df_final['téléphone'].notna() & (df_final['téléphone'] != '')
            is_high_score = df_final['Score_num'] >= 4.0
            is_popular = df_final['Views_num'] >= 20
            
            df_select = df_final[
                (has_phone & (is_high_score | is_popular)) |
                (is_high_score & (df_final['Score_num'] >= 4.5)) 
            ].copy()
            
            # Tri
            df_select = df_select.sort_values(by=['Score_num', 'Views_num'], ascending=[False, False])
            
            # Sauvegarde
            dossier = os.path.dirname(fichier_sortie)
            path_select = os.path.join(dossier, "Leads-sélectionnés.xlsx")
            df_select.drop(columns=['Score_num', 'Views_num']).to_excel(path_select, index=False)
            print(f"✨ Tri sélectif effectué : {len(df_select)} top leads sauvegardés dans '{os.path.basename(path_select)}'")
            
        except Exception as e_select:
            print(f"⚠️ Erreur lors du tri sélectif : {e_select}")
        # --------------------------------------------

    except PermissionError:
        print(f"\n⚠️ ATTENTION : Le fichier '{fichier_sortie}' est ouvert dans Excel.")
        base, ext = os.path.splitext(fichier_sortie)
        fallback_file = f"{base}_v2{ext}"
        df_final.to_excel(fallback_file, index=False)
        print(f"✅ Sauvegarde effectuée sous un autre nom pour éviter l'erreur : {fallback_file}")

if __name__ == "__main__":
    # Utilise le dossier où se trouve ce script
    dossier_leads = os.path.dirname(os.path.abspath(__file__))
    # Le dossier racine est le parent de "Leads"
    dossier_racine = os.path.dirname(dossier_leads)

    # --- CONFIGURATION ---
    # Liste des fichiers à analyser.
    fichiers_entrants_noms = ["Book1.xlsx", "Book2.xlsx", "Book3.xlsx"]
    # Nom du fichier de sortie
    fichier_sortie_nom = "Leads-consolidés-propre.xlsx"
    # --- FIN CONFIGURATION ---

    # On cherche les fichiers à la racine
    fichiers_a_analyser = [os.path.join(dossier_racine, f) for f in fichiers_entrants_noms]
    fichiers_existants = [f for f in fichiers_a_analyser if os.path.exists(f)]

    if not fichiers_existants:
        # Fallback : chercher dans le dossier Leads au cas où
        fichiers_a_analyser_leads = [os.path.join(dossier_leads, f) for f in fichiers_entrants_noms]
        fichiers_existants = [f for f in fichiers_a_analyser_leads if os.path.exists(f)]

    if not fichiers_existants:
        print(f"⚠️ Aucun des fichiers spécifiés n'a été trouvé à la racine ou dans Leads : {fichiers_entrants_noms}")
    else:
        print(f"Fichiers trouvés : {[os.path.basename(f) for f in fichiers_existants]}")
        # On sauvegarde le résultat dans le dossier Leads
        fichier_sortie_path = os.path.join(dossier_leads, fichier_sortie_nom)
        analyser_leads(fichiers_existants, fichier_sortie_path)
