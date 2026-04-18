"""
Phase 1 : Construction de la collection de test
Collecte de tweets sur la thématique "Guerre en Iran" avec Playwright
VERSION AVEC PROFIL CHROME EXISTANT (sessions préservées)
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import os

from playwright.async_api import async_playwright


class IranWarTweetCollector:
    """Collecteur de tweets sur la thématique Guerre en Iran"""
    
    def __init__(self, output_dir: str = "phase1_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Requêtes en anglais sur le thème Guerre en Iran
        self.queries = [
            {"num": "MB01", "title": "regime change Iran"},
            {"num": "MB02", "title": "regime collapse"},
            {"num": "MB03", "title": "Closing Hormuz strait"},
            {"num": "MB04", "title": "Intercepting missiles drones"},
            {"num": "MB05", "title": "revolutionary guard Iran"}
        ]
        
        self.tweets_per_query = 100
        self.relevant_count = 30
        self.all_tweets = []
        self.tweet_ids = set()
    
    def get_chrome_user_data_dir(self):
        """Trouve le répertoire de profil Chrome de l'utilisateur"""
        username = os.getenv('USERNAME') or os.getenv('USER')
        
        # Chemin Chrome par défaut sur Windows
        chrome_paths = [
            f"C:\\playwright-profile"
           
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    async def collect_tweets_for_query(self, page, query: Dict) -> List[Dict]:
        """Collecte les tweets pour une requête donnée"""
        print(f"\n🔍 Collecte pour la requête: {query['title']} ({query['num']})")
        
        tweets = []
        
        try:
            # URL de recherche sur X
            search_url = f"https://x.com/search?q={query['title']}&f=live"
            print(f"   → Accès à: {search_url}")
            
            await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Vérifier si on est connecté
            try:
                login_button = await page.query_selector('a[href="/login"]')
                if login_button:
                    print("   ⚠️  Pas connecté! Veuillez vous connecter dans le navigateur...")
                    print("   ⏸️  Appuyez sur ENTRÉE une fois connecté...")
                    await asyncio.get_event_loop().run_in_executor(None, input)
            except:
                pass
            
            # Scroller pour charger plus de tweets
            tweet_count = 0
            previous_height = 0
            scroll_attempts = 0
            max_scroll_attempts = 20
            
            while tweet_count < self.tweets_per_query and scroll_attempts < max_scroll_attempts:
                # Extraire les tweets visibles
                tweet_elements = await page.query_selector_all('article[data-testid="tweet"]')
                current_count = len(tweet_elements)
                
                print(f"   → Tweets collectés: {len(tweets)}/{self.tweets_per_query} (visibles: {current_count})")
                
                # Parser les tweets
                for element in tweet_elements:
                    if len(tweets) >= self.tweets_per_query:
                        break
                    
                    try:
                        tweet = await self._extract_tweet_data(element, query)
                        if tweet and tweet['id'] not in self.tweet_ids:
                            tweets.append(tweet)
                            self.tweet_ids.add(tweet['id'])
                    except Exception as e:
                        continue
                
                tweet_count = len(tweets)
                
                if tweet_count >= self.tweets_per_query:
                    break
                
                # Scroller vers le bas
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == previous_height:
                    scroll_attempts += 1
                    if scroll_attempts >= 3:
                        print(f"   ⚠️  Fin du scroll")
                        break
                else:
                    scroll_attempts = 0
                
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await page.wait_for_timeout(2000)
                previous_height = new_height
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        print(f"   ✅ {len(tweets)} tweets collectés pour {query['num']}")
        return tweets[:self.tweets_per_query]
    
    async def _extract_tweet_data(self, element, query: Dict) -> Dict:
        """Extrait les données d'un tweet"""
        try:
            # Texte du tweet
            text_element = await element.query_selector('[data-testid="tweetText"]')
            text = await text_element.inner_text() if text_element else ""
            
            # ID du tweet
            link_element = await element.query_selector('a[href*="/status/"]')
            if link_element:
                href = await link_element.get_attribute('href')
                tweet_id = re.search(r'/status/(\d+)', href)
                if tweet_id:
                    tweet_id = tweet_id.group(1)
                else:
                    return None
            else:
                return None
            
            # Nom d'utilisateur
            user_element = await element.query_selector('[data-testid="User-Name"]')
            username = await user_element.inner_text() if user_element else "Unknown"
            
            # Timestamp
            time_element = await element.query_selector('time')
            timestamp = await time_element.get_attribute('datetime') if time_element else datetime.now().isoformat()
            
            # Stats
            retweets = 0
            likes = 0
            
            try:
                retweet_element = await element.query_selector('[data-testid="retweet"]')
                if retweet_element:
                    retweet_text = await retweet_element.inner_text()
                    retweets = self._parse_count(retweet_text)
                
                like_element = await element.query_selector('[data-testid="like"]')
                if like_element:
                    like_text = await like_element.inner_text()
                    likes = self._parse_count(like_text)
            except:
                pass
            
            return {
                "id": tweet_id,
                "query_id": query['num'],
                "timestamp": timestamp,
                "user": username.split('\n')[0] if username else "Unknown",
                "text": text,
                "lang": "en",
                "retweets": retweets,
                "likes": likes
            }
            
        except Exception as e:
            return None
    
    def _parse_count(self, text: str) -> int:
        """Parse les compteurs (ex: '1.2K' -> 1200)"""
        if not text:
            return 0
        
        text = text.strip().upper()
        if 'K' in text:
            return int(float(text.replace('K', '')) * 1000)
        elif 'M' in text:
            return int(float(text.replace('M', '')) * 1000000)
        else:
            try:
                return int(text)
            except:
                return 0
    
    async def collect_all_tweets(self):
        """Collecte les tweets pour toutes les requêtes"""
        print("=" * 60)
        print("PHASE 1: COLLECTE DE TWEETS - THÈME: GUERRE EN IRAN")
        print("=" * 60)
        
        # Trouver le profil Chrome
        chrome_dir = self.get_chrome_user_data_dir()
        
        if chrome_dir:
            print(f"\n✅ Profil Chrome trouvé: {chrome_dir}")
            print("   → Vos sessions seront préservées!")
        else:
            print("\n⚠️  Profil Chrome non trouvé - nouveau navigateur vide")
        
        async with async_playwright() as p:
            print("\n🌐 Lancement du navigateur...")
            
            if chrome_dir:
                # Utiliser le profil Chrome existant
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=chrome_dir,
                    headless=False,
                    channel="chrome",  # Utilise Chrome au lieu de Chromium
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-first-run',
                        '--no-default-browser-check',
                    ],
                    viewport={'width': 1280, 'height': 720},
                )
                page = context.pages[0] if context.pages else await context.new_page()
            else:
                # Fallback: navigateur normal
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                )
                page = await context.new_page()
            
            print("✅ Navigateur lancé!")
            
            # Aller directement sur X.com
            print("🌐 Ouverture de X.com...")
            await page.goto("https://x.com", timeout=30000)
            await page.wait_for_timeout(3000)
            
            print("\n" + "=" * 60)
            print("⏸️  VÉRIFIEZ DANS LE NAVIGATEUR:")
            print("=" * 60)
            print("   ✓ Êtes-vous connecté à votre compte X?")
            print("   ✓ Voyez-vous votre fil d'actualité?")
            print("")
            print("   Si NON → Connectez-vous maintenant dans le navigateur")
            print("   Si OUI → Continuez ci-dessous")
            print("=" * 60)
            print("\n>>> APPUYEZ SUR ENTRÉE DANS CE TERMINAL POUR COMMENCER <<<\n")
            await asyncio.get_event_loop().run_in_executor(None, input)
            
            # Collecter pour chaque requête
            for query in self.queries:
                tweets = await self.collect_tweets_for_query(page, query)
                self.all_tweets.extend(tweets)
            
            print("\n⏸️  Collecte terminée! Appuyez sur ENTRÉE pour fermer...")
            await asyncio.get_event_loop().run_in_executor(None, input)
            
            await context.close()
        
        print(f"\n📊 Total: {len(self.all_tweets)} tweets collectés")
    
    def save_tweets_json(self):
        """Sauvegarde les tweets en JSON"""
        output_file = self.output_dir / "tweets.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_tweets, f, indent=2, ensure_ascii=False)
        print(f"✅ Tweets sauvegardés: {output_file}")
        return output_file
    
    def save_queries(self):
        """Sauvegarde les requêtes en JSON"""
        output_file = self.output_dir / "topics.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.queries, f, indent=2, ensure_ascii=False)
        print(f"✅ Requêtes sauvegardées: {output_file}")
        return output_file
    
    def generate_qrels(self):
        """Génère le fichier Qrels (jugements de pertinence)"""
        qrels_file = self.output_dir / "qrels.txt"
        
        with open(qrels_file, 'w') as f:
            for query in self.queries:
                query_tweets = [t for t in self.all_tweets if t['query_id'] == query['num']]
                
                for idx, tweet in enumerate(query_tweets):
                    relevance = 1 if idx < self.relevant_count else 0
                    f.write(f"{query['num']} 0 {tweet['id']} {relevance}\n")
        
        print(f"✅ Qrels sauvegardés: {qrels_file}")
        return qrels_file
    
    def generate_report(self):
        """Génère un rapport de collecte"""
        report_file = self.output_dir / "rapport_phase1.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("RAPPORT DE PHASE 1 - CONSTRUCTION DE LA COLLECTION DE TEST\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("THÈME: Guerre en Iran\n")
            f.write(f"DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("STATISTIQUES:\n")
            f.write(f"  - Nombre de requêtes: {len(self.queries)}\n")
            f.write(f"  - Total de tweets collectés: {len(self.all_tweets)}\n")
            f.write(f"  - Tweets pertinents par requête: {self.relevant_count}\n")
            f.write(f"  - Total de jugements: {len(self.all_tweets)}\n\n")
            
            f.write("REQUÊTES UTILISÉES:\n")
            for query in self.queries:
                count = len([t for t in self.all_tweets if t['query_id'] == query['num']])
                f.write(f"  {query['num']}: {query['title']} ({count} tweets)\n")
            
            f.write("\nFICHIERS GÉNÉRÉS:\n")
            f.write(f"  - tweets.json: Corpus de tweets\n")
            f.write(f"  - topics.json: Ensemble des requêtes\n")
            f.write(f"  - qrels.txt: Jugements de pertinence (Qrels)\n")
            f.write(f"  - rapport_phase1.txt: Ce rapport\n")
        
        print(f"✅ Rapport sauvegardé: {report_file}")
        return report_file


async def main():
    """Fonction principale"""
    collector = IranWarTweetCollector(output_dir="phase1_output")
    
    await collector.collect_all_tweets()
    
    collector.save_tweets_json()
    collector.save_queries()
    collector.generate_qrels()
    collector.generate_report()
    
    print("\n" + "=" * 60)
    print("✅ PHASE 1 TERMINÉE - Tous les fichiers ont été générés")
    print("=" * 60)
    print(f"\nDossier de sortie: {collector.output_dir}")


if __name__ == "__main__":
    asyncio.run(main())