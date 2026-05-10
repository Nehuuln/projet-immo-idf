"""
visualisation.py
Génération de la carte interactive Folium des prix immobiliers en IDF.
"""

import pandas as pd
import folium
import branca.colormap as cm

from data_processing import stats_par_departement

# Labels pour les départements
DEPT_LABELS = {
    '75': 'Paris (75)',
    '77': 'Seine-et-Marne (77)',
    '78': 'Yvelines (78)',
    '91': 'Essonne (91)',
    '92': 'Hauts-de-Seine (92)',
    '93': 'Seine-Saint-Denis (93)',
    '94': 'Val-de-Marne (94)',
    '95': "Val-d'Oise (95)",
}


def _build_colormap(df: pd.DataFrame) -> cm.LinearColormap:
    """Construit la colormap de prix (vert → jaune → orange → rouge → violet)."""
    return cm.LinearColormap(
        colors=['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c', '#8e44ad'],
        vmin=df["prix_m2_moyen"].quantile(0.05),
        vmax=df["prix_m2_moyen"].quantile(0.95),
        caption='Prix moyen au m² (€)',
    )


def _popup_html(row: pd.Series, color: str) -> str:
    """Génère le HTML du popup pour une commune."""
    return f"""
    <div style="font-family: Arial, sans-serif; min-width: 175px;">
        <b style="font-size:14px">{row['Commune']}</b><br>
        <span style="color:#666; font-size:11px">
            Code postal : {row['Code postal']} &nbsp;|&nbsp;
            Dép. {row['Code departement']}
        </span>
        <hr style="margin: 5px 0; border-color: #eee;">
        <span style="font-size:18px; color:{color}">
            <b>{row['prix_m2_moyen']:,.0f} €/m²</b>
        </span><br>
        <span style="color:#555; font-size:12px">
            Médiane : {row['prix_m2_median']:,.0f} €/m²
        </span><br>
        <span style="color:#999; font-size:11px; margin-top:3px; display:block">
            {int(row['nb_transactions'])} transactions analysées
        </span>
    </div>
    """


def _title_html() -> str:
    """HTML du bandeau titre de la carte."""
    return """
    <div style="
        position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
        z-index: 1000; background: white; padding: 10px 22px;
        border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.18);
        font-family: Arial, sans-serif; text-align: center;">
        <b style="font-size:16px">🏠 Prix de l'immobilier en Île-de-France — 2025</b><br>
        <span style="font-size:11px; color:#777">
            Source : Demandes de Valeurs Foncières (DVF) · data.gouv.fr<br>
            Cliquez sur un cercle pour les détails · Taille = nombre de transactions
        </span>
    </div>
    """


def _stats_html(df: pd.DataFrame) -> str:
    """HTML du panneau de statistiques par département."""
    stats = stats_par_departement(df)
    rows = ""
    for _, r in stats.iterrows():
        dept_label = DEPT_LABELS.get(str(r["Code departement"]), r["Code departement"])
        rows += f"""
        <tr>
            <td style="padding: 2px 6px;">{dept_label}</td>
            <td style="padding: 2px 6px; text-align:right">
                <b>{r['prix_m2_moyen']:,.0f} €/m²</b>
            </td>
            <td style="padding: 2px 6px; text-align:right; color:#999; font-size:10px">
                {int(r['nb_transactions']):,} ventes
            </td>
        </tr>
        """

    total_transactions = int(df["nb_transactions"].sum())
    total_communes = len(df)

    return f"""
    <div style="
        position: fixed; bottom: 30px; left: 15px; z-index: 1000;
        background: white; padding: 12px 16px; border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
        font-family: Arial, sans-serif; font-size: 12px; min-width: 300px;">
        <b style="font-size:13px">📊 Prix moyen par département</b>
        <table style="width:100%; margin-top:6px; border-collapse:collapse;">
            {rows}
        </table>
        <div style="margin-top:8px; color:#aaa; font-size:10px; border-top:1px solid #eee; padding-top:6px;">
            {total_communes} communes · {total_transactions:,} transactions au total
        </div>
    </div>
    """


def generate_map(df: pd.DataFrame, output_path: str = "output/carte_immobilier_idf.html") -> None:
    """
    Génère la carte Folium interactive et la sauvegarde en HTML.

    Chaque commune est représentée par un cercle :
    - Couleur  → prix au m² (vert = pas cher, violet = très cher)
    - Taille   → nombre de transactions (plus c'est gros, plus c'est représentatif)
    - Popup    → détails au clic (prix moyen, médiane, nb transactions)
    - Tooltip  → résumé au survol

    Args:
        df:          DataFrame avec lat, lon, prix_m2_moyen, etc.
        output_path: Chemin de sortie du fichier HTML
    """
    colormap = _build_colormap(df)

    # Carte de base
    m = folium.Map(
        location=[48.85, 2.35],
        zoom_start=10,
        tiles='CartoDB positron',
    )

    for _, row in df.iterrows():
        prix  = row["prix_m2_moyen"]
        color = colormap(min(max(prix, colormap.vmin), colormap.vmax))

        radius = max(4, min(15, row["nb_transactions"] / 40))

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.72,
            weight=1,
            popup=folium.Popup(_popup_html(row, color), max_width=240),
            tooltip=f"{row['Commune']} — {prix:,.0f} €/m²",
        ).add_to(m)

    colormap.add_to(m)

    m.get_root().html.add_child(folium.Element(_title_html()))
    m.get_root().html.add_child(folium.Element(_stats_html(df)))

    m.save(output_path)
