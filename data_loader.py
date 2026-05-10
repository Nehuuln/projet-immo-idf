"""
data_loader.py
Chargement et filtrage du fichier DVF pour l'Île-de-France.
"""

import pandas as pd

# Départements Île-de-France
IDF_DEPARTEMENTS = ['75', '77', '78', '91', '92', '93', '94', '95']

# Colonnes utiles à charger du fichier DVF
COLONNES_UTILES = [
    'Date mutation',
    'Nature mutation',
    'Valeur fonciere',
    'Code postal',
    'Commune',
    'Code departement',
    'Type local',
    'Surface reelle bati',
    'Nombre pieces principales',
]


def load_and_filter_dvf(filepath: str) -> pd.DataFrame:
    """
    Charge le fichier DVF par chunks pour économiser la mémoire,
    puis filtre sur l'Île-de-France et les ventes uniquement.
    """
    chunks = []

    for chunk in pd.read_csv(
        filepath,
        sep="|",
        low_memory=False,
        chunksize=100_000,
        usecols=lambda c: c in COLONNES_UTILES
    ):
        chunk["Code departement"] = chunk["Code departement"].astype(str).str.strip()

        # Garder uniquement l'IDF et les ventes
        mask = (
            chunk["Code departement"].isin(IDF_DEPARTEMENTS) &
            (chunk["Nature mutation"] == "Vente")
        )
        chunks.append(chunk[mask])

    df = pd.concat(chunks, ignore_index=True)
    return df
