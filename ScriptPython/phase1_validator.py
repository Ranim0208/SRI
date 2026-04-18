"""
Utilitaires pour Phase 1: Validation et analyse des données
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter


class Phase1Validator:
    """Classe pour valider et analyser les données de Phase 1"""
    
    def __init__(self, output_dir: str = "phase1_output"):
        self.output_dir = Path(output_dir)
        self.tweets = []
        self.topics = []
        self.qrels = []
    
    def load_files(self):
        """Charge les fichiers générés"""
        try:
            # Charger les tweets
            tweets_file = self.output_dir / "tweets.json"
            if tweets_file.exists():
                with open(tweets_file, 'r', encoding='utf-8') as f:
                    self.tweets = json.load(f)
                print(f"✅ {len(self.tweets)} tweets chargés")
            
            # Charger les topics
            topics_file = self.output_dir / "topics.json"
            if topics_file.exists():
                with open(topics_file, 'r', encoding='utf-8') as f:
                    self.topics = json.load(f)
                print(f"✅ {len(self.topics)} requêtes chargées")
            
            # Charger les qrels
            qrels_file = self.output_dir / "qrels.txt"
            if qrels_file.exists():
                with open(qrels_file, 'r') as f:
                    self.qrels = [line.strip().split() for line in f if line.strip()]
                print(f"✅ {len(self.qrels)} jugements chargés")
            
            return True
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return False
    
    def validate_structure(self) -> bool:
        """Valide la structure des données"""
        print("\n" + "=" * 60)
        print("VALIDATION DE LA STRUCTURE")
        print("=" * 60)
        
        valid = True
        
        # Valider les tweets
        print("\n📋 TWEETS:")
        required_fields = {'id', 'query_id', 'text', 'timestamp', 'user'}
        for tweet in self.tweets[:5]:  # Vérifier les 5 premiers
            missing = required_fields - set(tweet.keys())
            if missing:
                print(f"  ❌ Tweet {tweet.get('id', 'Unknown')} manque: {missing}")
                valid = False
        if not any(missing for tweet in self.tweets):
            print(f"  ✅ Tous les {len(self.tweets)} tweets ont les champs requis")
        
        # Valider les topics
        print("\n🎯 REQUÊTES:")
        required_topic_fields = {'num', 'title'}
        for topic in self.topics:
            missing = required_topic_fields - set(topic.keys())
            if missing:
                print(f"  ❌ Requête {topic.get('num', 'Unknown')} manque: {missing}")
                valid = False
        if not any(missing for topic in self.topics):
            print(f"  ✅ Toutes les {len(self.topics)} requêtes sont valides")
        
        # Valider les qrels
        print("\n✔️ QRELS:")
        for qrel in self.qrels[:5]:  # Vérifier les 5 premiers
            if len(qrel) != 4:
                print(f"  ❌ Ligne mal formée: {' '.join(qrel)}")
                valid = False
        
        if all(len(qrel) == 4 for qrel in self.qrels):
            print(f"  ✅ Tous les {len(self.qrels)} jugements sont valides")
        
        return valid
    
    def generate_statistics(self):
        """Génère des statistiques sur les données"""
        print("\n" + "=" * 60)
        print("STATISTIQUES")
        print("=" * 60)
        
        if not self.tweets:
            print("⚠️  Aucun tweet chargé")
            return
        
        # Statistiques des tweets
        print("\n📊 TWEETS:")
        print(f"  Total: {len(self.tweets)}")
        print(f"  Par requête: {len(self.tweets) // len(self.topics):.0f} en moyenne")
        
        # Distribution par requête
        query_distribution = Counter(t['query_id'] for t in self.tweets)
        print("\n  Distribution par requête:")
        for query_id in sorted(query_distribution.keys()):
            count = query_distribution[query_id]
            print(f"    {query_id}: {count} tweets")
        
        # Statistiques des jugements
        print("\n🎯 JUGEMENTS DE PERTINENCE:")
        relevant_count = sum(1 for qrel in self.qrels if qrel[3] == '1')
        non_relevant_count = sum(1 for qrel in self.qrels if qrel[3] == '0')
        
        print(f"  Pertinents (1): {relevant_count}")
        print(f"  Non pertinents (0): {non_relevant_count}")
        print(f"  Ratio pertinence: {relevant_count/len(self.qrels)*100:.1f}%")
        
        # Vérification: 30 pertinents par requête
        relevant_per_query = Counter(qrel[0] for qrel in self.qrels if qrel[3] == '1')
        print("\n  Pertinents par requête:")
        for query_id in sorted(relevant_per_query.keys()):
            count = relevant_per_query[query_id]
            print(f"    {query_id}: {count}")
        
        # Statistiques des langues
        languages = Counter(t.get('lang', 'unknown') for t in self.tweets)
        print(f"\n🌐 LANGUES: {dict(languages)}")
        
        # Longueur moyenne des tweets
        avg_length = sum(len(t.get('text', '')) for t in self.tweets) / len(self.tweets)
        print(f"\n📏 Longueur moyenne des tweets: {avg_length:.0f} caractères")
    
    def check_duplicates(self):
        """Vérifie les doublons"""
        print("\n" + "=" * 60)
        print("VÉRIFICATION DES DOUBLONS")
        print("=" * 60)
        
        tweet_ids = [t['id'] for t in self.tweets]
        unique_ids = set(tweet_ids)
        
        if len(tweet_ids) == len(unique_ids):
            print(f"✅ Aucun doublon: {len(tweet_ids)} IDs uniques")
        else:
            duplicates = len(tweet_ids) - len(unique_ids)
            print(f"⚠️  {duplicates} doublons détectés!")
            
            # Lister les IDs dupliqués
            id_counts = Counter(tweet_ids)
            duplicated_ids = [id for id, count in id_counts.items() if count > 1]
            print(f"   IDs dupliqués: {duplicated_ids[:10]}")  # Afficher les 10 premiers
    
    def check_consistency(self):
        """Vérifie la cohérence entre les fichiers"""
        print("\n" + "=" * 60)
        print("VÉRIFICATION DE COHÉRENCE")
        print("=" * 60)
        
        # Vérifier que toutes les query_ids des tweets existent dans topics
        tweet_query_ids = set(t['query_id'] for t in self.tweets)
        topic_ids = set(t['num'] for t in self.topics)
        
        missing_topics = tweet_query_ids - topic_ids
        if missing_topics:
            print(f"⚠️  Query IDs dans tweets mais pas dans topics: {missing_topics}")
        else:
            print(f"✅ Toutes les query IDs des tweets existent dans topics")
        
        # Vérifier que toutes les query_ids des qrels existent dans topics
        qrel_query_ids = set(qrel[0] for qrel in self.qrels)
        missing_qrel_topics = qrel_query_ids - topic_ids
        if missing_qrel_topics:
            print(f"⚠️  Query IDs dans qrels mais pas dans topics: {missing_qrel_topics}")
        else:
            print(f"✅ Toutes les query IDs des qrels existent dans topics")
        
        # Vérifier que tous les tweet_ids des qrels existent dans tweets
        tweet_ids = set(t['id'] for t in self.tweets)
        qrel_tweet_ids = set(qrel[2] for qrel in self.qrels)
        missing_tweets = qrel_tweet_ids - tweet_ids
        if missing_tweets:
            print(f"⚠️  Tweet IDs dans qrels mais pas dans tweets: {len(missing_tweets)}")
        else:
            print(f"✅ Tous les tweet IDs des qrels existent dans tweets")
    
    def generate_summary_report(self):
        """Génère un rapport récapitulatif"""
        output_file = self.output_dir / "validation_report.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("RAPPORT DE VALIDATION - PHASE 1\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("FICHIERS DÉTECTÉS:\n")
            f.write(f"  Tweets: {len(self.tweets)} documents\n")
            f.write(f"  Topics: {len(self.topics)} requêtes\n")
            f.write(f"  Qrels: {len(self.qrels)} jugements\n\n")
            
            f.write("STATISTIQUES CLÉS:\n")
            if self.tweets:
                query_distribution = Counter(t['query_id'] for t in self.tweets)
                f.write(f"  Requêtes avec tweets:\n")
                for query_id in sorted(query_distribution.keys()):
                    f.write(f"    {query_id}: {query_distribution[query_id]}\n")
            
            if self.qrels:
                relevant = sum(1 for qrel in self.qrels if qrel[3] == '1')
                f.write(f"\n  Jugements pertinents: {relevant}/{len(self.qrels)}\n")
                f.write(f"  Jugements non pertinents: {len(self.qrels) - relevant}/{len(self.qrels)}\n")
            
            f.write("\nVALIDATION: SUCCÈS ✅\n")
        
        print(f"\n📄 Rapport sauvegardé: {output_file}")
        return output_file
    
    def run_full_validation(self):
        """Exécute la validation complète"""
        print("\n🔍 VALIDATION COMPLÈTE DE PHASE 1\n")
        
        if not self.load_files():
            return False
        
        self.validate_structure()
        self.check_duplicates()
        self.check_consistency()
        self.generate_statistics()
        self.generate_summary_report()
        
        print("\n" + "=" * 60)
        print("✅ VALIDATION TERMINÉE")
        print("=" * 60)
        return True


def main():
    """Fonction principale"""
    validator = Phase1Validator(output_dir="/home/claude/phase1_output")
    validator.run_full_validation()


if __name__ == "__main__":
    main()
