import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram API credentials
    API_ID = os.getenv('TELEGRAM_API_ID')
    API_HASH = os.getenv('TELEGRAM_API_HASH')
    PHONE = os.getenv('TELEGRAM_PHONE')
    
    # Collection settings
    RECON_LIST = 'reconlist.txt'

    # Conservative Telegram API pacing
    # realistically DO NOT CHANGE THESE VALUES 
    # UNLESS YOU ARE OKAY LOSING YOUR TG ACCOUNT.
    # These are very conservative and slow API 
    # requests because Telegram will ban if they have suspcious requests
    API_REQUEST_DELAY = 1.5
    MESSAGE_DELAY = 0.25
    CHANNEL_DELAY = 5
    FLOOD_WAIT_BUFFER = 5
    MAX_RATE_LIMIT_RETRIES = 3
    
    # Message limits
    MESSAGE_LIMITS = {
        '100': 100,
        '500': 500,
        '1000': 1000,
        '10000': 10000,
        '100000': 100000,
        'all': None
    }
    
    # Minimum share threshold
    MIN_SHARES = 1  # Configurable
    
    # Track both forwards AND original posts
    TRACK_FORWARDS_ONLY = False  # Set to True to only track forwarded messages
    
    # Output paths
    OUTPUT_DIR = 'output'
    SHARES_CSV = os.path.join(OUTPUT_DIR, 'telegram_shares.csv')
    MESSAGES_CSV = os.path.join(OUTPUT_DIR, 'messages_data.csv')
    ORIGINAL_POSTS_CSV = os.path.join(OUTPUT_DIR, 'original_posts.csv')
    
    # Language assets used by sentiment analysis and word clouds
    # For the lexicons you can theoretically add any language you want
    # but you will need to provide a lexicon in .txt, in .csv, as well as a stopword list 
    # of your own. see the main Read Me for more information
    LEXICON_DIR = 'lexicons'
    STOPWORDS_DIR = 'stopwords'
    FONT_DIR = 'fonts'
    TELEGRAM_MASK = 'telegram-mask.svg'
    LANGUAGE_FILES = {
        'arabic': ('Arabic-NRC-EmoLex.txt', 'arabic_stopwords.txt'),
        'belarusian': ('belarusian_lexicon.txt', 'belarusian_stopwords.txt'),
        #'croatian': ('croatian_lexicon.txt', None),
        #'czech': ('czech_lexicon.txt', None),
        #'danish': ('danish_lexicon.txt', None),
        #'dutch': ('dutch_lexicon.txt', None),
        'english': ('English-NRC-EmoLex.txt', 'english_stopwords.txt'),
        'finnish': ('finnish_lexicon.txt', 'finnish_stopwords.txt'),
        #'georgian': ('georgian_lexicon.txt', None),
        'german': ('german_lexicon.txt', 'german_stopwords.txt'),
        'hebrew': ('Hebrew-NRC-EmoLex.txt', 'hebrew_stopwords.txt'),
        #'hungarian': ('hungarian_lexicon.txt', None),
        #'lithuanian': ('lithuanian_lexicon.txt', None),
        #'norwegian': ('norwegian_lexicon.txt', None),
        'polish': ('polish_lexicon.txt', 'polish_stopwords.txt'),
        #'romanian': ('romanian_lexicon.txt', None),
        'russian': ('russian_lexicon.txt', 'russian_stopwords.txt'),
        #'serbian': ('serbian_lexicon.txt', None),
        #'slovak': ('slovak_lexicon.txt', None),
        #'slovenian': ('slovenian_lexicon.txt', None),
        'swedish': ('swedish_lexicon.txt', 'swedish_stopwords.txt'),
        #'tatar': ('tatar_lexicon.txt', None),
        'ukrainian': ('ukrainian_lexicon.txt', 'ukrainian_stopwords.txt'),
    }
    LANGUAGE_LEXICONS = {}
    LANGUAGE_STOPWORDS = {}


Config.LANGUAGE_LEXICONS = {
    language: os.path.join(Config.LEXICON_DIR, files[0])
    for language, files in Config.LANGUAGE_FILES.items()
}
Config.LANGUAGE_STOPWORDS = {
    language: os.path.join(Config.STOPWORDS_DIR, files[1])
    for language, files in Config.LANGUAGE_FILES.items()
    if files[1]
}