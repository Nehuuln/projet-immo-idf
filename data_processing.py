"""
data_processing.py
Nettoyage des données DVF et calcul du prix au m² par commune.
"""

import pandas as pd

# Types de biens
TYPES_BIENS = ["Appartement", "Maison"]

# Seuils de prix au m² pour éliminer les grosses valeurs
PRIX_M2_MIN = 500
PRIX_M2_MAX = 30_000

NB_TRANSACTIONS_MIN = 3


def clean_and_aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie les données brutes DVF et calcule le prix moyen au m²
    par commune (code postal).

    Étapes :
    1. Filtrer sur les appartements et maisons
    2. Convertir et nettoyer les colonnes numériques
    3. Supprimer les lignes incomplètes ou aberrantes
    4. Calculer le prix au m²
    5. Agréger par commune
    """

    # 1. Filtrer les types de biens
    df = df[df["Type local"].isin(TYPES_BIENS)].copy()

    # 2. Convertir la valeur foncière
    df["Valeur fonciere"] = (
        df["Valeur fonciere"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )
    df["Valeur fonciere"] = pd.to_numeric(df["Valeur fonciere"], errors="coerce")

    # 3. Convertir la surface
    df["Surface reelle bati"] = pd.to_numeric(df["Surface reelle bati"], errors="coerce")

    # 4. Supprimer les lignes avec valeurs manquantes essentielles
    df = df.dropna(subset=["Valeur fonciere", "Surface reelle bati", "Code postal"])

    # 5. Supprimer les surfaces nulles ou négatives
    df = df[df["Surface reelle bati"] > 0]

    # 6. Calculer le prix au m²
    df["prix_m2"] = df["Valeur fonciere"] / df["Surface reelle bati"]

    # 7. Éliminer les valeurs aberrantes
    df = df[(df["prix_m2"] >= PRIX_M2_MIN) & (df["prix_m2"] <= PRIX_M2_MAX)]

    # 8. Normaliser le code postal
    df["Code postal"] = df["Code postal"].astype(str).str[:5]

    # 9. Agréger par commune
    df_agg = (
        df.groupby(["Code postal", "Commune", "Code departement"])
        .agg(
            prix_m2_moyen=("prix_m2", "mean"),
            prix_m2_median=("prix_m2", "median"),
            nb_transactions=("prix_m2", "count"),
        )
        .reset_index()
    )

    # 10. Garder uniquement les communes avec assez de transactions
    df_agg = df_agg[df_agg["nb_transactions"] >= NB_TRANSACTIONS_MIN]

    # 11. Arrondir les prix
    df_agg["prix_m2_moyen"] = df_agg["prix_m2_moyen"].round(0)
    df_agg["prix_m2_median"] = df_agg["prix_m2_median"].round(0)

    return df_agg.reset_index(drop=True)


def stats_par_departement(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les statistiques de prix au m² par département.
    """
    stats = (
        df.groupby("Code departement")
        .agg(
            prix_m2_moyen=("prix_m2_moyen", "mean"),
            prix_m2_median=("prix_m2_median", "median"),
            nb_communes=("Code postal", "count"),
            nb_transactions=("nb_transactions", "sum"),
        )
        .reset_index()
        .sort_values("prix_m2_moyen", ascending=False)
    )
    stats["prix_m2_moyen"] = stats["prix_m2_moyen"].round(0)
    return stats
