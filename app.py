import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  
from datetime import datetime
import plotly.express as px
import os 


# Logo centré
col1, col2, col3 = st.columns([1.5, 2, 1])
with col2:
    st.image("logo.png", width=200)

st.markdown(
    """<style>
    h1 {
        font-family: "calibri", serif;
        color: #f7dc6f;
        text-align: center;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Fichiers
matrice_path = "matrice.xlsx"
historique_path = "historique_adherents.xlsx"
#df_Recompenses = pd.read_excel("matricecons.xlsx")
Recompense_path = "matricecons.xlsx"


#df_Recompenses = pd.read_excel("matricecons.ods", engine="odf")


#matrice
df_matrice = pd.read_excel(matrice_path, sheet_name="Feuil2")
df_matrice.columns = df_matrice.columns.str.strip()
#df_Recompenses = pd.read_excel(Recompense_path)
df_Recompenses = pd.read_excel(Recompense_path)
options = dict(zip(df_Recompenses["Recompense"], df_Recompenses["Coût en points"]))


# Créer historique if not
if not os.path.exists(historique_path):
    pd.DataFrame(columns=["Date", "Nom", "Activité", "Abonnement", "Fréquence", "Situation", "Points", "Points restants"]).to_excel(historique_path, index=False)

# side bar
#page = st.sidebar.selectbox("📋 Menu", ["Ajouter des points", "Historique des adhérents"])
#page = st.sidebar.selectbox("📋 Menu", ["Ajouter des points", "Historique des adhérents", "Consommer des points"])
#page = st.sidebar.selectbox("📋 Menu", ["Ajouter des points", "Historique des adhérents", "Consommer des points", "📈 Tableau de bord"])
st.sidebar.title("📋 Menu")
page = st.sidebar.selectbox("📋 Menu", [ "Ajouter des points", "Historique des adhérents", "Consommer des points", "📈 Tableau de bord"])


if page == "Ajouter des points":
    st.title("Attribution de Points")
    nom = st.text_input("Nom de l'adhérent")
    points = 0
    situation = None
    points_restants = 0

    Activité_options = ["-- Sélectionner --"] + sorted(df_matrice["Activité"].dropna().unique())
    Activité = st.selectbox("Activité", Activité_options)

    if Activité != "-- Sélectionner --":
        df_Activité = df_matrice[df_matrice["Activité"] == Activité]
        abonnement_options = ["-- Sélectionner --"] + sorted(df_Activité["Abonnement"].dropna().unique())
        abonnement = st.selectbox("Abonnement", abonnement_options)

        if abonnement != "-- Sélectionner --":
            df_abonnement = df_Activité[df_Activité["Abonnement"] == abonnement]

            # Gérer la fréquence seulement si elle existe
            freqs = df_abonnement["frequence"].dropna().unique()
            if len([f for f in freqs if str(f).strip()]) > 0:
                frequence_options = ["-- Sélectionner --"] + sorted([f for f in freqs if str(f).strip()])
                frequence = st.selectbox("Fréquence", frequence_options)
            else:
                frequence = None

            if frequence is None or frequence != "-- Sélectionner --":
                df_frequence = df_abonnement if frequence is None else df_abonnement[df_abonnement["frequence"] == frequence]

                # Gérer la situation seulement si elle existe
                situations = df_frequence["Situation"].dropna().unique()
                if len([s for s in situations if str(s).strip()]) > 0:
                    situation_options = ["-- Sélectionner --"] + sorted([s for s in situations if str(s).strip()])
                    situation = st.selectbox("Situation", situation_options)
                else:
                    situation = None

                if situation is None or situation != "-- Sélectionner --":
                    match = df_frequence if situation is None else df_frequence[df_frequence["Situation"] == situation]

                    if not match.empty:
                        points = int(match.iloc[0]["Points"])
                    #    points_restants = st.number_input("➕ Points restants de l'adhérent", min_value=0, step=1)

                    #    if situation is None or situation.lower() != "interruption":
                    #        points += points_restants
                    #    else:
                    #        points_restants = 0

                        st.success(f"✅ {points} points seront attribués à {nom}.")
                    #else:
                    #    st.warning("⚠️ Aucune correspondance trouvée dans la matrice.")


    # Bouton de validation
    if st.button("Attribuer les points"):
        if (
            nom and
            Activité != "-- Sélectionner --" and
            abonnement != "-- Sélectionner --" and
            frequence != "-- Sélectionner --" and
            situation != "-- Sélectionner --"
        ):
            nouvelle_entree = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Nom": nom,
                "Activité": Activité,
                "Abonnement": abonnement,
                "Fréquence": frequence,
                "Situation": situation,
                "Points": points,
                "Points restants": points_restants
            }])
            historique_df = pd.read_excel(historique_path)
            historique_df = pd.concat([historique_df, nouvelle_entree], ignore_index=True)
            historique_df.to_excel(historique_path, index=False)
            st.success("👍 Points enregistrés avec succès !")
        else:
            st.error("❌ Merci de remplir tous les champs avant de valider.")

elif page == "Historique des adhérents":
    st.title("🕓 Historique des Points")
    historique_df = pd.read_excel(historique_path)

    # date
    historique_df["Date"] = pd.to_datetime(historique_df["Date"], errors='coerce')

    # Filtres
    nom_filtre = st.text_input("🔍 Filtrer par nom")
    Activité_filtre = st.selectbox("🏋️ Filtrer par Activité", ["Tous"] + sorted(historique_df["Activité"].dropna().unique()))

    # cal
    min_date = historique_df["Date"].min().date() if not historique_df["Date"].isna().all() else datetime.today().date()
    max_date = historique_df["Date"].max().date() if not historique_df["Date"].isna().all() else datetime.today().date()

    date_filtre = st.date_input(
        "📅 Filtrer par date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    filtré = historique_df.copy()

    if nom_filtre:
        filtré = filtré[filtré["Nom"].str.contains(nom_filtre, case=False, na=False)]
    if Activité_filtre != "Tous":
        filtré = filtré[filtré["Activité"] == Activité_filtre]

    if isinstance(date_filtre, tuple) and len(date_filtre) == 2:
        start_date, end_date = date_filtre
        filtré = filtré[(filtré["Date"].dt.date >= start_date) & (filtré["Date"].dt.date <= end_date)]

    st.dataframe(filtré, use_container_width=True)

    # Bouton de téléchargement
    with open(historique_path, "rb") as f:
        st.download_button(
            label="📥 Télécharger l'historique (.xlsx)",
            data=f,
            file_name="historique_adherents.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif page == "Consommer des points":
    st.title("💳 Consommation de Points")

    historique_df = pd.read_excel(historique_path)
    historique_df["Date"] = pd.to_datetime(historique_df["Date"], errors='coerce')

    noms = sorted(historique_df["Nom"].dropna().unique())
    nom_choisi = st.selectbox("👤 Sélectionner un adhérent", ["-- Sélectionner --"] + list(noms))

    if nom_choisi != "-- Sélectionner --":
        adherent_data = historique_df[historique_df["Nom"] == nom_choisi]
        total_points = adherent_data["Points"].sum()
        total_consommes = adherent_data.get("Points consommes", pd.Series([0]*len(adherent_data))).sum()
        solde = total_points - total_consommes

        st.info(f"💰 Solde actuel : **{solde} points**")

        try:
            df_Recompenses = pd.read_excel(Recompense_path)
            options = dict(zip(df_Recompenses["Recompense"], df_Recompenses["Coût en points"]))
        except Exception as e:
            st.error(f"Erreur lors de la lecture des Recompenses : {e}")
            options = {}

        if options:
            choix = st.selectbox("🎁 Choisir une Recompense", ["-- Sélectionner --"] + list(options.keys()))
            if choix != "-- Sélectionner --":
                coût = options[choix]
                if coût > solde:
                    st.error("❌ Solde insuffisant pour cette Recompense.")
                else:
                    if st.button("✅ Confirmer la consommation"):
                        nouvelle_ligne = {
                            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Nom": nom_choisi,
                            "Activité": "Recompense",
                            "Abonnement": "",
                            "Fréquence": "",
                            "Situation": "Consommation",
                            "Points": 0,
                            "Points restants": solde - coût,
                            "Recompense": choix,
                            "Points consommes": coût
                        }

                        for col in ["Recompense", "Points consommes"]:
                            if col not in historique_df.columns:
                                historique_df[col] = None

                        historique_df = pd.concat([historique_df, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
                        historique_df.to_excel(historique_path, index=False)

                        st.success(f"🎉 {choix} attribué à {nom_choisi}. Nouveau solde : {solde - coût} points.")







elif page == "📈 Tableau de bord":
    st.title("📊 Tableau de Bord des Adhérents")
    if st.button("🔄 Recharger les données"):
        st.experimental_rerun()


    def load_data():
        historique_path = "historique_adherents.xlsx"
        if not os.path.exists(historique_path):
            st.error(f"Fichier introuvable : {historique_path}")
            return pd.DataFrame()
        df = pd.read_excel(historique_path)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        return df

    df = load_data()
    if df.empty:
        st.stop()

    # Statistiques globales
    st.subheader("Statistiques Globales")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nombre d'adhérents uniques", df['Nom'].nunique())
    col2.metric("Total Points Attribués", int(df['Points'].sum()))
    col3.metric("Total Points Consommés", int(df['Points consommes'].sum()))
    solde = df['Points'] - df['Points consommes']
    #col4.metric("Solde Moyen", f"{solde.mean():.2f}" if not solde.empty else "0")

    # Filtres
    st.sidebar.header("Filtres Tableau de bord")
    noms = st.sidebar.multiselect("Filtrer par nom", options=sorted(df['Nom'].unique()), default=sorted(df['Nom'].unique()))
    date_min = st.sidebar.date_input("Date min", df['Date'].min().date())
    date_max = st.sidebar.date_input("Date max", df['Date'].max().date())

    # Application des filtres
    mask = (
        df['Nom'].isin(noms) &
        (df['Date'] >= pd.to_datetime(date_min)) &
        (df['Date'] <= pd.to_datetime(date_max))
    )
    df_filtered = df[mask]

     # Graphique : répartition des récompenses
    st.subheader("🎁 Répartition des Récompenses")
    fig_pie = px.pie(df_filtered[df_filtered['Recompense'].notna()], names='Recompense', title='Répartition des Récompenses', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)
    # Graphique : évolution des points dans le temps
    st.subheader("📈 Évolution des Points dans le Temps")

    evolution_df = df_filtered.copy()
    evolution_df['Attribués'] = evolution_df['Points']
    evolution_df['Consommés'] = evolution_df['Points consommes']

    evolution_summary = evolution_df.groupby('Date')[['Attribués', 'Consommés']].sum().reset_index()
    fig_line = px.line(evolution_summary, x='Date', y=['Attribués', 'Consommés'], title='Évolution des Points Attribués et Consommés')
    fig_line.update_layout(yaxis_title="Points", xaxis_title="Date")
    st.plotly_chart(fig_line, use_container_width=True)


    

    # Top adhérents
    st.subheader("🏅 Top 10 Adhérents par Points Attribués")
    top_adherents = df_filtered.groupby('Nom')['Points'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_bar = px.bar(top_adherents, x='Nom', y='Points', title='Top 10 Adhérents', text='Points')
    fig_bar.update_traces(marker_color='indigo', textposition='outside')
    fig_bar.update_layout(xaxis_title="Nom", yaxis_title="Points", uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig_bar, use_container_width=True)

    # Podium
    st.subheader("🎖️ Podium - Top 3 Adhérents par Points Attribués")
    top3 = df_filtered.groupby("Nom")["Points"].sum().sort_values(ascending=False).head(3).reset_index()
    podium_icons = ["🥇", "🥈", "🥉"]
    for i, row in top3.iterrows():
        st.markdown(f"{podium_icons[i]} **{row['Nom']}** — {row['Points']} points")


    # Données tabulaires
    st.subheader("📋 Données Filtrées")
    st.dataframe(df_filtered.sort_values(by="Date", ascending=False), use_container_width=True)

    st.markdown("---")
    st.caption("Tableau de bord généré avec Streamlit © 2025")
