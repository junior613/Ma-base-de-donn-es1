import pandas as pd
import os
import re

def clean_phone(phone):
    if pd.isna(phone):
        return phone
    # Remove non-numeric characters
    cleaned = re.sub(r'\D', '', str(phone))
    # Return formatted if it looks like a standard number, or just the digits
    return cleaned

def clean_email(email):
    if pd.isna(email) or str(email).lower() == 'nan' or str(email).lower() == 'inconnu':
        return None
    return str(email).strip().lower()

def standardize_city(city, context=""):
    if pd.isna(city):
        city = ""
    city = str(city).strip()
    
    # Check context (like segment_detecte or address) if city is empty
    full_text = f"{city} {context}".lower()
    
    if any(v in full_text for v in ['douala', 'doua', 'dla']):
        return 'Douala'
    if any(v in full_text for v in ['yaoundé', 'yaounde', 'younde', 'yde']):
        return 'Yaoundé'
    if any(v in full_text for v in ['bafoussam', 'bfs']):
        return 'Bafoussam'
    
    return city if city else 'Inconnu'

def process_lead_files(fichiers, on_error=None):
    """
    Charge, fusionne, nettoie et standardise les données depuis une liste de fichiers.
    """
    if not fichiers:
        return None

    all_leads = []
    for fichier in fichiers:
        nom_fichier = ""
        try:
            if hasattr(fichier, 'name'):
                nom_fichier = fichier.name
            else:
                nom_fichier = os.path.basename(fichier)

            # Ignorer les fichiers consolidés pour ne pas les relire en boucle
            if "propre" in nom_fichier.lower():
                if len(fichiers) > 1: continue

            df = pd.read_excel(fichier)

            # Extraction du segment (Ville/Catégorie)
            match = re.search(r"Advanced Search Response (.*?) \d+ CM", nom_fichier)
            df['segment_detecte'] = match.group(1).strip() if match else "Autre"

            all_leads.append(df)
        except Exception as e:
            error_message = f"Erreur lors de la lecture du fichier '{nom_fichier}': {e}"
            if on_error: on_error(error_message)
            else: print(f"❌ {error_message}")

    if not all_leads:
        return None

    df_total = pd.concat(all_leads, ignore_index=True)

    # --- STANDARDISATION DES COLONNES (Mapping vers structure attendue par le Dashboard) ---
    mapping = {
        'noms': 'nom', 'name': 'nom', 'business name': 'nom', 'title': 'nom',
        'email': 'email', 'e-mail': 'email',
        'téléphone': 'téléphone', 'téléphones': 'téléphone', 'phone': 'téléphone', 'tel': 'téléphone',
        'source': 'source',
        'status': 'status',
        'budget': 'budget',
        'score': 'note google', 'note google': 'note google', 'google score': 'note google',
        'nombres de vues': 'review_count', 'review count': 'review_count', 'reviews': 'review_count',
        'ville': 'ville', 'villes': 'ville', 'city': 'ville', 'quartiers': 'ville',
        'catégorie': 'catégorie', 'categories': 'catégorie', 'type': 'catégorie',
        'maps url': 'Maps URL', 'url googlemaps': 'Maps URL',
        'facebook': 'URL_Facebook', 'url facebook': 'URL_Facebook',
        'instagram': 'URL_Instagram', 'url instagram': 'URL_Instagram'
    }
    
    cols_found = {}
    for col in df_total.columns:
        col_clean = col.lower().strip().replace('_', ' ').replace('.', ' ')
        new_name = mapping.get(col_clean)
        if new_name:
            cols_found[col] = new_name

    df_total = df_total.rename(columns=cols_found)

    # Fusion des colonnes dupliquées
    if df_total.columns.duplicated().any():
        parts = []
        for col in df_total.columns.unique():
            subset = df_total[col]
            if isinstance(subset, pd.DataFrame):
                if col in ['téléphone', 'email', 'Maps URL', 'URL_Facebook', 'URL_Instagram']:
                    parts.append(subset.apply(lambda x: ' | '.join(x.dropna().astype(str).unique()), axis=1).rename(col))
                else:
                    parts.append(subset.ffill(axis=1).iloc[:, -1].rename(col))
            else:
                parts.append(subset)
        df_total = pd.concat(parts, axis=1)

    # S'assurer que toutes les colonnes cibles existent pour le Dashboard
    target_cols = ['nom', 'email', 'téléphone', 'ville', 'catégorie', 'Maps URL', 'note google', 'review_count', 'status', 'source', 'budget', 'URL_Facebook', 'URL_Instagram']
    for col in target_cols:
        if col not in df_total.columns:
            df_total[col] = None

    # --- NETTOYAGE ET ENRICHISSEMENT ---
    if 'nom' in df_total.columns:
        df_total['nom'] = df_total['nom'].astype(str).str.title().str.strip()
    
    if 'email' in df_total.columns:
        df_total['email'] = df_total['email'].apply(clean_email)
    
    if 'téléphone' in df_total.columns:
        df_total['téléphone'] = df_total['téléphone'].apply(clean_phone)
        
    if 'ville' in df_total.columns:
        df_total['ville'] = df_total.apply(lambda row: standardize_city(row['ville'], row['segment_detecte']), axis=1)

    # Remplissage des valeurs par défaut
    df_total['status'] = df_total['status'].fillna('Nouveau')
    df_total['budget'] = df_total['budget'].fillna('Inconnu')
    df_total['source'] = df_total['source'].fillna('Import')

    # Nettoyage final des doublons
    df_total = df_total.drop_duplicates(subset=['nom', 'ville'], keep='first')
    
    # Conversion numérique finale pour les colonnes de score et d'avis
    df_total['note google'] = pd.to_numeric(df_total['note google'], errors='coerce')
    df_total['review_count'] = pd.to_numeric(df_total['review_count'], errors='coerce').fillna(0).astype(int)
    
    return df_total[target_cols]
