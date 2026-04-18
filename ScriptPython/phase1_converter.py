"""
Utilitaires de conversion et manipulation des formats Phase 1
"""

import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict


class FormatConverter:
    """Convertisseur de formats pour les fichiers Phase 1"""
    
    @staticmethod
    def json_to_xml_topics(input_file: str, output_file: str):
        """Convertit topics.json en format XML TREC"""
        with open(input_file, 'r', encoding='utf-8') as f:
            topics = json.load(f)
        
        root = ET.Element('topics')
        for topic in topics:
            top = ET.SubElement(root, 'top')
            num = ET.SubElement(top, 'num')
            num.text = topic['num']
            title = ET.SubElement(top, 'title')
            title.text = topic['title']
        
        tree = ET.ElementTree(root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        print(f"✅ Topics convertis en XML: {output_file}")
    
    @staticmethod
    def json_to_csv_tweets(input_file: str, output_file: str):
        """Convertit tweets.json en CSV"""
        with open(input_file, 'r', encoding='utf-8') as f:
            tweets = json.load(f)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if tweets:
                writer = csv.DictWriter(f, fieldnames=tweets[0].keys())
                writer.writeheader()
                writer.writerows(tweets)
        
        print(f"✅ Tweets convertis en CSV: {output_file}")
    
    @staticmethod
    def qrels_to_json(input_file: str, output_file: str):
        """Convertit qrels.txt en JSON"""
        qrels = []
        with open(input_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 4:
                    qrels.append({
                        "query_id": parts[0],
                        "zero": parts[1],
                        "tweet_id": parts[2],
                        "relevance": int(parts[3])
                    })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(qrels, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Qrels convertis en JSON: {output_file}")
    
    @staticmethod
    def create_summary_csv(tweets_file: str, topics_file: str, qrels_file: str, output_file: str):
        """Crée un CSV récapitulatif"""
        # Charger les données
        with open(tweets_file, 'r', encoding='utf-8') as f:
            tweets = json.load(f)
        with open(topics_file, 'r', encoding='utf-8') as f:
            topics = json.load(f)
        
        # Créer le résumé
        summary = []
        for topic in topics:
            query_id = topic['num']
            query_text = topic['title']
            tweet_count = len([t for t in tweets if t['query_id'] == query_id])
            
            summary.append({
                'query_id': query_id,
                'query_text': query_text,
                'tweet_count': tweet_count
            })
        
        # Sauvegarder
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['query_id', 'query_text', 'tweet_count'])
            writer.writeheader()
            writer.writerows(summary)
        
        print(f"✅ Résumé créé: {output_file}")
    
    @staticmethod
    def export_sample_tweets(tweets_file: str, output_file: str, sample_size: int = 10):
        """Exporte un échantillon de tweets lisible"""
        with open(tweets_file, 'r', encoding='utf-8') as f:
            tweets = json.load(f)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"ÉCHANTILLON DE {min(sample_size, len(tweets))} TWEETS\n")
            f.write("=" * 80 + "\n\n")
            
            for i, tweet in enumerate(tweets[:sample_size], 1):
                f.write(f"TWEET #{i}\n")
                f.write("-" * 80 + "\n")
                f.write(f"ID: {tweet['id']}\n")
                f.write(f"Query: {tweet['query_id']}\n")
                f.write(f"User: {tweet['user']}\n")
                f.write(f"Timestamp: {tweet['timestamp']}\n")
                f.write(f"Texte: {tweet['text'][:200]}...\n")
                f.write(f"Retweets: {tweet.get('retweets', 0)} | Likes: {tweet.get('likes', 0)}\n")
                f.write("\n")
        
        print(f"✅ Échantillon sauvegardé: {output_file}")


def create_export_bundle(input_dir: str = "phase1_output", output_dir: str = None):
    """Crée un bundle complet avec tous les formats"""
    input_path = Path(input_dir)
    
    if output_dir is None:
        output_dir = input_path / "exports"
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print("\n" + "=" * 60)
    print("CRÉATION D'UN BUNDLE D'EXPORTATION")
    print("=" * 60 + "\n")
    
    # Fichiers sources
    tweets_file = input_path / "tweets.json"
    topics_file = input_path / "topics.json"
    qrels_file = input_path / "qrels.txt"
    
    if not all(f.exists() for f in [tweets_file, topics_file, qrels_file]):
        print("❌ Fichiers sources manquants!")
        return
    
    # Conversions
    print("🔄 Conversion des formats...\n")
    
    # Topics en XML
    FormatConverter.json_to_xml_topics(
        str(topics_file),
        str(output_path / "topics.xml")
    )
    
    # Tweets en CSV
    FormatConverter.json_to_csv_tweets(
        str(tweets_file),
        str(output_path / "tweets.csv")
    )
    
    # Qrels en JSON
    FormatConverter.qrels_to_json(
        str(qrels_file),
        str(output_path / "qrels.json")
    )
    
    # Résumé CSV
    FormatConverter.create_summary_csv(
        str(tweets_file),
        str(topics_file),
        str(qrels_file),
        str(output_path / "query_summary.csv")
    )
    
    # Échantillon lisible
    FormatConverter.export_sample_tweets(
        str(tweets_file),
        str(output_path / "sample_tweets.txt"),
        sample_size=10
    )
    
    # Copier les fichiers originaux
    import shutil
    shutil.copy(tweets_file, output_path / "tweets.json")
    shutil.copy(topics_file, output_path / "topics.json")
    shutil.copy(qrels_file, output_path / "qrels.txt")
    
    print("\n" + "=" * 60)
    print("✅ BUNDLE D'EXPORTATION CRÉÉ")
    print("=" * 60)
    print(f"\nFichiers disponibles dans: {output_path}")
    print("\n📋 Fichiers générés:")
    for file in sorted(output_path.glob("*")):
        print(f"  - {file.name}")


if __name__ == "__main__":
    create_export_bundle(
        input_dir="/home/claude/phase1_output",
        output_dir="/home/claude/phase1_output/exports"
    )
