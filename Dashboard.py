import streamlit as st
import pandas as pd
import os
import glob
import re
from lead_processor import process_lead_files

# Configuration de la page
st.set_page_config(page_title="Lead Booster", layout="wide", page_icon="✨")

# --- STYLE & ANIMATION ---
def add_custom_background():
    page_bg_html = """
   <style>
        .stApp {
            background: linear-gradient(45deg, #3498db, #e74c3c, #2ecc71, #f1c40f);
            background-size: 400% 400%;
            animation: gradient 15s linear infinite;
        }

        @keyframes gradient {
            0% {
                background-position: 0% 50%;
            }

            50% {
                background-position: 100% 50%;
            }

            100% {
                background-position: 0% 50%;
            }
        }

        /* Cube animation */
        .container {
            perspective: 800px;
            width: 200px;
            height: 200px;
            position: relative;
            margin: 100px auto;
            animation: rotate 10s linear infinite;
        }

        .cube {
            width: 100%;
            height: 100%;
            transform-style: preserve-3d
        }

        .face {
            position: absolute;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid #000;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
        }

        .font {
            transform: translateZ(100px);
        }

        .back {
            transform: rotateY(180deg) translateZ(100px);
        }

        .right {
            transform: rotateY(90deg) translateZ(100px);
        }

        .left {
            transform: rotateY(-90deg) translateZ(100px);
        }

        .top {
            transform: rotateX(90deg) translateZ(100px);
        }

        .bottom {
            transform: rotateX(-90deg) translateZ(100px);
        }

        @keyframes rotate {
            0% {
                transform: rotateX(0) rotateY(0) rotateZ(0);
            }

            100% {
                transform: rotateX(360deg) rotateY(360deg) rotateZ(360deg);
            }
        }
    </style>
    <div class="container">
        <div class="cube">
            <div class="face font"></div>
            <div class="face back"></div>
            <div class="face right"></div>
            <div class="face left"></div>
            <div class="face top"></div>
            <div class="face bottom"></div>
        </div>
    </div>

    """
    st.markdown(page_bg_html, unsafe_allow_html=True)

# Appliquer le style personnalisé
add_custom_background()

# --- FONCTION DE CHARGEMENT ET NETTOYAGE (Reprise de votre script) ---
@st.cache_data
def charger_et_nettoyer_donnees(fichiers):
    """
    Charge, fusionne, nettoie et standardise les données depuis une liste de fichiers.
    La liste peut contenir des chemins de fichiers (str) ou des objets UploadedFile de Streamlit.
    """
    # On passe la fonction st.error comme callback pour afficher les erreurs dans l'interface
    return process_lead_files(fichiers, on_error=st.error)


# --- MOTEUR D'AUDIT STRATÉGIQUE ---
def generer_audit(row):
    score = 0
    max_score = 5  # Le score maximal possible
    points_forts = []
    points_faibles = []
    opportunites = []

    # 1. Analyse Site Web
    if pd.notna(row['Maps URL']) and str(row['Maps URL']).strip() != "":
        score += 1
        points_forts.append("✅ **Maps URL** : Présence confirmée.")
    else:
        points_faibles.append("❌ Pas de lien Maps détecté")
        opportunites.append({
            "icon": "🌐",
            "title": "Maps URL Inexistant",
            "action": "Vendre la création d'un site vitrine ou e-commerce."
        })

    # 2. Analyse Réseaux Sociaux
    if pd.notna(row['URL_Facebook']) and str(row['URL_Facebook']).strip() != "":
        score += 1
        points_forts.append("✅ **Réseaux Sociaux** : Présence détectée.")
    else:
        points_faibles.append("❌ Pas de Facebook/Instagram détecté")
        opportunites.append({
            "icon": "📱",
            "title": "Absence sur les Réseaux Sociaux",
            "action": "Proposer du Community Management et la création de pages professionnelles."
        })

    # 3. Analyse Réputation (Note)
    note = row['note google']
    if pd.notna(note):
        try:
            note = float(note)
            if note >= 4.5:
                score += 1
                points_forts.append(f"✅ **Réputation** : Excellente ({note}/5).")
            elif note >= 3.5:
                score += 0.5
                points_faibles.append(f"⚠️ Réputation moyenne ({note}/5)")
                opportunites.append({
                    "icon": "⭐",
                    "title": "Réputation à Améliorer",
                    "action": "Proposer une campagne de collecte d'avis positifs (email, QR code)."
                })
            else:
                points_faibles.append(f"🚨 Mauvaise réputation ({note}/5)")
                opportunites.append({
                    "icon": "🚨",
                    "title": "E-réputation en Crise",
                    "action": "URGENCE : Proposer une stratégie de gestion de crise et d'amélioration de l'e-réputation."
                })
        except (ValueError, TypeError):
            pass
    else:
        points_faibles.append("❓ Aucune note Google")
        opportunites.append({
            "icon": "🗺️",
            "title": "Fiche Google Manquante ou Incomplète",
            "action": "Créer et optimiser la fiche Google Business Profile pour apparaître sur la carte."
        })

    # 4. Analyse Visibilité (Nombre d'avis)
    avis = row['review_count']
    if pd.notna(avis):
        try:
            avis = int(avis)
            if avis > 50:
                score += 1
                points_forts.append(f"✅ **Visibilité** : Forte ({avis} avis).")
            elif avis > 10:
                score += 0.5
                points_faibles.append(f"⚠️ Visibilité modérée ({avis} avis)")
            else:
                points_faibles.append(f"📉 Très peu de visibilité ({avis} avis)")
                opportunites.append({
                    "icon": "🔍",
                    "title": "Manque de Visibilité Locale",
                    "action": "Mettre en place une stratégie de SEO local pour augmenter la visibilité et le nombre d'avis."
                })
        except (ValueError, TypeError):
            pass

    # 5. Contactabilité
    if pd.notna(row['téléphone']):
        score += 1
        points_forts.append("✅ **Contact** : Numéro de téléphone disponible.")
    else:
        points_faibles.append("❌ Pas de numéro de téléphone")

    return score, max_score, points_forts, points_faibles, opportunites

# --- FONCTIONS D'AFFICHAGE (UI) ---
def afficher_audit_ui(row):
    st.markdown("---")
    st.header(f"✨ Audit Stratégique : {row['nom']}")

    # Calcul de l'audit
    score, max_score, forts, faibles, opportunites = generer_audit(row)

    # Barre de score visuelle
    st.progress(score / max_score, text=f"Score de Maturité Digitale : {int(score)}/{max_score}")

    # Métriques clés
    col1, col2, col3 = st.columns(3)
    note_display = f"{row['note google']}/5" if pd.notna(row['note google']) else "N/A"
    col1.metric(label="⭐ Note Google", value=note_display)
    
    avis_display = f"{int(row['review_count'])}" if pd.notna(row['review_count']) else "N/A"
    col2.metric(label="✍️ Nombre d'Avis", value=avis_display)

    has_socials = "✅ Oui" if pd.notna(row['URL_Facebook']) and str(row['URL_Facebook']).strip() != "" else "❌ Non"
    col3.metric(label="📱 Présence Sociale", value=has_socials)

    st.markdown("---")

    # Section des opportunités, la plus importante
    st.subheader("🎯 Plan d'Action Commercial")
    if not opportunites:
        st.success("✅ **Excellent profil !** Ce prospect est digitalement mature. Proposez des services avancés (Publicité, SEO technique, Automatisation).")
    else:
        for opp in opportunites:
            with st.container(border=True):
                st.markdown(f"**{opp['icon']} {opp['title']}**")
                st.write(f"👉 {opp['action']}")

    # Détails dans un expander
    with st.expander("🔍 Voir l'analyse détaillée (Forces / Faiblesses)"):
        c_a, c_b = st.columns(2)
        with c_a:
            st.write("**Points Forts :**")
            if forts:
                for p in forts: st.markdown(p)
            else:
                st.write("Aucun point fort majeur détecté.")
        with c_b:
            st.write("**Faiblesses :**")
            if faibles:
                for p in faibles: st.markdown(p)
            else:
                st.write("Aucun point faible majeur détecté.")

    # Section de contact et suivi
    st.markdown("---")
    col_info, col_suivi = st.columns([2, 1])
    with col_info:
        st.subheader("Fiche de Contact")
        st.write(f"**📍 Ville:** {row['ville']}")
        st.write(f"**📞 Tél:** {row['téléphone'] if pd.notna(row['téléphone']) else 'Non trouvé'}")
        st.write(f"**🌐 Maps:** {row['Maps URL'] if pd.notna(row['Maps URL']) else 'Non trouvé'}")

    with col_suivi:
        prospect_id = f"{row['nom']}@{row['ville']}"
        if 'contacted_prospects' not in st.session_state:
            st.session_state.contacted_prospects = {}

        if prospect_id not in st.session_state.contacted_prospects:
            if st.button("➕ Ajouter au suivi", key=f"contact_{prospect_id}", type="primary", use_container_width=True):
                st.session_state.contacted_prospects[prospect_id] = {
                    'notes': f"Prospect ajouté le {pd.Timestamp.now().strftime('%d/%m/%Y à %H:%M')}.\n",
                    'data': row.to_dict()
                }
                st.success(f"Ajouté au suivi !")
                st.toast('✅ Prospect ajouté !', icon='🎉')
                st.rerun()
        else:
            st.info("📌 Déjà dans le suivi.")

def afficher_page_suivi():
    st.title("📝 Suivi des Relances")

    if 'contacted_prospects' not in st.session_state or not st.session_state.contacted_prospects:
        st.info("Aucun prospect dans la liste de suivi. 🕵️‍♂️", icon="ℹ️")
        st.write("👈 Retournez sur l'Audit et cliquez sur '➕ Ajouter au suivi' pour commencer.")
        return

    st.success(f"**{len(st.session_state.contacted_prospects)}** prospect(s) en cours de suivi.", icon="🎯")

    prospect_ids = list(st.session_state.contacted_prospects.keys())
    display_names = [f"{pid.split('@')[0]} ({pid.split('@')[1]})" for pid in prospect_ids]

    selected_display = st.selectbox("Sélectionnez un prospect à suivre :", options=display_names)

    if selected_display:
        idx = display_names.index(selected_display)
        selected_id = prospect_ids[idx]
        
        info = st.session_state.contacted_prospects[selected_id]
        data = info['data']
        
        st.subheader(f"Historique pour : {data['nom']}")
        
        c1, c2 = st.columns([2, 1])
        with c1:
            notes = st.text_area("Notes sur les échanges (appels, emails, etc.)", value=info['notes'], height=300, key=f"note_{selected_id}", label_visibility="collapsed")
            
            col_save, col_del = st.columns(2)
            with col_save:
                if st.button("💾 Enregistrer les notes", key=f"save_{selected_id}", use_container_width=True):
                    st.session_state.contacted_prospects[selected_id]['notes'] = notes
                    st.toast("Notes mises à jour !", icon="👍")
            with col_del:
                if st.button("🗑️ Retirer du suivi", key=f"del_{selected_id}", use_container_width=True):
                    del st.session_state.contacted_prospects[selected_id]
                    st.toast(f"{data['nom']} retiré du suivi.", icon="🗑️")
                    st.rerun()
        with c2:
            with st.container(border=True):
                st.markdown("##### Fiche Rapide")
                st.write(f"**📞 Tél:** {data['téléphone'] if pd.notna(data['téléphone']) else 'N/A'}")
                st.write(f"**🌐 Maps:** {data['Maps URL'] if pd.notna(data['Maps URL']) else 'N/A'}")
                st.write(f"**⭐ Note:** {data['note google'] if pd.notna(data['note google']) else 'N/A'}/5")
                st.write(f"**✍️ Avis:** {data['review_count'] if pd.notna(data['review_count']) else 'N/A'}")

# --- INTERFACE UTILISATEUR ---

# --- INITIALISATION SESSION STATE ---
if 'contacted_prospects' not in st.session_state:
    st.session_state.contacted_prospects = {}

# --- NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Audit de Leads", "Suivi des Relances"])

if page == "Suivi des Relances":
    afficher_page_suivi()

elif page == "Audit de Leads":
    st.title("📊 Plateforme d'Audit de Leads")

    # Barre latérale pour l'upload des fichiers
    st.sidebar.header("📂 Importation des données")
    uploaded_files = st.sidebar.file_uploader("Déposez vos fichiers Excel ici", accept_multiple_files=True, type=['xlsx'])

    # Logique de chargement des données :
    # Priorité aux fichiers uploadés. Sinon, on charge ceux du dossier local.
    fichiers_a_charger = []
    if uploaded_files:
        fichiers_a_charger = uploaded_files
        st.sidebar.info(f"{len(uploaded_files)} fichier(s) chargé(s) via l'upload.")
    else:
        st.sidebar.info("Aucun fichier uploadé. Recherche dans le dossier local...")
        try:
            dossier_courant = os.path.dirname(os.path.abspath(__file__))
            dossier_racine = os.path.dirname(dossier_courant)
            
            # Recherche dans Leads
            fichiers_leads = glob.glob(os.path.join(dossier_courant, "*.xlsx"))
            # Recherche à la racine
            fichiers_racine = glob.glob(os.path.join(dossier_racine, "*.xlsx"))
            
            tous_fichiers = fichiers_leads + fichiers_racine
            
            # Priorité : Leads-sélectionnés > Leads-consolidés-propre
            fichier_selectionne = [f for f in tous_fichiers if "Leads-sélectionnés.xlsx" in f]
            if not fichier_selectionne:
                fichier_selectionne = [f for f in tous_fichiers if "Leads-consolidés-propre.xlsx" in f]
            
            if fichier_selectionne:
                fichiers_a_charger = [fichier_selectionne[0]]
                st.sidebar.success(f"Fichier {'sélectionné' if 'sélectionnés' in fichier_selectionne[0] else 'propre'} trouvé et priorisé.")
            else:
                fichiers_a_charger = [f for f in tous_fichiers if "propre" not in f and "sélectionné" not in f.lower() and "consolidé" not in f.lower()]
            
            if fichiers_a_charger:
                st.sidebar.success(f"{len(fichiers_a_charger)} fichier(s) trouvé(s) (Local/Racine).")
        except NameError: 
            st.sidebar.warning("Impossible de déterminer le dossier local.")

    df = charger_et_nettoyer_donnees(fichiers_a_charger)

    if df is not None:
        # Filtres latéraux
        st.sidebar.header("🎯 Filtres")
        villes = st.sidebar.multiselect("Filtrer par Ville", options=df['ville'].unique(), key="db_villes")
        categories = st.sidebar.multiselect("Filtrer par Catégorie", options=df['catégorie'].unique(), key="db_categories")

        df_filtre = df.copy()
        if villes:
            df_filtre = df_filtre[df_filtre['ville'].isin(villes)]
        if categories:
            df_filtre = df_filtre[df_filtre['catégorie'].isin(categories)]

        st.write(f"**{len(df_filtre)} prospects trouvés**")

        st.markdown("---")
        st.subheader("Base de données complète")

        # Sélection du prospect pour l'audit (juste au-dessus du tableau)
        prospect_selectionne = st.selectbox("🔍 Rechercher ou sélectionner une entreprise pour voir l'audit :", df_filtre['nom'].unique())

        st.dataframe(df_filtre)

        if prospect_selectionne:
            row = df_filtre[df_filtre['nom'] == prospect_selectionne].iloc[0]

            # Utilisation de la fonction d'affichage centralisée
            afficher_audit_ui(row)

    else:
        st.info("👋 **Bienvenue sur Lead Booster !** Chargez vos fichiers pour lancer la magie.", icon="🚀")
        st.markdown("""
        **Comment ça marche ?**
        1.  Dans le menu à gauche, cliquez sur **Browse files** ou glissez-déposez vos fichiers Excel.
        2.  L'outil analyse, nettoie et enrichit vos données automatiquement.
        3.  Sélectionnez un prospect dans la liste pour obtenir un audit stratégique et un plan d'action.
        
        *Si aucun fichier n'est fourni, l'outil essaiera de charger les fichiers `.xlsx` présents dans son dossier.*
        """)
