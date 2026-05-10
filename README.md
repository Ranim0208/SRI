# Projet SRI — Système de Recherche d'Information

### ISAMM — Collecte, Indexation et Évaluation sur corpus Twitter

**Thème :** Guerre en Iran  
**Groupe :** Maycem Ben Lagha · Ryned Soua · Khouloud Hammadi · Mohamed El Mehdi Ben Taher · Ranim Ben Cheikh

---

## Structure du projet

```
SRI/
├── phase1_collector.py          # Scraping Playwright de X (Twitter)
├── phase1_validator.py          # Validation des données collectées
├── phase1_converter.py          # Export CSV / XML / JSON
├── phase2_indexer_v2.py         # Indexation PyTerrier (lexèmes, stems, lemmes)
├── phase2_retrieval.py          # Retrieval BM25, TF-IDF, PL2, DPH
├── phase2_evaluation.py         # Évaluation MAP, P@K, courbes R-P
├── requirements_phase2.txt      # Dépendances Python Phase 2
├── venv_sri/                    # Environnement virtuel Python 3.11
├── phase1_output/
│   ├── tweets.json              # 500 tweets collectés
│   ├── topics.json              # 5 requêtes TREC
│   ├── qrels.txt                # 500 jugements de pertinence
│   └── rapport_phase1.txt       # Rapport d'exécution Phase 1
└── phase2_output/
    ├── corpus_preprocessed.csv  # Corpus nettoyé + lemmatisé
    ├── indexes/
    │   ├── index_lexemes/       # Index PyTerrier — mots bruts
    │   ├── index_stems/         # Index PyTerrier — Porter stemmer
    │   └── index_lemmes/        # Index PyTerrier — lemmatisation spaCy
    ├── results/                 # 12 fichiers TREC (4 modèles × 3 index)
    ├── all_results.csv
    ├── evaluation_summary.csv   # Tableau MAP / P@1 / P@5 / P@10
    ├── rapport_phase2.txt       # Rapport narratif complet
    └── charts/                  # 6 courbes Rappel-Précision (PNG)
```

---

## Phase 1 — Construction de la collection de test

### Objectif

Construire un corpus de 500 tweets, 5 requêtes et les jugements de pertinence associés, au format TREC.

### Requêtes utilisées

| ID   | Requête                      | Thème                  |
| ---- | ---------------------------- | ---------------------- |
| MB01 | regime change Iran           | Changement de régime   |
| MB02 | regime collapse              | Effondrement du régime |
| MB03 | Closing Hormuz strait        | Détroit d'Hormuz       |
| MB04 | Intercepting missiles drones | Défense aérienne       |
| MB05 | revolutionary guard Iran     | Garde révolutionnaire  |

### Statistiques

| Métrique              | Valeur       |
| --------------------- | ------------ |
| Requêtes              | 5            |
| Tweets par requête    | 100          |
| Total tweets          | 500          |
| Tweets pertinents     | 150 (30 × 5) |
| Tweets non pertinents | 350          |
| Jugements totaux      | 500          |

### Format des fichiers

**tweets.json**

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

**topics.json**

```json
{ "num": "MB01", "title": "regime change Iran" }
```

**qrels.txt**

```
MB01 0 1234567890 1
MB01 0 1234567891 0
```

### Lancer la Phase 1

```bash
pip install -r requirements.txt
playwright install chromium

python phase1_collector.py    # Collecte des tweets
python phase1_validator.py    # Validation des données
python phase1_converter.py    # Export CSV / XML / JSON
```

---

## Phase 2 — Indexation, Retrieval et Évaluation

### Prérequis système

- **Python 3.11** (obligatoire — PyTerrier est incompatible avec Python 3.13)
- **Java JDK 11** (obligatoire pour PyTerrier)
- **Windows 10/11 64-bit**

---

### Étape 1 — Installer Python 3.11

PyTerrier ne fonctionne pas sur Python 3.13. Il faut Python 3.11.9 (dernière version avec installeur Windows).

Télécharge l'installeur : https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

Lance l'installeur et coche **"Add Python 3.11 to PATH"**.

Vérifie que les deux versions coexistent :

```powershell
py --list
# Doit afficher :
#  -V:3.13 *   Python 3.13 (64-bit)
#  -V:3.11     Python 3.11 (64-bit)
```

---

### Étape 2 — Installer Java JDK 11

PyTerrier utilise Java en interne. Sans JDK 11, il refuse de démarrer.

```powershell
winget install EclipseAdoptium.Temurin.11.JDK
```

Après installation, définis JAVA_HOME de façon permanente :

```powershell
[System.Environment]::SetEnvironmentVariable(
  "JAVA_HOME",
  "C:\Program Files\Eclipse Adoptium\jdk-11.0.31.11-hotspot",
  "User"
)
```

Ferme et réouvre PowerShell, puis vérifie :

```powershell
java -version
# Doit afficher : openjdk version "11.x.x" ...
```

---

### Étape 3 — Créer l'environnement virtuel Python 3.11

```powershell
cd C:\Users\hp\SRI
py -V:3.11 -m venv venv_sri
```

---

### Étape 4 — Activer le venv et installer les dépendances

À chaque nouvelle session PowerShell, active toujours le venv avant de travailler :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& C:\Users\hp\SRI\venv_sri\Scripts\Activate.ps1
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-11.0.31.11-hotspot"
```

Le prompt doit afficher `(venv_sri)` en préfixe.

Installe les dépendances (une seule fois) :

```powershell
pip install python-terrier spacy pandas numpy matplotlib
python -m spacy download en_core_web_sm
```

Vérifie que tout fonctionne :

```powershell
python -c "import pyterrier; import spacy; print('OK tout fonctionne')"
```

---

### Étape 5 — Créer les dossiers de sortie

```powershell
New-Item -ItemType Directory -Force "C:\Users\hp\SRI\phase2_output\indexes\index_lexemes"
New-Item -ItemType Directory -Force "C:\Users\hp\SRI\phase2_output\indexes\index_stems"
New-Item -ItemType Directory -Force "C:\Users\hp\SRI\phase2_output\indexes\index_lemmes"
```

---

### Étape 6 — Lancer les scripts Phase 2

Toujours dans le venv activé avec JAVA_HOME défini :

```powershell
# Tâche 2 — Indexation (3 index : lexèmes, stems, lemmes) (~3-5 min)
python phase2_indexer_v2.py

# Tâche 3 — Retrieval (4 modèles × 3 index = 12 runs) (~2 min)
python phase2_retrieval.py

# Tâche 4 — Évaluation (MAP, P@K, courbes R-P) (~1 min)
python phase2_evaluation.py
```

---

### Commande complète à copier-coller (session unique)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& C:\Users\hp\SRI\venv_sri\Scripts\Activate.ps1
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-11.0.31.11-hotspot"

python phase2_indexer_v2.py
python phase2_retrieval.py
python phase2_evaluation.py
```

---

### Résultats Phase 2

#### Index construits

| Index         | Traitement          | Termes distincts |
| ------------- | ------------------- | ---------------- |
| index_lexemes | Mots bruts          | ~2090            |
| index_stems   | Porter stemmer      | ~2090            |
| index_lemmes  | Lemmatisation spaCy | ~1898            |

#### Modèles de retrieval testés

| Modèle | Type                             |
| ------ | -------------------------------- |
| BM25   | Probabiliste (Okapi)             |
| TF-IDF | Vectoriel classique              |
| PL2    | Divergence from Randomness       |
| DPH    | Divergence from Randomness (DFR) |

#### Résultats d'évaluation (extrait)

| Run            | MAP    | P@1  | P@5  | P@10 |
| -------------- | ------ | ---- | ---- | ---- |
| PL2_stems      | 0.1868 | 0.80 | 0.40 | 0.46 |
| DPH_lexemes    | 0.1849 | 0.80 | 0.48 | 0.46 |
| TF_IDF_lexemes | 0.1842 | 0.80 | 0.40 | 0.46 |
| BM25_lemmes    | 0.1506 | 0.60 | 0.32 | 0.32 |

**Observation :** Les modèles PL2 et DPH (Divergence from Randomness) surpassent BM25 sur cette collection. La lemmatisation ne dégrade pas systématiquement les résultats mais réduit le vocabulaire (~10%).

---

## Dépannage

### `Exception: Unable to find JAVA_HOME`

Java n'est pas visible par Python. Définis JAVA_HOME dans la session :

```powershell
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-11.0.31.11-hotspot"
```

Pour le rendre permanent : voir Étape 2.

### `No module named spacy` dans le venv

spaCy a été installé dans le mauvais Python. Vérifie que le venv est activé (`(venv_sri)` visible), puis :

```powershell
pip install spacy
python -m spacy download en_core_web_sm
```

### `ContentTooShortError` lors du téléchargement des JARs Terrier

Connexion interrompue. Supprime le cache et relance :

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.pyterrier"
python phase2_indexer_v2.py
```

Si le problème persiste, télécharge le JAR manuellement depuis :
`https://repo1.maven.org/maven2/org/terrier/terrier-assemblies/5.11/terrier-assemblies-5.11-jar-with-dependencies.jar`
et place-le dans `C:\Users\hp\.pyterrier\`.

### `NoClassDefFoundError: org/terrier/indexing/Collection`

JARs Terrier corrompus. Supprime le cache :

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.pyterrier"
```

---

## Technologies utilisées

| Outil          | Usage                                  |
| -------------- | -------------------------------------- |
| Playwright     | Web scraping de X (Twitter)            |
| PyTerrier 0.11 | Indexation et retrieval (Terrier 5.11) |
| spaCy          | Lemmatisation (modèle en_core_web_sm)  |
| NLTK / Porter  | Stemming                               |
| ir_measures    | Calcul MAP, P@K                        |
| matplotlib     | Courbes Rappel-Précision               |
| Java JDK 11    | Runtime pour Terrier                   |
| Python 3.11    | Compatibilité PyTerrier + spaCy        |
