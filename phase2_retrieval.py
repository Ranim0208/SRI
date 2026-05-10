"""
Phase 2 - Tâche 3 : Mise en correspondance requêtes / tweets
=============================================================
Modèles testés : BM25, TF_IDF, PL2, DPH
sur les 3 index : lexèmes, stems, lemmes

Auteurs : Groupe SRI - 2ème ING IMD - ISAMM 2025-2026
"""

import json
import re
from pathlib import Path

import pandas as pd
import pyterrier as pt

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

TOPICS_FILE = Path("phase1_output/topics.json").resolve()
INDEX_DIR   = Path("phase2_output/indexes").resolve()
OUTPUT_DIR  = Path("phase2_output").resolve()
RESULTS_DIR = OUTPUT_DIR / "results"
TOP_K = 30

INDEXES = {
    "lexemes": INDEX_DIR / "index_lexemes",
    "stems":   INDEX_DIR / "index_stems",
    "lemmes":  INDEX_DIR / "index_lemmes",
}

MODELS = {
    "BM25":   "BM25",
    "TF_IDF": "TF_IDF",
    "PL2":    "PL2",
    "DPH":    "DPH",
}


# ═══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT DES REQUÊTES
# ═══════════════════════════════════════════════════════════════════════════════

def load_topics(path: Path) -> pd.DataFrame:
    with open(path, encoding="utf-8") as f:
        topics = json.load(f)
    records = []
    for t in topics:
        query = re.sub(r"[^\w\s]", " ", t["title"]).lower().strip()
        records.append({"qid": t["num"], "query": query})
    df = pd.DataFrame(records)
    print(f"[✓] {len(df)} requêtes chargées")
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# RECHERCHE
# ═══════════════════════════════════════════════════════════════════════════════

def results_to_trec(df: pd.DataFrame, run_id: str) -> str:
    lines = []
    for _, row in df.iterrows():
        lines.append(
            f"{row['qid']} Q0 {row['docno']} {int(row['rank'])} "
            f"{row['score']:.6f} {run_id}"
        )
    return "\n".join(lines)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Vérifier les index
    for name, path in INDEXES.items():
        if not path.exists():
            print(f"[✗] Index '{name}' introuvable.")
            print("    → Lancez d'abord : python phase2_indexer_v2.py")
            return

    # Initialiser PyTerrier
    print("[→] Initialisation de PyTerrier...")
    if not pt.java.started():
        pt.java.init()
    print("[✓] PyTerrier prêt\n")

    topics = load_topics(TOPICS_FILE)
    all_results = []

    print("=" * 60)
    print("LANCEMENT DES MODÈLES DE RECHERCHE")
    print("=" * 60)

    for idx_name, idx_path in INDEXES.items():
        print(f"\n[→] Index : {idx_name}")
        index = pt.IndexFactory.of(str(idx_path))

        for model_name, wmodel in MODELS.items():
            run_id = f"{model_name}_{idx_name}"
            print(f"   [→] {model_name}...", end=" ", flush=True)
            try:
                retriever = pt.BatchRetrieve(
                    index,
                    wmodel=wmodel,
                    num_results=TOP_K,
                    metadata=["docno"],
                )
                results_df = retriever.transform(topics)
                results_df["run_id"] = run_id

                trec_str = results_to_trec(results_df, run_id)
                out_file = RESULTS_DIR / f"results_{run_id}.txt"
                out_file.write_text(trec_str, encoding="utf-8")
                all_results.append(results_df)
                print(f"✓  ({len(results_df)} résultats)")
            except Exception as e:
                print(f"✗ Erreur : {e}")

    if all_results:
        combined = pd.concat(all_results, ignore_index=True)
        combined.to_csv(OUTPUT_DIR / "all_results.csv", index=False)
        print(f"\n[✓] Tous les résultats → {OUTPUT_DIR}/all_results.csv")

    print("\n" + "=" * 60)
    print("✅ Retrieval terminé.")
    for f in sorted(RESULTS_DIR.glob("*.txt")):
        print(f"   ├── {f.name}")
    print("=" * 60)
    print("\n→ Prochaine étape : python phase2_evaluation.py")


if __name__ == "__main__":
    main()
