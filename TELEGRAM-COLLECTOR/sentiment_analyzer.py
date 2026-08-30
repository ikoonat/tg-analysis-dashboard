import re
import os
import io
from glob import glob
import hashlib
import random
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display
import emoji
from PIL import Image, ImageDraw, ImageFont
import cairosvg
import numpy as np

class SentimentAnalyzer:
    GOOGLE_FONT_FALLBACKS = {
        'arabic': ['Noto Naskh Arabic', 'Amiri', 'Cairo', 'Lateef'],
        'hebrew': ['Noto Sans Hebrew', 'Rubik', 'Assistant', 'Open Sans'],
        'russian': ['Roboto', 'Noto Sans', 'Open Sans', 'Inter'],
        'ukrainian': ['Rubik', 'Montserrat', 'Roboto', 'Manrope'],
        'polish': ['Lato', 'Poppins', 'Montserrat', 'Roboto'],
        'german': ['Montserrat', 'Open Sans', 'Roboto', 'Lato'],
        'finnish': ['Roboto', 'Montserrat', 'Noto Sans', 'Open Sans'],
        'swedish': ['Roboto', 'Montserrat', 'Noto Sans', 'Open Sans'],
        'belarusian': ['Roboto', 'Noto Sans', 'Open Sans', 'Inter'],
        'english': ['Roboto', 'Open Sans', 'Lato', 'Montserrat'],
        'latin': ['Roboto', 'Open Sans', 'Lato', 'Montserrat'],
    }

    LANGUAGE_HINTS = {
        'polish': {'jestem', 'bardzo', 'nie', 'się', 'szczęśliwy', 'szczęśliwa'},
        'english': {'the', 'and', 'with', 'this', 'that', 'very'},
        'finnish': {'olen', 'erittäin', 'että', 'ja', 'on', 'minä'},
        'swedish': {'jag', 'är', 'och', 'inte', 'det', 'som'},
        'russian': {'я', 'очень', 'что', 'это', 'и', 'не'},
        'ukrainian': {'я', 'дуже', 'що', 'це', 'і', 'не'},
        'german': {'ich', 'bin', 'sehr', 'und', 'nicht', 'das'},
    }

    def __init__(self, config):
        self.config = config
        self.lexicons = self._load_lexicons()
        self.stopwords = self._load_stopwords()
    
    def _load_lexicons(self):
        """Load NRC EmoLex lexicons for multiple languages"""
        lexicons = {language: {} for language in self.config.LANGUAGE_FILES}
        
        # Emotion column mapping for matrix format
        emotion_columns = {
            1: 'anger', 2: 'anticipation', 3: 'disgust', 4: 'fear', 
            5: 'joy', 6: 'negative', 7: 'positive', 8: 'sadness', 
            9: 'surprise', 10: 'trust'
        }
        
        for lang, path in self.config.LANGUAGE_LEXICONS.items():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                    # Skip if file is empty
                    if not lines:
                        continue
                    
                    # Check format by looking at first data line (skip header)
                    first_line = lines[1].strip() if len(lines) > 1 else ""
                    parts = first_line.split('\t')
                    
                    # Detect format: matrix (12 columns) or standard (3 columns)
                    is_matrix_format = len(parts) >= 12
                    
                    for line_num, line in enumerate(lines, 1):
                        line = line.strip()
                        
                        # Skip empty lines and header
                        if not line or line_num == 1:
                            continue
                        
                        parts = line.split('\t')
                        
                        if is_matrix_format and len(parts) >= 12:
                            # Matrix format: English Word | emotions (0/1) | Hebrew/Arabic Word
                            english_word = parts[0].strip().lower()
                            foreign_word = parts[11].strip().lower()
                            
                            # Process emotions (columns 1-10)
                            for col_idx, emotion in emotion_columns.items():
                                try:
                                    score = int(parts[col_idx].strip())
                                    if score == 1:
                                        if english_word and lang == 'english':
                                            lexicons['english'].setdefault(english_word, []).append(emotion)
                                        
                                        # Add to target language lexicon
                                        if foreign_word and foreign_word != english_word:
                                            lexicons[lang].setdefault(foreign_word, []).append(emotion)
                                except (ValueError, IndexError):
                                    continue
                        
                        elif len(parts) >= 3:
                            # Standard format: word | emotion | score
                            word = parts[0].strip().lower()
                            emotion = parts[1].strip()
                            
                            try:
                                score = int(parts[2].strip())
                                if score == 1:
                                    if word not in lexicons[lang]:
                                        lexicons[lang][word] = []
                                    lexicons[lang][word].append(emotion)
                            except (ValueError, IndexError):
                                continue
                                
            except FileNotFoundError:
                print(f"Warning: {path} not found - sentiment analysis will be limited for {lang}")
            except Exception as e:
                print(f"Warning: Error loading {path}: {e}")
        
        # Report loaded lexicon sizes
        for lang in lexicons:
            if lexicons[lang]:
                print(f"Loaded {len(lexicons[lang])} words for {lang} sentiment analysis")
        
        return lexicons
    
    def _load_stopwords(self):
        """Load stopwords for multiple languages"""
        stopwords = {language: set() for language in self.config.LANGUAGE_FILES}
        
        for lang, path in self.config.LANGUAGE_STOPWORDS.items():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    stopwords[lang] = {line.strip().lower() for line in f if line.strip()}
            except FileNotFoundError:
                print(f"Warning: {path} not found")
        
        return stopwords
    
    def detect_language(self, text):
        """Detect language using script hints and language asset matches."""
        if not text:
            return 'english'

        tokens = self._tokenize(text)
        script_counts = {
            'arabic': len(re.findall(r'[\u0600-\u06FF]', text)),
            'hebrew': len(re.findall(r'[\u0590-\u05FF]', text)),
            'georgian': len(re.findall(r'[\u10A0-\u10FF]', text)),
            'cyrillic': len(re.findall(r'[\u0400-\u04FF]', text)),
        }
        if script_counts['arabic'] > 0:
            return 'arabic'
        if script_counts['hebrew'] > 0:
            return 'hebrew'
        if script_counts['georgian'] > 0:
            return 'georgian'

        normalized_text = set(tokens)
        hint_scores = {
            language: len(normalized_text & hints)
            for language, hints in self.LANGUAGE_HINTS.items()
        }
        best_hint_language, best_hint_score = max(
            hint_scores.items(), key=lambda item: item[1]
        )
        if best_hint_score:
            return best_hint_language

        scores = {}
        for language, lexicon in self.lexicons.items():
            matches = sum(token in lexicon for token in tokens)
            stopword_matches = sum(token in self.stopwords[language] for token in tokens)
            scores[language] = matches * 3 + stopword_matches

        best_language, best_score = max(scores.items(), key=lambda item: item[1])
        if best_score:
            return best_language
        if script_counts['cyrillic'] > 0:
            return 'russian'
        return 'english'

    def _tokenize(self, text):
        """Return Unicode letter tokens while preserving accents and scripts."""
        text = re.sub(r'http\S+|www\S+', '', text)
        text = re.sub(r'@\w+|#\w+', '', text)
        text = emoji.replace_emoji(text, '')
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)
        return [token.lower() for token in text.split() if len(token) >= 2]
    
    def clean_text(self, text, language):
        """Clean and tokenize text"""
        if not text:
            return []
        
        tokens = self._tokenize(text)
        
        # Remove stopwords
        stopwords = self.stopwords.get(language, set())
        tokens = [t for t in tokens if t not in stopwords]
        
        return tokens
    
    def analyze_sentiment(self, text):
        """Analyze sentiment using Plutchik's wheel emotions"""
        language = self.detect_language(text)
        tokens = self.clean_text(text, language)
        
        emotions = []
        for token in tokens:
            if token in self.lexicons[language]:
                emotions.extend(self.lexicons[language][token])
        
        emotion_counts = Counter(emotions)
        
        return {
            'language': language,
            'emotions': dict(emotion_counts),
            'tokens': tokens,
            'dominant_emotion': emotion_counts.most_common(1)[0][0] if emotion_counts else None
        }
    
    def generate_wordcloud(self, texts, output_path, language='english', colormap=None,
                           title=None, mask_mode='none'):
        """Generate word cloud from texts with proper RTL support"""
        all_tokens = []
        for text in texts:
            tokens = self.clean_text(text, language)
            all_tokens.extend(tokens)
        
        if not all_tokens:
            print(f"No tokens found for {language} word cloud")
            return
        
        text_for_cloud = ' '.join(all_tokens)
        
        # Color palettes - cycle through these
        color_palettes = [
            'viridis',      # Blue-green-yellow
            'plasma',       # Purple-pink-yellow
            'inferno',      # Black-red-yellow
            'magma',        # Black-purple-white
            'cividis',      # Blue-yellow (colorblind friendly)
            'twilight',     # Purple-pink-blue
            'ocean',        # Blue gradient
            'RdYlBu',       # Red-Yellow-Blue
            'Spectral',     # Rainbow
            'coolwarm',     # Blue-red
        ]
        
        # Use provided colormap or pick one based on language
        if colormap is None:
            if language == 'arabic':
                colormap = color_palettes[1]  # plasma
            elif language == 'hebrew':
                colormap = color_palettes[0]  # viridis
            else:
                colormap = color_palettes[2]  # inferno
        
        font_paths = self._find_fonts(language)
        font_path = self._pick_random_font(font_paths, output_path) if font_paths else None
        fallback_fonts = self._google_font_fallbacks(language)
        mask = self._build_mask(mask_mode)

        # Special handling for RTL languages
        if language in ['arabic', 'hebrew']:
            # CRITICAL FIX: Reshape RTL text for proper display
            try:
                # Reshape and reorder the text for RTL display
                reshaped_text = arabic_reshaper.reshape(text_for_cloud)
                bidi_text = get_display(reshaped_text)
                text_for_cloud = bidi_text
            except Exception as e:
                print(f"Warning: RTL reshaping failed for {language}: {e}")
                print("Continuing with original text...")
            
            # Create word cloud with RTL support and transparent background
            wordcloud = WordCloud(
                width=1000,
                height=1000,
                background_color=None,
                mode='RGBA',
                font_path=font_path,
                relative_scaling=0.5,
                min_font_size=10,
                max_words=100,
                colormap=colormap,
                # Important: Don't let WordCloud normalize the text
                regexp=r'\S+',  # Match any non-whitespace as a word
                mask=mask,
            ).generate(text_for_cloud)
        else:
            wordcloud = WordCloud(
                width=1000,
                height=1000,
                background_color=None,
                mode='RGBA',
                relative_scaling=0.5,
                min_font_size=10,
                max_words=100,
                colormap=colormap,
                font_path=font_path,
                mask=mask,
            ).generate(text_for_cloud)
        
        # Draw each word with a separately selected font from the language folder.
        image = self._render_wordcloud(wordcloud, font_paths, output_path)

        # Create figure with transparent background
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.imshow(image, interpolation='bilinear')
        ax.axis('off')
        
        # Add title if provided
        if title:
            # For RTL languages, reshape the title too
            if language in ['arabic', 'hebrew'] and any(c >= '\u0590' for c in title):
                try:
                    reshaped_title = arabic_reshaper.reshape(title)
                    title = get_display(reshaped_title)
                except:
                    pass  # Use original title if reshaping fails
            
            ax.set_title(title, fontsize=16, pad=20, fontweight='bold')
        
        # Save with transparent background
        plt.tight_layout(pad=0)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        plt.savefig(output_path, dpi=100, bbox_inches='tight', 
                   facecolor='none', edgecolor='none', transparent=True)
        plt.close()
        
        print(f"Word cloud saved to {output_path} (colormap: {colormap}, language: {language})")

    def _google_font_fallbacks(self, language):
        """Return a simple Google Fonts fallback list for the requested language."""
        normalized = (language or 'latin').lower()
        return self.GOOGLE_FONT_FALLBACKS.get(normalized, self.GOOGLE_FONT_FALLBACKS['latin'])

    def _pick_random_font(self, font_paths, output_path):
        """Choose a deterministic random font from the available local paths."""
        if not font_paths:
            return None
        seed = int(hashlib.sha256((output_path or str(font_paths)).encode('utf-8')).hexdigest(), 16)
        return random.Random(seed).choice(font_paths)

    def _find_fonts(self, language):
        """Find fonts from ./TELEGRAM-COLLECTOR/fonts/{language}/ and fall back gracefully."""
        project_root = os.path.dirname(os.path.abspath(__file__))
        font_root = os.path.join(project_root, self.config.FONT_DIR)
        language_dir = os.path.join(font_root, (language or 'latin').lower())

        local_fonts = []
        if os.path.isdir(language_dir):
            for extension in ('*.ttf', '*.otf'):
                local_fonts.extend(glob(os.path.join(language_dir, extension)))
        if local_fonts:
            return sorted(local_fonts)

        for extension in ('*.ttf', '*.otf'):
            local_fonts.extend(glob(os.path.join(font_root, '**', extension), recursive=True))

        language_fonts = [
            path for path in local_fonts
            if os.path.basename(os.path.dirname(path)).lower() == (language or 'latin').lower()
        ]
        if language_fonts:
            return sorted(language_fonts)

        latin_languages = {
            'belarusian', 'croatian', 'czech', 'danish', 'dutch', 'english',
            'finnish', 'german', 'hungarian', 'lithuanian', 'norwegian',
            'polish', 'romanian', 'serbian', 'slovak', 'slovenian', 'swedish',
        }
        if language in latin_languages:
            latin_fonts = [
                path for path in local_fonts
                if os.path.basename(os.path.dirname(path)).lower() == 'latin'
            ]
            if latin_fonts:
                return sorted(latin_fonts)

        # Avoid hard-coded Windows paths in the repo. The project should rely on
        # local language folders (./fonts/{language}) and generic platform fonts,
        # or simply skip custom font loading when no project fonts are available.
        generic_font_candidates = []
        for base_dir in (
            '/usr/share/fonts',
            '/usr/local/share/fonts',
            '/System/Library/Fonts',
            '/Library/Fonts',
            os.path.expanduser('~/.fonts'),
            os.path.expanduser('~/Library/Fonts'),
        ):
            if os.path.isdir(base_dir):
                for extension in ('*.ttf', '*.otf'):
                    generic_font_candidates.extend(glob(os.path.join(base_dir, '**', extension), recursive=True))

        if generic_font_candidates:
            return sorted(set(generic_font_candidates))

        return []

    def _build_mask(self, mask_mode):
        """Create a WordCloud mask with black usable areas and white blocked areas."""
        if mask_mode == 'none':
            return None

        size = 1000
        if mask_mode == 'circle':
            y, x = np.ogrid[:size, :size]
            center = (size - 1) / 2
            radius = (size - 1) / 2 - 12
            return np.where((x - center) ** 2 + (y - center) ** 2 <= radius ** 2, 0, 255).astype(np.uint8)

        if mask_mode == 'telegram':
            svg_path = os.path.join(self.config.TELEGRAM_MASK)
            if not os.path.exists(svg_path):
                raise FileNotFoundError(f"Telegram mask not found: {svg_path}")
            png_bytes = cairosvg.svg2png(url=svg_path, output_width=size, output_height=size)
            image = Image.open(io.BytesIO(png_bytes)).convert('RGBA')
            alpha = np.asarray(image)[..., 3]
            return np.where(alpha > 0, 0, 255).astype(np.uint8)

        raise ValueError(f"Unknown word-cloud mask: {mask_mode}")

    def _render_wordcloud(self, wordcloud, font_paths, output_path):
        """Render the layout with a stable random font choice for each word."""
        if not font_paths:
            return wordcloud.to_image()

        image = Image.new(
            wordcloud.mode,
            (int(wordcloud.width * wordcloud.scale), int(wordcloud.height * wordcloud.scale)),
            wordcloud.background_color,
        )
        draw = ImageDraw.Draw(image)
        seed = int(hashlib.sha256(output_path.encode('utf-8')).hexdigest(), 16)
        generator = random.Random(seed)

        for (word, count), font_size, position, orientation, color in wordcloud.layout_:
            font_path = generator.choice(font_paths)
            font = ImageFont.truetype(font_path, int(font_size * wordcloud.scale))
            transposed_font = ImageFont.TransposedFont(font, orientation=orientation)
            pos = (
                int(position[1] * wordcloud.scale),
                int(position[0] * wordcloud.scale),
            )
            draw.text(pos, word, fill=color, font=transposed_font)

        return image