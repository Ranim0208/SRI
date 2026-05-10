"""
Phase 1 : Collecte de tweets - Guerre en Iran
VERSION CORRIGÉE - gère les redirections X
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import os

from playwright.async_api import async_playwright

SESSION_DIR = r"C:\playwright-session"

class IranWarTweetCollector:
    
    def __init__(self, output_dir: str = "phase1_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
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

    async def safe_goto(self, page, url, retries=3):
        """Navigation robuste qui gère les redirections"""
        for attempt in range(retries):
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)
                # Vérifier qu'on est bien sur la bonne page
                current_url = page.url
                if "x.com/search" in current_url or "twitter.com/search" in current_url:
                    return True
                elif attempt < retries - 1:
                    print(f"   ⚠️  Redirigé vers {current_url}, nouvelle tentative...")
                    await page.wait_for_timeout(2000)
            except Exception as e:
                if "interrupted" in str(e).lower() and attempt < retries - 1:
                    print(f"   ⚠️  Navigation interrompue, nouvelle tentative ({attempt+1}/{retries})...")
                    await page.wait_for_timeout(3000)
                else:
                    raise e
        return False

    async def collect_tweets_for_query(self, page, query: Dict) -> List[Dict]:
        print(f"\n🔍 Collecte pour la requête: {query['title']} ({query['num']})")
        tweets = []
        
        try:
            search_url = f"https://x.com/search?q={query['title'].replace(' ', '%20')}&f=live"
            print(f"   → Accès à: {search_url}")
            
            success = await self.safe_goto(page, search_url)
            if not success:
                print(f"   ❌ Impossible d'accéder à la page de recherche")
                return tweets
            
            await page.wait_for_timeout(2000)
            
            scroll_attempts = 0
            no_new_tweets = 0
            previous_height = 0

            while len(tweets) < self.tweets_per_query and scroll_attempts < 30:
                tweet_elements = await page.query_selector_all('article[data-testid="tweet"]')
                before = len(tweets)
                
                for element in tweet_elements:
                    if len(tweets) >= self.tweets_per_query:
                        break
                    try:
                        tweet = await self._extract_tweet_data(element, query)
                        if tweet and tweet['id'] not in self.tweet_ids:
                            tweets.append(tweet)
                            self.tweet_ids.add(tweet['id'])
                    except:
                        continue
                
                print(f"   → Tweets collectés: {len(tweets)}/{self.tweets_per_query} (visibles: {len(tweet_elements)})")
                
                if len(tweets) >= self.tweets_per_query:
                    break
                
                if len(tweets) == before:
                    no_new_tweets += 1
                    if no_new_tweets >= 5:
                        print(f"   ⚠️  Plus de nouveaux tweets disponibles")
                        break
                else:
                    no_new_tweets = 0
                
                new_height = await page.evaluate("document.body.scrollHeight")
                await page.evaluate("window.scrollBy(0, 1200)")
                await page.wait_for_timeout(2000)
                
                if new_height == previous_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                previous_height = new_height
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        print(f"   ✅ {len(tweets)} tweets collectés pour {query['num']}")
        return tweets[:self.tweets_per_query]
    
    async def _extract_tweet_data(self, element, query: Dict) -> Dict:
        try:
            text_element = await element.query_selector('[data-testid="tweetText"]')
            text = await text_element.inner_text() if text_element else ""
            
            link_element = await element.query_selector('a[href*="/status/"]')
            if not link_element:
                return None
            href = await link_element.get_attribute('href')
            match = re.search(r'/status/(\d+)', href)
            if not match:
                return None
            tweet_id = match.group(1)
            
            user_element = await element.query_selector('[data-testid="User-Name"]')
            username = await user_element.inner_text() if user_element else "Unknown"
            
            time_element = await element.query_selector('time')
            timestamp = await time_element.get_attribute('datetime') if time_element else datetime.now().isoformat()
            
            retweets, likes = 0, 0
            try:
                rt = await element.query_selector('[data-testid="retweet"]')
                if rt:
                    retweets = self._parse_count(await rt.inner_text())
                lk = await element.query_selector('[data-testid="like"]')
                if lk:
                    likes = self._parse_count(await lk.inner_text())
            except:
                pass
            
            return {
                "id": tweet_id,
                "query_id": query['num'],
                "timestamp": timestamp,
                "user": username.split('\n')[0],
                "text": text,
                "lang": "en",
                "retweets": retweets,
                "likes": likes
            }
        except:
            return None
    
    def _parse_count(self, text: str) -> int:
        if not text:
            return 0
        text = text.strip().upper()
        try:
            if 'K' in text:
                return int(float(text.replace('K', '')) * 1000)
            elif 'M' in text:
                return int(float(text.replace('M', '')) * 1000000)
            return int(text)
        except:
            return 0
    
    async def collect_all_tweets(self):
        print("=" * 60)
        print("PHASE 1: COLLECTE DE TWEETS - THÈME: GUERRE EN IRAN")
        print("=" * 60)
        
        session_exists = os.path.exists(os.path.join(SESSION_DIR, "Default"))
        
        async with async_playwright() as p:
            print(f"\n🌐 Lancement du navigateur...")
            
            context = await p.chromium.launch_persistent_context(
                user_data_dir=SESSION_DIR,
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-first-run',
                    '--no-default-browser-check',
                ],
                viewport={'width': 1280, 'height': 800},
            )
            
            page = context.pages[0] if context.pages else await context.new_page()
            print("✅ Navigateur lancé!")
            
            await page.goto("https://x.com", timeout=30000)
            await page.wait_for_timeout(4000)
            
            # Vérifier si connecté
            current_url = page.url
            login_btn = await page.query_selector('a[href="/login"]')
            is_logged_in = not login_btn and ("home" in current_url or "/i/" in current_url or current_url == "https://x.com/")
            
            if not is_logged_in or not session_exists:
                print("\n" + "=" * 60)
                print("🔐 CONNEXION REQUISE - LISEZ ATTENTIVEMENT")
                print("=" * 60)
                print("")
                print("   ÉTAPES:")
                print("   1. Regardez le navigateur qui s'est ouvert")
                print("   2. Cliquez sur 'Se connecter' / 'Sign in'")
                print("   3. Entrez votre email et mot de passe X")
                print("   4. Attendez d'être sur votre FIL D'ACTUALITÉ")
                print("      (vous voyez des tweets de gens que vous suivez)")
                print("")
                print("   ⚠️  SEULEMENT APRÈS être connecté:")
                print("   → Revenez dans CE terminal")
                print("   → Appuyez sur ENTRÉE")
                print("=" * 60)
                input("\n>>> ENTRÉE SEULEMENT APRÈS CONNEXION COMPLÈTE <<<\n")
                
                # Attendre que la page se stabilise
                await page.wait_for_timeout(3000)
            else:
                print("\n✅ Déjà connecté à X!")
                input(">>> APPUYEZ SUR ENTRÉE POUR COMMENCER <<<\n")
            
            # Collecter les tweets
            for query in self.queries:
                tweets = await self.collect_tweets_for_query(page, query)
                self.all_tweets.extend(tweets)
            
            print("\n✅ Collecte terminée! Appuyez sur ENTRÉE pour fermer...")
            input()
            await context.close()
        
        print(f"\n📊 Total: {len(self.all_tweets)} tweets collectés")
    
    def save_tweets_json(self):
        output_file = self.output_dir / "tweets.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_tweets, f, indent=2, ensure_ascii=False)
        print(f"✅ Tweets sauvegardés: {output_file}")
    
    def save_queries(self):
        output_file = self.output_dir / "topics.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.queries, f, indent=2, ensure_ascii=False)
        print(f"✅ Requêtes sauvegardées: {output_file}")
    
    def generate_qrels(self):
        qrels_file = self.output_dir / "qrels.txt"
        with open(qrels_file, 'w') as f:
            for query in self.queries:
                query_tweets = [t for t in self.all_tweets if t['query_id'] == query['num']]
                for idx, tweet in enumerate(query_tweets):
                    relevance = 1 if idx < self.relevant_count else 0
                    f.write(f"{query['num']} 0 {tweet['id']} {relevance}\n")
        print(f"✅ Qrels sauvegardés: {qrels_file}")
    
    def generate_report(self):
        report_file = self.output_dir / "rapport_phase1.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("RAPPORT DE PHASE 1\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total tweets: {len(self.all_tweets)}\n\n")
            for query in self.queries:
                count = len([t for t in self.all_tweets if t['query_id'] == query['num']])
                f.write(f"  {query['num']}: {query['title']} → {count} tweets\n")
        print(f"✅ Rapport sauvegardé: {report_file}")


async def main():
    collector = IranWarTweetCollector(output_dir="phase1_output")
    await collector.collect_all_tweets()
    collector.save_tweets_json()
    collector.save_queries()
    collector.generate_qrels()
    collector.generate_report()
    
    print("\n" + "=" * 60)
    print("✅ PHASE 1 TERMINÉE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())