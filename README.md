# Prix de l'immobilier en Île-de-France (2025)

Analyse et visualisation interactive des prix au m² en Île-de-France à partir des données officielles **Demandes de Valeurs Foncières (DVF)**.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-lightblue?logo=pandas)
![Folium](https://img.shields.io/badge/Folium-0.14+-green)
![Data](https://img.shields.io/badge/Source-data.gouv.fr-orange)

---

## 📊 Aperçu

La carte interactive affiche le **prix moyen au m²** de chaque commune d'Île-de-France :

- 🟢 **Vert** → prix bas
- 🟡 **Jaune** → prix moyen
- 🔴 **Rouge / Violet** → prix élevé
- **Taille du cercle** → proportionnelle au nombre de transactions (plus représentatif)
- **Clic sur un cercle** → prix moyen, médiane et nombre de transactions

---

## Structure du projet

```
projet_immo_idf/
│
├── main.py               # Point d'entrée
├── data_loader.py        # Chargement et filtrage du fichier DVF
├── data_processing.py    # Nettoyage, calcul du prix au m², agrégation par commune
├── geocoding.py          # Ajout des coordonnées GPS par code postal
├── visualisation.py      # Génération de la carte interactive (Folium)
│
├── data/
│   └── ValeursFoncieres-2025.txt   # Fichier source DVF
│
├── map/
│   └── carte_immobilier_idf.html   # Carte générée
│
├── requirements.txt
└── README.md
```

---

## Installation et utilisation

### 1. Cloner le dépôt

```bash
git clone https://github.com/<ton-username>/prix-immobilier-idf.git
cd prix-immobilier-idf
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Télécharger les données DVF

Télécharger le fichier **Demandes de Valeurs Foncières** sur :
→ [data.gouv.fr — DVF](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/)

Placer le fichier dans le dossier `data/` :
```
data/ValeursFoncieres-2025.txt
```

### 4. Créer le dossier de sortie

```bash
mkdir map
```

### 5. Lancer l'analyse

```bash
python main.py
```

### 6. Ouvrir la carte

```bash
open map/carte_immobilier_idf.html
```

---

## Pipeline de données

```
Fichier DVF brut (~3M lignes)
        │
        ▼
data_loader.py
  → Lecture par chunks pour optimiser la mémoire
  → Filtrage sur les 8 départements IDF (75, 77, 78, 91, 92, 93, 94, 95)
  → Conservation des ventes uniquement
        │
        ▼
data_processing.py
  → Filtrage : appartements et maisons uniquement
  → Conversion de la valeur foncière
  → Suppression des valeurs manquantes et aberrantes
  → Calcul du prix au m² = Valeur foncière / Surface réelle bâtie
  → Filtrage des outliers (500 €/m² < prix < 30 000 €/m²)
  → Agrégation par commune (moyenne, médiane, nb transactions)
        │
        ▼
geocoding.py
  → Association code postal → coordonnées GPS
  → Dictionnaire de ~200 codes postaux IDF connus
  → Fallback aléatoire dans la boîte englobante du département
        │
        ▼
visualisation.py
  → Carte Folium sur fond CartoDB Positron
  → Cercles colorés par prix (colormap 5 couleurs)
  → Popups interactifs au clic
  → Panneau de statistiques par département
  → Export HTML autonome
```

---

## Résultats

| Département | Prix moyen au m² |
|---|---|
| Paris (75) | ~11 000 – 15 000 €/m² |
| Hauts-de-Seine (92) | ~7 000 – 10 000 €/m² |
| Val-de-Marne (94) | ~5 000 – 7 000 €/m² |
| Seine-Saint-Denis (93) | ~4 000 – 6 000 €/m² |
| Grande couronne (77, 78, 91, 95) | ~3 000 – 5 000 €/m² |

---

## Source des données

- **Demandes de Valeurs Foncières (DVF)** — Ministère de l'Économie et des Finances
- Disponible sur [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/)

---
