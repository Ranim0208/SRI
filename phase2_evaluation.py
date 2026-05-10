"""
Phase 2 - Tâche 4 : Évaluation des résultats de RI
====================================================
Ce script évalue les résultats de retrieval selon les mesures standard :
  - MAP     : Mean Average Precision
  - P@1     : Précision au rang 1
  - P@5     : Précision au rang 5
  - P@10    : Précision au rang 10
  - Rappel  : Recall global (au rang 30)
  - Courbes Rappel-Précision (sauvegardées en PNG)

Auteurs : Groupe SRI - 2ème ING IMD - ISAMM 2025-2026
"""

import re
from pathlib import Path
from collections import defaultdict

import pandas as pd
import matplotlib
matplotlib.use("Agg")   # pas besoin d'écran
import matplotlib.pyplot as plt
import numpy as np

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

QRELS_FILE   = Path("phase1_output/qrels.txt").resolve()
RESULTS_DIR  = Path("phase2_output/results").resolve()
OUTPUT_DIR   = Path("phase2_output").resolve()
CHARTS_DIR   = OUTPUT_DIR / "charts"

TOP_K = 30   # on évalue sur le top-30


# ═══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT DES QRELS
# ═══════════════════════════════════════════════════════════════════════════════

def load_qrels(path: Path) -> dict:
    """
    Charge qrels.txt → dict { qid : set(docno_pertinents) }
    Format : qid  iter  docno  relevance
    """
    qrels = defaultdict(set)
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 4:
                continue
            qid, _, docno, rel = parts[0], parts[1], parts[2], int(parts[3])
            if rel > 0:
                qrels[qid].add(docno)
    print(f"[✓] Qrels chargés : {len(qrels)} requêtes, "
          f"{sum(len(v) for v in qrels.values())} documents pertinents")
    return dict(qrels)


# ═══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT DES RÉSULTATS TREC
# ═══════════════════════════════════════════════════════════════════════════════

def load_trec_results(path: Path) -> dict:
    """
    Charge un fichier TREC → dict { qid : [docno_ordonnés] }
    Format : qid  Q0  docno  rank  score  run_name
    """
    results = defaultdict(list)
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 6:
                continue
            qid, docno, rank = parts[0], parts[2], int(parts[3])
            results[qid].append((rank, docno))
    # Trier par rang et garder seulement les docno
    return {q: [d for _, d in sorted(docs)] for q, docs in results.items()}


# ═══════════════════════════════════════════════════════════════════════════════
# CALCUL DES MÉTRIQUES
# ═══════════════════════════════════════════════════════════════════════════════

def precision_at_k(retrieved: list, relevant: set, k: int) -> float:
    """P@K : proportion de documents pertinents parmi les k premiers."""
    if not retrieved:
        return 0.0
    top_k = retrieved[:k]
    hits = sum(1 for d in top_k if d in relevant)
    return hits / k


def recall_at_k(retrieved: list, relevant: set, k: int) -> float:
    """Recall@K : proportion des pertinents retrouvés dans les k premiers."""
    if not relevant:
        return 0.0
    top_k = retrieved[:k]
    hits = sum(1 for d in top_k if d in relevant)
    return hits / len(relevant)


def average_precision(retrieved: list, relevant: set) -> float:
    """AP : précision moyenne aux rangs où un document pertinent est retrouvé."""
    if not relevant or not retrieved:
        return 0.0
    hits = 0
    sum_prec = 0.0
    for i, doc in enumerate(retrieved, start=1):
        if doc in relevant:
            hits += 1
            sum_prec += hits / i
    return sum_prec / len(relevant)


def recall_precision_curve(retrieved: list, relevant: set):
    """Retourne (recall_points, precision_points) pour la courbe R-P."""
    recalls, precisions = [], []
    hits = 0
    for i, doc in enumerate(retrieved, start=1):
        if doc in relevant:
            hits += 1
        precisions.append(hits / i)
        recalls.append(hits / len(relevant) if relevant else 0.0)
    return recalls, precisions


def evaluate_run(results: dict, qrels: dict, top_k: int = 30) -> dict:
    """
    Calcule toutes les métriques pour un run.
    Retourne un dict avec les valeurs par requête + moyennes (MAP, etc.)
    """
    per_query = {}
    for qid, retrieved in results.items():
        relevant = qrels.get(qid, set())
        top = retrieved[:top_k]
        per_query[qid] = {
            "AP":    average_precision(top, relevant),
            "P@1":   precision_at_k(top, relevant, 1),
            "P@5":   precision_at_k(top, relevant, 5),
            "P@10":  precision_at_k(top, relevant, 10),
            "R@30":  recall_at_k(top, relevant, 30),
            "retrieved": top,
            "relevant":  relevant,
        }

    # Moyennes sur toutes les requêtes
    metrics = ["AP", "P@1", "P@5", "P@10", "R@30"]
    averages = {}
    for m in metrics:
        vals = [v[m] for v in per_query.values() if qid in results]
        averages[m] = np.mean([per_query[q][m] for q in per_query]) if per_query else 0.0
    averages["MAP"] = averages.pop("AP")  # renommer AP moyen → MAP

    return {"per_query": per_query, "averages": averages}


# ═══════════════════════════════════════════════════════════════════════════════
# TRACÉ DES COURBES
# ═══════════════════════════════════════════════════════════════════════════════

def plot_rp_curves(all_evals: dict, qrels: dict):
    """Trace et sauvegarde les courbes Rappel-Précision par requête."""
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    # Récupérer toutes les requêtes
    all_qids = sorted(qrels.keys())

    for qid in all_qids:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.set_title(f"Courbe Rappel-Précision — Requête {qid}", fontsize=13)
        ax.set_xlabel("Rappel")
        ax.set_ylabel("Précision")
        ax.set_xlim(0, 1.05)
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3)

        for run_name, eval_data in all_evals.items():
            pq = eval_data["per_query"]
            if qid not in pq:
                continue
            retrieved = pq[qid]["retrieved"]
            relevant  = pq[qid]["relevant"]
            recalls, precisions = recall_precision_curve(retrieved, relevant)
            if recalls:
                ax.plot(recalls, precisions, marker="o", markersize=3,
                        label=run_name, linewidth=1.5)

        ax.legend(fontsize=7, loc="upper right", ncol=2)
        fig.tight_layout()
        out = CHARTS_DIR / f"rp_curve_{qid}.png"
        fig.savefig(out, dpi=120)
        plt.close(fig)
        print(f"   [✓] Courbe R-P → {out.name}")

    # Courbe globale (interpolée 11 points standard)
    recall_levels = np.linspace(0, 1, 11)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title("Courbes Rappel-Précision (moyennées — tous modèles)", fontsize=13)
    ax.set_xlabel("Rappel")
    ax.set_ylabel("Précision")
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    for run_name, eval_data in all_evals.items():
        interp_precisions = []
        for rl in recall_levels:
            prec_vals = []
            for qid in qrels:
                pq = eval_data["per_query"]
                if qid not in pq:
                    continue
                retrieved = pq[qid]["retrieved"]
                relevant  = pq[qid]["relevant"]
                recalls, precisions = recall_precision_curve(retrieved, relevant)
                # précision interpolée au niveau de rappel rl
                p = max((p for r, p in zip(recalls, precisions) if r >= rl), default=0.0)
                prec_vals.append(p)
            interp_precisions.append(np.mean(prec_vals) if prec_vals else 0.0)
        ax.plot(recall_levels, interp_precisions, marker="s", markersize=4,
                label=run_name, linewidth=2)

    ax.legend(fontsize=8, loc="upper right", ncol=2)
    fig.tight_layout()
    out = CHARTS_DIR / "rp_curve_global.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"   [✓] Courbe R-P globale → {out.name}")


# ═══════════════════════════════════════════════════════════════════════════════
# RAPPORT TEXTUEL
# ═══════════════════════════════════════════════════════════════════════════════

def generate_report(summary_df: pd.DataFrame, all_evals: dict, qrels: dict) -> str:
    lines = []
    lines.append("=" * 70)
    lines.append("RAPPORT D'ÉVALUATION — PHASE 2")
    lines.append("Projet SRI — 2ème ING IMD — ISAMM 2025-2026")
    lines.append("Thème : Guerre en Iran")
    lines.append("=" * 70)

    lines.append("\n## 1. Tableau comparatif des stratégies (moyennes)\n")
    lines.append(summary_df.to_string(index=True, float_format="{:.4f}".format))

    lines.append("\n\n## 2. Meilleure stratégie par métrique\n")
    for col in ["MAP", "P@1", "P@5", "P@10", "R@30"]:
        best_run = summary_df[col].idxmax()
        best_val = summary_df[col].max()
        lines.append(f"  {col:6s} : {best_run}  ({best_val:.4f})")

    lines.append("\n\n## 3. Détail par requête\n")
    for run_name, eval_data in all_evals.items():
        lines.append(f"\n--- Run : {run_name} ---")
        pq = eval_data["per_query"]
        for qid in sorted(pq):
            m = pq[qid]
            lines.append(
                f"  {qid}  AP={m['AP']:.4f}  P@1={m['P@1']:.2f}  "
                f"P@5={m['P@5']:.2f}  P@10={m['P@10']:.2f}  R@30={m['R@30']:.2f}"
            )

    lines.append("\n\n## 4. Analyse et interprétation\n")
    best_map = summary_df["MAP"].idxmax()
    worst_map = summary_df["MAP"].idxmin()
    lines.append(
        f"  La stratégie '{best_map}' obtient le meilleur MAP ({summary_df.loc[best_map,'MAP']:.4f}).\n"
        f"  La stratégie '{worst_map}' obtient le MAP le plus faible ({summary_df.loc[worst_map,'MAP']:.4f}).\n"
        f"  Les courbes Rappel-Précision sont disponibles dans phase2_output/charts/."
    )

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# SCRIPT PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Vérifier que les résultats existent
    result_files = sorted(RESULTS_DIR.glob("results_*.txt"))
    if not result_files:
        print(f"[✗] Aucun fichier résultat dans {RESULTS_DIR}")
        print("    → Lancez d'abord : python phase2_retrieval.py")
        return

    # Charger les qrels
    qrels = load_qrels(QRELS_FILE)

    # Évaluer chaque run
    all_evals = {}
    print("\n[→] Évaluation des runs...")
    for rf in result_files:
        run_name = rf.stem.replace("results_", "")
        results  = load_trec_results(rf)
        eval_data = evaluate_run(results, qrels, TOP_K)
        all_evals[run_name] = eval_data
        avg = eval_data["averages"]
        print(f"   {run_name:35s}  MAP={avg['MAP']:.4f}  "
              f"P@5={avg['P@5']:.4f}  P@10={avg['P@10']:.4f}")

    # Tableau récapitulatif
    rows = {}
    for run_name, eval_data in all_evals.items():
        rows[run_name] = eval_data["averages"]
    summary_df = pd.DataFrame(rows).T[["MAP", "P@1", "P@5", "P@10", "R@30"]]
    summary_df.index.name = "Run"
    summary_df = summary_df.sort_values("MAP", ascending=False)

    # Sauvegarder en CSV
    summary_df.to_csv(OUTPUT_DIR / "evaluation_summary.csv")
    print(f"\n[✓] Tableau d'évaluation → {OUTPUT_DIR}/evaluation_summary.csv")

    # Courbes Rappel-Précision
    print("\n[→] Génération des courbes Rappel-Précision...")
    plot_rp_curves(all_evals, qrels)

    # Rapport textuel
    report = generate_report(summary_df, all_evals, qrels)
    report_path = OUTPUT_DIR / "rapport_phase2.txt"
    report_path.write_text(report, encoding="utf-8")
    print(f"\n[✓] Rapport → {report_path}")

    # Afficher le tableau final
    print("\n" + "=" * 60)
    print("✅ ÉVALUATION TERMINÉE")
    print("=" * 60)
    print(summary_df.to_string(float_format="{:.4f}".format))
    print("\n→ Consultez phase2_output/ pour tous les résultats.")


if __name__ == "__main__":
    main()
