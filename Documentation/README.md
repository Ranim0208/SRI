# 🎯 Phase 1: Construction de la Collection de Test - Système de Recherche d'Information

## 📌 Vue d'ensemble

Ce projet implémente la **Phase 1** du projet SRI (Systèmes de Recherche d'Information) de l'ISAMM.

**Thème**: Construction d'une collection de test (corpus de tweets + requêtes + jugements de pertinence) sur le thème **"Guerre en Iran"** en utilisant **Playwright** pour le web scraping.

---

## 📦 Contenu du Package

```
phase1/
├── phase1_collector.py          # 🎬 Script principal - Collecte de tweets
├── phase1_validator.py          # ✅ Validateur de données
├── phase1_converter.py          # 🔄 Convertisseur de formats
├── GUIDE_PHASE1.md             # 📖 Guide complet d'utilisation
├── requirements.txt             # 📦 Dépendances Python
└── phase1_output/              # 📁 Dossier de sortie
    ├── tweets.json             # Corpus de 500 tweets
    ├── topics.json             # 5 requêtes
    ├── qrels.txt              # Jugements de pertinence
    └── rapport_phase1.txt     # Rapport d'exécution
```

---

## 🚀 Quick Start

### 1️⃣ Installation
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2️⃣ Lancer la collecte
```bash
python3 phase1_collector.py
```

### 3️⃣ Valider les données
```bash
python3 phase1_validator.py
```

### 4️⃣ Exporter les formats
```bash
python3 phase1_converter.py
```

---

## 📄 Fichiers Générés

### 1. **tweets.json** - Corpus de tweets
```json
{
  "id": "1234567890",
  "query_id": "MB01",
  "timestamp": "2024-04-18T14:23:45Z",
  "user": "user123",
  "text": "Content about Iran war...",
  "lang": "en",
  "retweets": 5,
  "likes": 10
}
```

### 2. **topics.json** - Requêtes TREC
```json
{
  "num": "MB01",
  "title": "regime change Iran"
}
```

### 3. **qrels.txt** - Jugements de pertinence
```
MB01 0 1234567890 1    # Pertinent (top 30)
MB01 0 1234567891 0    # Non pertinent
```

### 4. **rapport_phase1.txt** - Rapport d'exécution

---

## 🔍 Architecture

### Classe `IranWarTweetCollector`

```python
# Initialisation
collector = IranWarTweetCollector(output_dir="phase1_output")

# Méthodes principales
await collector.collect_all_tweets()     # Collecte
collector.save_tweets_json()             # Sauvegarde tweets
collector.save_queries()                 # Sauvegarde requêtes
collector.generate_qrels()               # Génère jugements
collector.generate_report()              # Génère rapport
```

### Classe `Phase1Validator`

```python
# Initialisation
validator = Phase1Validator(output_dir="phase1_output")

# Validation complète
validator.run_full_validation()

# Ou validations individuelles
validator.load_files()
validator.validate_structure()
validator.check_duplicates()
validator.check_consistency()
validator.generate_statistics()
```

### Classe `FormatConverter`

```python
# Conversions disponibles
FormatConverter.json_to_xml_topics(input, output)
FormatConverter.json_to_csv_tweets(input, output)
FormatConverter.qrels_to_json(input, output)

# Bundle complet
create_export_bundle(input_dir, output_dir)
```

---

## 📊 Statistiques Attendues

| Métrique | Valeur |
|----------|--------|
| **Requêtes** | 5 |
| **Tweets par requête** | 100 |
| **Total tweets** | 500 |
| **Tweets pertinents** | 150 (30 × 5 requêtes) |
| **Tweets non pertinents** | 350 (70 × 5 requêtes) |
| **Jugements totaux** | 500 |

---

## 🎯 Requêtes Utilisées

| ID | Requête | Thème |
|---|---------|-------|
| **MB01** | regime change Iran | Changement de régime |
| **MB02** | regime collapse | Effondrement du régime |
| **MB03** | Closing Hormuz strait | Détroit d'Hormuz |
| **MB04** | Intercepting missiles drones | Défense aérienne |
| **MB05** | revolutionary guard Iran | Garde révolutionnaire |

---

## ⚙️ Configuration

### Modifier les requêtes
```python
self.queries = [
    {"num": "MB01", "title": "custom query"},
    ...
]
```

### Modifier les nombres
```python
self.tweets_per_query = 100      # Tweets par requête
self.relevant_count = 30         # Tweets pertinents
```

### Modifier le dossier de sortie
```python
collector = IranWarTweetCollector(output_dir="mon_dossier")
```

---

## 🐛 Dépannage

| Problème | Solution |
|----------|----------|
| Playwright non installé | `pip install playwright` |
| Navigateur manquant | `playwright install chromium` |
| X.com ne charge pas | Vérifier connexion, augmenter timeout |
| Trop peu de tweets | Requête moins populaire, augmenter délai |
| Erreur CORS/Script | Vérifier sélecteurs CSS dans le code |

---

## 📋 Checklist Avant Remise

- [ ] Scripts exécutés sans erreur
- [ ] Dossier `phase1_output/` créé
- [ ] 4 fichiers présents:
  - [ ] `tweets.json` (500 tweets)
  - [ ] `topics.json` (5 requêtes)
  - [ ] `qrels.txt` (500 jugements)
  - [ ] `rapport_phase1.txt`
- [ ] Validation exécutée avec succès
- [ ] Statistiques vérifiées
- [ ] Pas de doublons
- [ ] Cohérence des données confirmée
- [ ] Dossier compressé: `2ing1-Groupe01.zip` (exemple)
- [ ] Partagé sur Google Drive avec `chiraz.latiri@isamm.uma.tn`
- [ ] **Date limite: 18 avril 2026**

---

## 📚 Ressources

- **PyPlaywright**: https://playwright.dev/python/
- **Format TREC**: https://pages.nist.gov/trec-browser/
- **TREC Microblog**: https://pages.nist.gov/trec-browser/trec20/microblog/
- **Énoncé complet**: `Enonce_projet_Ing2-2026.pdf`

---

## 👥 Contributions

Ce package a été créé pour le projet SRI 2ème année IMD 2025-2026.

---

## 📝 Notes Importantes

1. **Conformité TREC**: Les fichiers générés suivent le format TREC standard
2. **Authentification X**: Playwright simule un navigateur réel pour éviter les blocages
3. **Délais**: Des délais sont inclus entre les requêtes pour ne pas surcharger les serveurs
4. **Doublons**: Implémentation automatique de vérification de doublons

---

## 🎓 Phases du Projet

- **Phase 1** ✅ (Ce document): Construction de la collection
  - Deadline: 18 avril 2026
  
- **Phase 2**: Indexation et recherche
  - Deadline: 2 mai 2026
  
- **Phase 3**: Présentation orale
  - Dates: 4-6 mai 2026

---

**Bonne chance pour votre projet! 🚀**

Pour toute question, consultez `GUIDE_PHASE1.md` ou les fichiers source.
