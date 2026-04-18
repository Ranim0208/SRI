"""
Configuration Phase 1 - Paramètres personnalisables
Modifiez ce fichier pour adapter le projet à vos besoins
"""

# ============================================================================
# CONFIGURATION DE COLLECTE
# ============================================================================

# Thème du projet
THEME = "Guerre en Iran"
THEME_ENGLISH = "Iran War"

# Dossier de sortie
OUTPUT_DIR = "phase1_output"

# Nombre de tweets à collecter par requête
TWEETS_PER_QUERY = 100

# Nombre de tweets considérés comme pertinents (top N)
RELEVANT_TWEETS_PER_QUERY = 30

# Nombre maximum de requêtes
MAX_QUERIES = 5

# ============================================================================
# REQUÊTES (TOPICS)
# ============================================================================

QUERIES = [
    {"num": "MB01", "title": "regime change Iran"},
    {"num": "MB02", "title": "regime collapse"},
    {"num": "MB03", "title": "Closing Hormuz strait"},
    {"num": "MB04", "title": "Intercepting missiles drones"},
    {"num": "MB05", "title": "revolutionary guard Iran"},
    
   
    # {"num": "MB06", "title": "We are much stronger"},
    # {"num": "MB07", "title": "Surrender on our terms"},
    # {"num": "MB08", "title": "Hitting US bases"},
    # {"num": "MB09", "title": "The supreme leader"},
    # {"num": "MB10", "title": "Zionist coalition"},
]

# ============================================================================
# CONFIGURATION PLAYWRIGHT
# ============================================================================

# Navigateur à utiliser (chromium, firefox, webkit)
BROWSER_TYPE = "chromium"

# Mode headless (True = pas de fenêtre visible, False = fenêtre visible)
HEADLESS_MODE = False

# Timeout pour charger les pages (en millisecondes)
PAGE_LOAD_TIMEOUT = 30000

# Délai entre les requêtes (en millisecondes)
DELAY_BETWEEN_QUERIES = 3000

# Délai entre les scroll (en millisecondes)
DELAY_BETWEEN_SCROLLS = 2000

# Délai avant d'extraire les tweets (en millisecondes)
INITIAL_WAIT_TIME = 3000

# ============================================================================
# CHAMPS DES TWEETS À EXTRAIRE
# ============================================================================

TWEET_FIELDS = [
    "id",           # ID unique du tweet
    "query_id",     # ID de la requête
    "timestamp",    # Horodatage
    "user",         # Nom d'utilisateur
    "text",         # Contenu du tweet
    "lang",         # Langue
    "retweets",     # Nombre de retweets
    "likes",        # Nombre de likes
]

# ============================================================================
# FORMATS DE SORTIE
# ============================================================================

# Générer les fichiers JSON
GENERATE_JSON = True

# Générer les fichiers CSV
GENERATE_CSV = True

# Générer les fichiers XML (topics)
GENERATE_XML = True

# Générer les rapports texte
GENERATE_REPORTS = True

# ============================================================================
# FILTRES ET VALIDATIONS
# ============================================================================

# Langue des tweets (vide = toutes les langues)
LANGUAGE_FILTER = ""  # "en" pour anglais seulement

# Filtrer les retweets (True = exclure les RT)
EXCLUDE_RETWEETS = False

# Longueur minimale du tweet (caractères)
MIN_TEXT_LENGTH = 10

# Permettre les doublons entre requêtes
ALLOW_DUPLICATES_ACROSS_QUERIES = False

# ============================================================================
# SÉLECTEURS CSS (Pour extraire les tweets)
# ============================================================================

# Sélecteur pour un article de tweet
TWEET_ARTICLE_SELECTOR = 'article[role="article"]'

# Sélecteur pour le texte du tweet
TWEET_TEXT_SELECTOR = '[data-testid="tweet"] span'

# Sélecteur pour le lien du tweet (contient l'ID)
TWEET_LINK_SELECTOR = 'a[href*="/status/"]'

# Sélecteur pour le nom d'utilisateur
TWEET_USER_SELECTOR = '[data-testid="User-Name"]'

# Sélecteur pour le timestamp
TWEET_TIME_SELECTOR = 'time'

# ============================================================================
# OPTIONS DE SCRAPING AVANCÉES
# ============================================================================

# Utiliser un proxy (laissez vide pour pas de proxy)
PROXY_URL = ""

# Utiliser des headers personnalisés
CUSTOM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Accepter les cookies automatiquement
AUTO_ACCEPT_COOKIES = True

# ============================================================================
# VALIDATION ET VÉRIFICATION
# ============================================================================

# Vérifier les doublons
CHECK_DUPLICATES = True

# Vérifier la cohérence des données
CHECK_CONSISTENCY = True

# Générer un rapport de validation
GENERATE_VALIDATION_REPORT = True

# ============================================================================
# LOGGING ET DEBUG
# ============================================================================

# Niveau de verbosité
VERBOSE = True

# Sauvegarder les logs
SAVE_LOGS = True

# Log file
LOG_FILE = "phase1.log"

# Afficher les erreurs détaillées
DEBUG_MODE = True

# ============================================================================
# EXPORT SUPPLÉMENTAIRES
# ============================================================================

# Créer un bundle d'exportation avec tous les formats
CREATE_EXPORT_BUNDLE = True

# Créer un fichier lisible d'échantillon
CREATE_SAMPLE_FILE = True

# Nombre de tweets dans le fichier d'échantillon
SAMPLE_SIZE = 10

# ============================================================================
# FIN DE CONFIGURATION
# ============================================================================

def print_config():
    """Affiche la configuration actuelle"""
    print("\n" + "=" * 60)
    print("CONFIGURATION PHASE 1")
    print("=" * 60)
    print(f"Thème: {THEME}")
    print(f"Requêtes: {len(QUERIES)}")
    print(f"Tweets par requête: {TWEETS_PER_QUERY}")
    print(f"Tweets pertinents: {RELEVANT_TWEETS_PER_QUERY}")
    print(f"Mode headless: {HEADLESS_MODE}")
    print(f"Dossier de sortie: {OUTPUT_DIR}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print_config()
