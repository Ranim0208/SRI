# 📋 Phase 1: Construction de la Collection de Test - Guide Complet

## 🎯 Objectif
Collecter des tweets sur le thème **"Guerre en Iran"** en utilisant **Playwright** (web scraping automatisé) pour construire:
1. **Corpus de tweets** (tweets.json)
2. **Requêtes** (topics.json)
3. **Jugements de pertinence** (qrels.txt)

---

## 📦 Installation

### Étape 1: Installer Python 
```bash
python3 --version  # Vérifier que Python 3.8+ est installé
```

### Étape 2: Créer un environnement virtuel (optionnel mais recommandé)
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Linux/macOS
# ou sur Windows:
venv\Scripts\activate
```

### Étape 3: Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 4: Installer les navigateurs Playwright
```bash
playwright install chromium
```

---

## 🚀 Utilisation

### Exécuter le script principal
```bash
python3 phase1_collector.py
```

Le script va:
1. ✅ Lancer un navigateur Chromium (vous verrez la fenêtre du navigateur)
2. ✅ Naviguer sur X (Twitter)
3. ✅ Chercher chaque requête
4. ✅ Scraper les 100 premiers tweets
5. ✅ Générer 4 fichiers de sortie

---

## 📄 Formats des Fichiers Générés

### 1️⃣ tweets.json
Contient tous les tweets collectés au format JSON:

```json
[
  {
    "id": "1234567890",
    "query_id": "MB01",
    "timestamp": "2024-04-18T14:23:45Z",
    "user": "User123",
    "text": "Tweet content about Iran war...",
    "lang": "en",
    "retweets": 5,
    "likes": 10
  },
  ...
]
```

### 2️⃣ topics.json
Contient les 5 requêtes au format JSON TREC:

```json
[
  {
    "num": "MB01",
    "title": "regime change Iran"
  },
  {
    "num": "MB02",
    "title": "regime collapse"
  },
  ...
]
```

### 3️⃣ qrels.txt
Contient les jugements de pertinence au format TREC standard:

```
MB01 0 1234567890 1
MB01 0 1234567891 1
MB01 0 1234567892 1
...
MB01 0 1234567999 0
MB02 0 5678901234 1
...
```

**Format**: `<query_id> 0 <tweet_id> <relevance>`
- `query_id`: MB01, MB02, ...
- `0`: Champ fixe (standard TREC)
- `tweet_id`: ID du tweet
- `relevance`: **1** (pertinent - 30 premiers tweets) ou **0** (non pertinent)

### 4️⃣ rapport_phase1.txt
Rapport récapitulatif avec statistiques.

---

## 🔍 Requêtes Utilisées (Phase 1)

| ID | Requête | Thème |
|----|---------|-------|
| MB01 | regime change Iran | Changement de régime |
| MB02 | regime collapse | Effondrement du régime |
| MB03 | Closing Hormuz strait | Fermeture du détroit d'Hormuz |
| MB04 | Intercepting missiles drones | Interception de missiles |
| MB05 | revolutionary guard Iran | Garde révolutionnaire |

---


## 📊 Structure du Dossier de Sortie

```
phase1_output/
├── tweets.json          # Corpus de tweets
├── topics.json          # Requêtes
├── qrels.txt           # Jugements de pertinence
└── rapport_phase1.txt  # Rapport d'exécution
```

---