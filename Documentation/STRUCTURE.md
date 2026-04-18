# 📊 Structure du Projet Phase 1 - Vue d'ensemble

## 🗂️ Structure des Fichiers

```
phase1-project/
│
├── 📘 DOCUMENTATION
│   ├── README.md                    # Vue d'ensemble du projet
│   ├── GUIDE_PHASE1.md             # Guide complet d'utilisation
│   └── STRUCTURE.md                 # Ce fichier
│
├── 🐍 SCRIPTS PYTHON
│   ├── phase1_collector.py         # Collecte de tweets avec Playwright
│   ├── phase1_validator.py         # Validation des données
│   ├── phase1_converter.py         # Conversion de formats
│   └── config.py                   # Configuration personnalisable
│
├── ⚙️ INSTALLATION
│   ├── requirements.txt             # Dépendances Python
│   ├── install.sh                  # Script Linux/macOS
│   └── install.bat                 # Script Windows
│
└── 📁 SORTIE (Généré après exécution)
    └── phase1_output/
        ├── tweets.json             # Corpus de 500 tweets
        ├── topics.json             # 5 requêtes
        ├── qrels.txt              # Jugements de pertinence
        ├── rapport_phase1.txt     # Rapport d'exécution
        ├── validation_report.txt  # Rapport de validation
        └── exports/               # Formats additionnels
            ├── tweets.csv
            ├── topics.xml
            ├── qrels.json
            ├── query_summary.csv
            └── sample_tweets.txt
```

---

## 🔄 Flux d'Exécution

```
┌─────────────────────────────────────────────────────────┐
│           PHASE 1: CONSTRUCTION DE LA COLLECTION         │
└─────────────────────────────────────────────────────────┘

                        ┌──────────────┐
                        │  START       │
                        └──────┬───────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  INSTALLATION        │
                    │  - Python 3.8+       │
                    │  - Playwright        │
                    │  - Dépendances       │
                    └──────────┬───────────┘
                               │
                               ▼
        ┌──────────────────────────────────────────┐
        │  PHASE 1: COLLECTE DE TWEETS             │
        ├──────────────────────────────────────────┤
        │                                          │
        │  Pour chaque requête:                     │
        │  1. Accéder à X (Twitter)                │
        │  2. Chercher la requête                  │
        │  3. Scraper les tweets                   │
        │  4. Extraire les métadonnées             │
        │  5. Sauvegarder les données              │
        │                                          │
        │  Résultat: tweets.json (500 documents)  │
        │                                          │
        └──────────────┬──────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────┐
        │  GÉNÉRATION DES REQUÊTES                 │
        ├──────────────────────────────────────────┤
        │                                          │
        │  Créer le fichier topics.json            │
        │  avec les 5 requêtes définies            │
        │                                          │
        │  Résultat: topics.json (5 requêtes)     │
        │                                          │
        └──────────────┬──────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────┐
        │  GÉNÉRATION DES QRELS                    │
        ├──────────────────────────────────────────┤
        │                                          │
        │  Pour chaque requête:                     │
        │  - Les 30 premiers tweets = pertinent (1)│
        │  - Les 70 autres = non pertinent (0)     │
        │                                          │
        │  Résultat: qrels.txt (500 jugements)    │
        │                                          │
        └──────────────┬──────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────┐
        │  VALIDATION DES DONNÉES                  │
        ├──────────────────────────────────────────┤
        │                                          │
        │  ✓ Vérifier la structure                │
        │  ✓ Vérifier les doublons                │
        │  ✓ Vérifier la cohérence                │
        │  ✓ Générer les statistiques             │
        │                                          │
        │  Résultat: validation_report.txt        │
        │                                          │
        └──────────────┬──────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────┐
        │  CONVERSION DE FORMATS (OPTIONNEL)       │
        ├──────────────────────────────────────────┤
        │                                          │
        │  Générer:                                 │
        │  - tweets.csv                           │
        │  - topics.xml                           │
        │  - qrels.json                           │
        │  - query_summary.csv                    │
        │  - sample_tweets.txt                    │
        │                                          │
        │  Résultat: dossier exports/             │
        │                                          │
        └──────────────┬──────────────────────────┘
                       │
                       ▼
                    ┌──────────────┐
                    │  TERMINER    │
                    └──────────────┘
```

---

## 📋 Classe Principale: IranWarTweetCollector

### Architecture

```python
class IranWarTweetCollector:
    """
    Collecteur de tweets sur le thème Guerre en Iran
    
    Attributs:
        - queries: Liste des 5 requêtes
        - tweets_per_query: Nombre de tweets à collecter
        - relevant_count: Nombre de tweets pertinents
        - all_tweets: Liste de tous les tweets collectés
        - tweet_ids: Set d'IDs pour éviter les doublons
    
    Méthodes principales:
        - collect_all_tweets()      → Collecte tous les tweets
        - save_tweets_json()        → Sauvegarde tweets.json
        - save_queries()            → Sauvegarde topics.json
        - generate_qrels()          → Génère qrels.txt
        - generate_report()         → Crée le rapport
    """
```

### Flux interne

```
collect_all_tweets()
├── Pour chaque requête:
│   ├── collect_tweets_for_query()
│   │   ├── Lancer navigateur Playwright
│   │   ├── Accéder à X.com avec la recherche
│   │   ├── Boucle de scroll:
│   │   │   ├── Extraire les tweets visibles
│   │   │   ├── Parser chaque tweet
│   │   │   │   ├── _extract_tweet_data()
│   │   │   │   ├── Récupérer l'ID
│   │   │   │   ├── Récupérer le texte
│   │   │   │   ├── Récupérer l'utilisateur
│   │   │   │   ├── Récupérer le timestamp
│   │   │   │   └── Récupérer les stats
│   │   │   ├── Ajouter à all_tweets
│   │   │   └── Scroller pour plus de tweets
│   │   └── Fermer la page
│   └── Continuer requête suivante
│
├── save_tweets_json()
├── save_queries()
├── generate_qrels()
└── generate_report()
```

---

## 🔧 Classe Utilitaire: Phase1Validator

```python
class Phase1Validator:
    """
    Validateur de données Phase 1
    
    Méthodes:
        - load_files()              → Charger les fichiers
        - validate_structure()      → Vérifier la structure
        - check_duplicates()        → Déterminer les doublons
        - check_consistency()       → Vérifier la cohérence
        - generate_statistics()     → Générer des stats
        - run_full_validation()     → Validation complète
    """
```

---

## 🔄 Classe Convertisseur: FormatConverter

```python
class FormatConverter:
    """
    Convertisseur de formats
    
    Conversions statiques:
        - json_to_xml_topics()      → Topics: JSON → XML
        - json_to_csv_tweets()      → Tweets: JSON → CSV
        - qrels_to_json()           → Qrels: TXT → JSON
        - create_summary_csv()      → CSV récapitulatif
        - export_sample_tweets()    → Échantillon lisible
    
    Fonction globale:
        - create_export_bundle()    → Bundle complet
    """
```

---

## 📊 Format des Données

### tweets.json
```json
[
  {
    "id": "1234567890",              ← Identifiant unique
    "query_id": "MB01",              ← ID de la requête
    "timestamp": "2024-04-18T14:23Z", ← Date et heure
    "user": "user123",               ← Nom d'utilisateur
    "text": "Content...",             ← Contenu du tweet
    "lang": "en",                    ← Langue
    "retweets": 5,                   ← Nombre de retweets
    "likes": 10                      ← Nombre de likes
  }
]
```

### topics.json
```json
[
  {
    "num": "MB01",                   ← ID de la requête
    "title": "regime change Iran"    ← Texte de la requête
  }
]
```

### qrels.txt
```
MB01 0 1234567890 1   ← Query | Zero | TweetID | Pertinence
MB01 0 1234567891 0
MB02 0 5678901234 1
...
```

---

## 🎯 Requêtes (5 Total)

| ID   | Requête                    | Tweets | Pertinents | Non Pertinents |
|------|----------------------------|--------|-----------|----------------|
| MB01 | regime change Iran         | 100    | 30        | 70             |
| MB02 | regime collapse            | 100    | 30        | 70             |
| MB03 | Closing Hormuz strait      | 100    | 30        | 70             |
| MB04 | Intercepting missiles drones | 100  | 30        | 70             |
| MB05 | revolutionary guard Iran   | 100    | 30        | 70             |
| **TOTAL** | | **500** | **150** | **350** |

---

## 📈 Statistiques Attendues

```
Total tweets:           500
Tweets uniques:         500 (pas de doublons)
Requêtes:               5
Tweets par requête:     100
Jugements totaux:       500
  - Pertinents:        150 (30%)
  - Non pertinents:    350 (70%)
Langues:                Anglais
```

---

## ⚙️ Configuration

### Fichier config.py

```python
# Paramètres modifiables
THEME = "Guerre en Iran"
TWEETS_PER_QUERY = 100
RELEVANT_TWEETS_PER_QUERY = 30
HEADLESS_MODE = False
BROWSER_TYPE = "chromium"

QUERIES = [
    {"num": "MB01", "title": "regime change Iran"},
    # ... (5 requêtes)
]
```

---

## 🐛 Points Critiques

1. **Sélecteurs CSS**: Les sélecteurs pour extraire les éléments de X doivent être à jour
2. **Délais**: Des délais suffisants doivent être donnés pour que le contenu charge
3. **Authentification**: X peut bloquer les scraping → Playwright simule un navigateur réel
4. **Rate limiting**: Ne pas faire trop de requêtes trop vite
5. **Validation**: Vérifier les doublons entre requêtes

---

## 📝 Checklist d'Exécution

- [ ] Python 3.8+ installé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Playwright installé (`playwright install chromium`)
- [ ] Scripts téléchargés/copiés
- [ ] Connexion Internet vérifiée
- [ ] Lancer `phase1_collector.py`
- [ ] Vérifier la création du dossier `phase1_output/`
- [ ] Lancer `phase1_validator.py` pour valider
- [ ] Lancer `phase1_converter.py` pour exporter
- [ ] Tous les 4 fichiers présents
- [ ] Compresser le dossier
- [ ] Partager sur Google Drive avant le 18 avril 2026

---

**Fin de la documentation Phase 1** ✅
