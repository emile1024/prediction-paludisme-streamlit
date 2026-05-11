import streamlit as st
import pandas as pd
import joblib
import pydeck as pdk
import plotly.express as px
from datetime import datetime

# =====================================================
# CONFIGURATION PAGE
# =====================================================

st.set_page_config(
    page_title="Prédiction du Paludisme",
    page_icon="🦟",
    layout="wide"
)
# =====================================================
# PROTECTION PAR MOT DE PASSE
# =====================================================

def verifier_mot_de_passe():
    mot_de_passe = st.text_input(
        "Mot de passe",
        type="password"
    )

    if mot_de_passe == st.secrets["APP_PASSWORD"]:
        return True

    if mot_de_passe:
        st.error("Mot de passe incorrect")

    return False


if not verifier_mot_de_passe():
    st.stop()

def afficher_application():
    # =====================================================
    # TITRE
    # =====================================================
    
    st.title("🦟 Prédiction du Paludisme")
    st.sidebar.header("Paramètres")
    st.sidebar.markdown("---")
    
    st.write(
        """
        Prototype de prévision du paludisme
        basé sur le Machine Learning.
    
        Pays étudiés : le Burundi, le Rwanda et
        la République Démocratique du Congo.
    
        Réalisé par : Emile Nibasumba
        """
    )
    
    # =====================================================
    # CARTE DES PAYS ÉTUDIÉS
    # =====================================================
    
    df_map = pd.DataFrame({
        "Pays": [
            "Rwanda",
            "Burundi",
            "RDC"
        ],
        
        "lat": [
            -1.94,
            -3.37,
            -2.87
        ],
        
        "lon": [
            29.87,
            29.92,
            23.65
        ]
    })
    
    st.subheader("Pays étudiés")
    
    st.map(
        df_map.rename(
            columns={
                "lat": "LATITUDE",
                "lon": "LONGITUDE"
            }
        )
    )
    
    # =====================================================
    # CHOIX DU PAYS
    # =====================================================
    
    # =====================================================
    # VALEURS RÉELLES 2022
    # =====================================================
    
    valeurs_2022 = {
    
        "Rwanda": {
            "incidence": 85.57,
            "pluie": 4.55,
            "temperature": 18.96
        },
    
        "Burundi": {
            "incidence": 342.31,
            "pluie": 4.06,
            "temperature": 20.72
        },
    
        "Congo, Dem. Rep.": {
            "incidence": 327.94,
            "pluie": 5.46,
            "temperature": 17.01
        }
    }
    
    pays = st.sidebar.selectbox(
        "Choisir un pays",
        [
            "Burundi",
            "Rwanda",
            "Congo, Dem. Rep."
        ]
    )
    
    # =====================================================
    # VALEURS PAR DÉFAUT SELON LE PAYS
    # =====================================================
    
    valeurs = valeurs_2022[pays]
    
    incidence_defaut = valeurs["incidence"]
    
    pluie_defaut = valeurs["pluie"]
    
    temperature_defaut = valeurs["temperature"]

    # =====================================================
    # INITIALISATION SESSION STATE
    # =====================================================
    
    if "annee_connue" not in st.session_state:
        st.session_state.annee_connue = 2022
    
    if "incidence" not in st.session_state:
        st.session_state.incidence = incidence_defaut
    
    if "pluie" not in st.session_state:
        st.session_state.pluie = pluie_defaut
    
    if "temperature" not in st.session_state:
        st.session_state.temperature = temperature_defaut


    
    # =====================================================
    # CHARGER LE BON MODÈLE
    # =====================================================
    
    if pays == "Burundi":
        
        model = joblib.load(
            "Burundi_modele_paludisme.pkl"
        )
    
    elif pays == "Rwanda":
        
        model = joblib.load(
            "Rwanda_modele_paludisme.pkl"
        )
    
    else:
        
        model = joblib.load(
            "Congo_Dem_Rep_modele_paludisme.pkl"
        )

    # =====================================================
    # AFFICHAGE POUR UTILISATEUR
    # =====================================================
    
    st.sidebar.subheader("Variables d'entrée")
    
    st.info(
        """
        Informations importantes :
    
        • Les précipitations représentent des moyennes exprimées en millimètres par jour (mm/jour).
    
        • Les températures représentent des moyennes exprimées en degrés Celsius (°C).
    
        • L'incidence du paludisme est exprimée en nombre de cas positifs pour 1000 habitants à risque.
        """
    )

    # =====================================================
    # BOUTON RESET
    # =====================================================
    
    if st.sidebar.button("🔄 Réinitialiser les valeurs"):

        st.session_state.annee_connue = 2022
    
        st.session_state.incidence = incidence_defaut
    
        st.session_state.pluie = pluie_defaut
    
        st.session_state.temperature = temperature_defaut

        st.rerun()
    
    # =====================================================
    # ENTRÉES UTILISATEUR
    # =====================================================
    
    annee_connue = st.sidebar.number_input(
        "Dernière année connue",
        min_value=2000,
        key="annee_connue"
    )
    
    incidence_connue = st.sidebar.number_input(
        "Dernière incidence connue",
        key="incidence"
    )
    
    annee_fin = st.sidebar.number_input(
        "Année finale",
        min_value=annee_connue + 1,
        value=max(2030, annee_connue + 1)
    )
    
    pluie = st.sidebar.number_input(
        "Pluie moyenne annuelle",
        key="pluie"
    )
    
    temperature = st.sidebar.number_input(
        "Température moyenne annuelle",
        key="temperature"
    )

    # =====================================================
    # BOUTON PRÉDICTION
    # =====================================================
    
    if st.sidebar.button("Lancer la prédiction"):
        
        predictions = []
        
        annees = list(
        range(
            annee_connue + 1,
            annee_fin + 1
        )
    )
            
        incidence_prec = incidence_connue
        
        # =================================================
        # BOUCLE RÉCURSIVE
        # =================================================
        
        for annee in annees:
            
            futur = pd.DataFrame({
                
                "annee": [annee],
                
                "pluie": [pluie],
                
                "temperature": [temperature],
                
                "incidence_precedente": [
                    incidence_prec
                ]
            })
            
            prediction = model.predict(
                futur
            )[0]
            
            predictions.append(prediction)
            
            # IMPORTANT :
            # la prédiction devient
            # l'incidence précédente suivante
            
            incidence_prec = prediction
    
        df_predictions = pd.DataFrame({
            "Pays": [pays] * len(annees),
            "Année": annees,
            "Incidence prédite": predictions
        })
    
        date_export = datetime.now().strftime("%Y-%m-%d %H:%M:%S")         # création info sur la source et la date actuelle
    
        metadata = f"""Source : Application Streamlit - Prédiction du Paludisme        
        Auteur : Emile Nibasumba
        Modèle : Random Forest Regressor
        Date export : {date_export}
    
        """
    
        csv = (metadata + df_predictions.to_csv(index=False)).encode("utf-8-sig")     # création fichier csv
    
        st.download_button(                                     # ajout bouton de téléchargement
            label="📥 Télécharger les prévisions CSV",
            data=csv,
            file_name=f"predictions_{pays}.csv",
            mime="text/csv"
        )
        
        # =================================================
        # AFFICHAGE TEXTE
        # =================================================
        
        st.header(f"Résultats des prévisions pour {pays}")
        
        colonnes = st.columns(len(annees))

        for col, annee, prediction in zip(colonnes, annees, predictions):

            with col:

                st.metric(
                    label=f"Prévision {annee}",
                    value=f"{prediction:.2f}"
                )
         
    # =====================================================
    # GRAPHIQUE DES PRÉVISIONS
    # =====================================================
    
        df_graph = pd.DataFrame({
            "Année": annees,
            "Incidence": predictions,
            "Type": "Prévisions futures"
        })
    
        fig = px.line(
            df_graph,
            x="Année",
            y="Incidence",
            color="Type",
            markers=True,
            title=f"Évolution prévisionnelle de l’incidence du paludisme au {pays}"
        )
    
        fig.update_layout(
            xaxis_title="Année",
            yaxis_title="Incidence",
            template="plotly_dark"
        )
    
        st.plotly_chart(
            fig,
            use_container_width=True
        )
    
        # =====================================================
        # INTERPRÉTATION AUTOMATIQUE
        # =====================================================
    
        premiere = predictions[0]
    
        derniere = predictions[-1]
    
        difference = derniere - premiere
    
        # =====================================================
        # ANALYSE
        # =====================================================
    
        if difference > 5:
        
            interpretation = (
                f"Le modèle prévoit une augmentation progressive "
                f"de l'incidence du paludisme au {pays}."
            )
    
        elif difference < -5:
        
            interpretation = (
                f"Le modèle prévoit une diminution progressive "
                f"de l'incidence du paludisme au {pays}."
            )
    
        else:
        
            interpretation = (
                f"Le modèle prévoit une stabilisation "
                f"de l'incidence du paludisme au {pays}."
            )
    
        # =====================================================
        # AFFICHAGE
        # =====================================================
    
        st.subheader("Interprétation automatique")
    
        st.success(interpretation)
    
        # =====================================================
        # NIVEAU DE RISQUE
        # =====================================================
    
        incidence_finale = predictions[-1]
    
        # =====================================================
        # CLASSIFICATION OMS
        # =====================================================
    
        if incidence_finale < 50:
        
            niveau = "Relativement faible"
        
            message = "🟢 Niveau de risque relativement faible"
    
        elif incidence_finale < 100:
        
            niveau = "Faible"
        
            message = "🟡 Niveau de risque faible"
    
        elif incidence_finale < 250:
        
            niveau = "Modéré"
        
            message = "🟠 Niveau de risque modéré"
    
        elif incidence_finale < 400:
        
            niveau = "Élevé"
        
            message = "🔴 Niveau de risque élevé"
    
        else:
        
            niveau = "Très élevé"
        
            message = "🚨 Niveau de risque très élevé"
    
        # =====================================================
        # AFFICHAGE
        # =====================================================
    
        st.subheader("Évaluation du niveau de risque")
    
        st.warning(
            f"{message} "
            f"({round(incidence_finale, 2)} cas / 1000 habitants à risque)"
        )
    
        st.caption(
            "Projet de science des données appliquées - Emile Nibasumba"
        )

afficher_application()
