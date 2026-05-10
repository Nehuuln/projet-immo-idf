"""
Analyse des prix de l'immobilier en Île-de-France
Source : Demandes de Valeurs Foncières (DVF) - data.gouv.fr
"""

from data_loader import load_and_filter_dvf
from data_processing import clean_and_aggregate
from geocoding import add_coordinates
from visualisation import generate_map

print("Chargement des données DVF...")
df_raw = load_and_filter_dvf("data/ValeursFoncieres-2025.txt")
print(f"   {len(df_raw):,} lignes conservées (Île-de-France)")

print("\nNettoyage et calcul du prix au m²...")
df_agg = clean_and_aggregate(df_raw)
print(f"   {len(df_agg):,} communes avec transactions valides")

print("\nAjout des coordonnées géographiques...")
df_geo = add_coordinates(df_agg)
print(f"   {len(df_geo):,} communes géocodées")

print("\nGénération de la carte interactive...")
generate_map(df_geo, output_path="map/carte_immobilier_idf.html")
print("\nCarte générée : map/carte_immobilier_idf.html")
