"""
Phase 2 - Tâche 2 : Indexation des tweets avec PyTerrier 1.0
=============================================================
Ce script construit 3 index distincts :
  1. Lexèmes  : mots bruts (pas de transformation)
  2. Stems    : troncature Porter via PyTerrier
  3. Lemmes   : lemmatisation via spaCy

Auteurs : Groupe SRI - 2ème ING IMD - ISAMM 2025-2026
"""

import json
import re
import shutil
from pathlib import Path

import pandas as pd

# ── spaCy pour la lemmatisation ───────────────────────────────────────────────
import spacy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("[!] Modèle spaCy 'en_core_web_sm' non trouvé.")
    print("    Lancez : python -m spacy download en_core_web_sm")
    raise

# ── PyTerrier (import après spaCy pour éviter conflits) ──────────────────────
import pyterrier as pt

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

TWEETS_FILE = Path("phase1_output/tweets.json").resolve()
OUTPUT_DIR  = Path("phase2_output").resolve()
INDEX_DIR   = OUTPUT_DIR / "indexes"

# ═══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT DES TWEETS
# ═══════════════════════════════════════════════════════════════════════════════

def load_tweets(path: Path) -> pd.DataFrame:
    """Charge tweets.json et retourne un DataFrame PyTerrier-compatible."""
    with open(path, encoding="utf-8") as f:
        tweets = json.load(f)

    records = []
    for t in tweets:
        text = t.get("text", "").strip()
        if text:
            records.append({
                "docno":    str(t["id"]),
                "text":     text,
                "query_id": t.get("query_id", ""),
            })

    df = pd.DataFrame(records)
    print(f"[✓] {len(df)} tweets chargés depuis {path}")
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# PRÉTRAITEMENT DU TEXTE
# ═══════════════════════════════════════════════════════════════════════════════

def clean_text(text: str) -> str:
    """Nettoyage de base : supprime URLs, mentions, ponctuation."""
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = re.sub(r"#(\w+)", r"\1", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


def lemmatize_text(text: str) -> str:
    """Retourne les lemmes (sans stopwords, sans ponctuation)."""
    doc = nlp(text)
    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop and not token.is_punct and token.is_alpha
    ]
    return " ".join(tokens) if tokens else text


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRUCTION DES INDEX (API PyTerrier 1.0)
# ═══════════════════════════════════════════════════════════════════════════════

def build_index(df: pd.DataFrame, index_path: Path,
                stemmer: str = None, text_col: str = "text"):
    """
    Crée un index PyTerrier sur la colonne text_col.

    stemmer : None | "porter" | "snowball"
    """
    if index_path.exists():
        shutil.rmtree(index_path)
    index_path.mkdir(parents=True)

    # Préparer le DataFrame
    idx_df = df[["docno", text_col]].rename(columns={text_col: "text"}).copy()
    idx_df = idx_df[idx_df["text"].str.strip().str.len() > 0].reset_index(drop=True)

    # Configurer le pipeline de termes
    if stemmer == "porter":
        termpipelines = "Stopwords,PorterStemmer"
    elif stemmer == "snowball":
        termpipelines = "Stopwords,SnowballStemmer"
    else:
        termpipelines = ""

    # Chemin absolu obligatoire pour Terrier sur Windows
    abs_path = str(index_path.resolve())

    # Forcer Terrier à utiliser ce chemin exact (sans préfixe .\var\)
    pt.ApplicationSetup.setProperty("terrier.index.path", abs_path)

    # Créer l'indexer
    indexer = pt.IterDictIndexer(
        abs_path,
        overwrite=True,
        meta={"docno": 20},
        properties={
            "termpipelines": termpipelines,
            "terrier.index.path": abs_path,
        },
    )

    index_ref = indexer.index(
        ({"docno": row["docno"], "text": row["text"]} for _, row in idx_df.iterrows())
    )

    index = pt.IndexFactory.of(index_ref)
    stats = index.getCollectionStatistics()
    print(f"   [✓] Index créé : {index_path.name}")
    print(f"       Documents : {stats.getNumberOfDocuments()}")
    print(f"       Termes uniques : {stats.getNumberOfUniqueTerms()}")
    return index


# ═══════════════════════════════════════════════════════════════════════════════
# SCRIPT PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    # Initialiser PyTerrier
    print("[→] Initialisation de PyTerrier...")
    if not pt.java.started():
        # Forcer terrier.home vers le dossier courant pour éviter .\var\
        import os
        os.environ["TERRIER_HOME"] = str(Path(".").resolve())
        pt.java.init()
    print("[✓] PyTerrier initialisé")

    # 1. Charger les tweets
    df = load_tweets(TWEETS_FILE)

    # 2. Nettoyer le texte
    print("\n[→] Nettoyage du texte...")
    df["text_clean"] = df["text"].apply(clean_text)

    # 3. Lemmatisation
    print("[→] Lemmatisation avec spaCy... (2-4 minutes)")
    df["text_lemma"] = df["text_clean"].apply(lemmatize_text)
    print("[✓] Lemmatisation terminée")

    # Sauvegarder le corpus prétraité
    corpus_path = OUTPUT_DIR / "corpus_preprocessed.csv"
    df.to_csv(corpus_path, index=False)
    print(f"[✓] Corpus prétraité → {corpus_path}")

    # ── Index 1 : Lexèmes (mots bruts) ───────────────────────────────────────
    print("\n[→] Construction de l'index LEXÈMES...")
    build_index(df, INDEX_DIR / "index_lexemes", stemmer=None, text_col="text_clean")

    # ── Index 2 : Stems (Porter) ──────────────────────────────────────────────
    print("\n[→] Construction de l'index STEMS (Porter)...")
    build_index(df, INDEX_DIR / "index_stems", stemmer="porter", text_col="text_clean")

    # ── Index 3 : Lemmes (spaCy) ──────────────────────────────────────────────
    print("\n[→] Construction de l'index LEMMES...")
    build_index(df, INDEX_DIR / "index_lemmes", stemmer=None, text_col="text_lemma")

    print("\n" + "=" * 60)
    print("✅ Indexation terminée ! 3 index créés dans :")
    print(f"   {INDEX_DIR}/")
    print("   ├── index_lexemes/")
    print("   ├── index_stems/")
    print("   └── index_lemmes/")
    print("=" * 60)
    print("\n→ Prochaine étape : python phase2_retrieval.py")


if __name__ == "__main__":
    main()
