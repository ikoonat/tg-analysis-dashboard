"""
Reprocess Sentiment Analysis on Existing Collected Data
This script re-analyzes all your existing CSV files without collecting new data
"""

import pandas as pd
import os
import json
from tqdm import tqdm
from sentiment_analyzer import SentimentAnalyzer
from config import Config

class SentimentReprocessor:
    def __init__(self):
        self.config = Config()
        self.analyzer = SentimentAnalyzer(self.config)
        
    def should_skip_text(self, text):
        """Check if text should be skipped (only links, URLs, etc)"""
        if pd.isna(text) or not text or len(str(text).strip()) == 0:
            return True
        
        text = str(text).strip()
        
        # Skip if it's just a URL
        if text.startswith('http://') or text.startswith('https://'):
            return True
        
        # Skip if it's mostly URLs (more than 50% of content)
        url_chars = text.count('http://') + text.count('https://')
        if url_chars * 20 > len(text):  # Assuming avg URL is ~20 chars
            return True
        
        # Skip if too short (less than 5 characters after stripping URLs)
        text_without_urls = text
        for url_part in ['http://', 'https://', 'www.']:
            if url_part in text_without_urls:
                parts = text_without_urls.split(url_part)
                text_without_urls = parts[0]
        
        if len(text_without_urls.strip()) < 5:
            return True
        
        return False
    
    def clean_text_for_analysis(self, text):
        """Remove URLs from text before analysis"""
        import re
        
        if pd.isna(text):
            return ""
        
        text = str(text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        text = re.sub(r't\.me/\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        return text.strip()
    
    def reprocess_csv(self, input_file, output_file=None):
        """Reprocess a single CSV file"""
        
        if output_file is None:
            # Create backup and overwrite original
            backup_file = input_file.replace('.csv', '_backup.csv')
            output_file = input_file
        
        print(f"\n{'='*70}")
        print(f"Processing: {input_file}")
        print(f"{'='*70}")
        
        # Load CSV
        try:
            df = pd.read_csv(input_file, encoding='utf-8-sig')
        except Exception as e:
            print(f"❌ Error loading {input_file}: {e}")
            return None
        
        print(f"📊 Loaded {len(df)} rows")
        
        # Check if we have a Message_Text column
        if 'Message_Text' not in df.columns:
            print("⚠️  No Message_Text column found, skipping")
            return None
        
        # Initialize new columns
        df['Language_New'] = ''
        df['Emotions_New'] = ''
        df['Dominant_Emotion_New'] = ''
        df['Text_Skipped'] = False
        df['Skip_Reason'] = ''
        
        # Process each row
        skipped_count = 0
        processed_count = 0
        
        print(f"\n🔄 Reanalyzing sentiment...")
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):
            text = row['Message_Text']
            
            # Check if should skip
            if self.should_skip_text(text):
                df.at[idx, 'Text_Skipped'] = True
                df.at[idx, 'Skip_Reason'] = 'empty_or_links_only'
                skipped_count += 1
                continue
            
            # Clean text
            clean_text = self.clean_text_for_analysis(text)
            
            if len(clean_text) < 5:
                df.at[idx, 'Text_Skipped'] = True
                df.at[idx, 'Skip_Reason'] = 'too_short_after_cleaning'
                skipped_count += 1
                continue
            
            # Analyze sentiment
            try:
                sentiment = self.analyzer.analyze_sentiment(clean_text)
                
                df.at[idx, 'Language_New'] = sentiment['language']
                df.at[idx, 'Emotions_New'] = str(sentiment['emotions'])
                df.at[idx, 'Dominant_Emotion_New'] = sentiment['dominant_emotion'] or ''
                processed_count += 1
                
            except Exception as e:
                df.at[idx, 'Text_Skipped'] = True
                df.at[idx, 'Skip_Reason'] = f'error: {str(e)[:50]}'
                skipped_count += 1
        
        print(f"\n✓ Processed: {processed_count}")
        print(f"⊘ Skipped: {skipped_count}")
        
        # Replace old columns with new ones
        if 'Language' in df.columns:
            df['Language_Old'] = df['Language']
        df['Language'] = df['Language_New']
        
        if 'Emotions' in df.columns:
            df['Emotions_Old'] = df['Emotions']
        df['Emotions'] = df['Emotions_New']
        
        if 'Dominant_Emotion' in df.columns:
            df['Dominant_Emotion_Old'] = df['Dominant_Emotion']
        df['Dominant_Emotion'] = df['Dominant_Emotion_New']
        
        # Drop temporary columns
        df = df.drop(columns=['Language_New', 'Emotions_New', 'Dominant_Emotion_New'])
        
        # Save
        print(f"💾 Saving to {output_file}...")
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"✓ Done!")
        
        return df
    
    def reprocess_all(self):
        """Reprocess all CSV files in output directory"""
        
        print("="*70)
        print("SENTIMENT REPROCESSING - ALL FILES")
        print("="*70)
        print()
        
        files_to_process = []
        
        # Main CSV files
        main_files = [
            'output/messages_data.csv',
            'output/original_posts.csv',
        ]
        
        for file in main_files:
            if os.path.exists(file):
                files_to_process.append(file)
        
        # Per-channel CSV files
        per_channel_dir = 'output/per_channel'
        if os.path.exists(per_channel_dir):
            for filename in os.listdir(per_channel_dir):
                if filename.endswith('.csv') and not filename.startswith('_'):
                    filepath = os.path.join(per_channel_dir, filename)
                    files_to_process.append(filepath)
        
        print(f"Found {len(files_to_process)} files to process")
        print()
        
        # Process each file
        results = {}
        for filepath in files_to_process:
            result_df = self.reprocess_csv(filepath)
            if result_df is not None:
                results[filepath] = result_df
        
        # Generate new summary statistics
        print("\n" + "="*70)
        print("REGENERATING CHANNEL SUMMARIES")
        print("="*70)
        
        self.regenerate_summaries()
        
        print("\n" + "="*70)
        print("REPROCESSING COMPLETE!")
        print("="*70)
        print(f"✓ Processed {len(results)} files")
        print()
        print("📊 Statistics:")
        total_processed = sum(len(df[~df['Text_Skipped']]) for df in results.values() if 'Text_Skipped' in df.columns)
        total_skipped = sum(len(df[df['Text_Skipped']]) for df in results.values() if 'Text_Skipped' in df.columns)
        print(f"   Messages analyzed: {total_processed}")
        print(f"   Messages skipped: {total_skipped}")
    
    def regenerate_summaries(self):
        """Regenerate channel summary JSON files"""
        
        per_channel_dir = 'output/per_channel'
        if not os.path.exists(per_channel_dir):
            return
        
        for filename in os.listdir(per_channel_dir):
            if filename.endswith('.csv') and not filename.startswith('_'):
                csv_path = os.path.join(per_channel_dir, filename)
                json_path = csv_path.replace('.csv', '_summary.json')
                
                try:
                    df = pd.read_csv(csv_path, encoding='utf-8-sig')
                    
                    # Calculate summary
                    summary = {
                        'Channel_Username': df['Channel_Username'].iloc[0] if 'Channel_Username' in df.columns else 'Unknown',
                        'Channel_Name': df['Channel_Name'].iloc[0] if 'Channel_Name' in df.columns else 'Unknown',
                        'Total_Messages': len(df),
                        'Forwarded_Messages': len(df[df['Is_Forward'] == True]) if 'Is_Forward' in df.columns else 0,
                        'Original_Posts': len(df[df['Is_Forward'] == False]) if 'Is_Forward' in df.columns else len(df),
                        'Total_Views': int(df['Views'].sum()) if 'Views' in df.columns else 0,
                        'Total_Forwards': int(df['Forwards'].sum()) if 'Forwards' in df.columns else 0,
                        'Avg_Views': float(df['Views'].mean()) if 'Views' in df.columns else 0,
                        'Avg_Forwards': float(df['Forwards'].mean()) if 'Forwards' in df.columns else 0,
                        'Languages': df['Language'].value_counts().to_dict() if 'Language' in df.columns else {},
                        'Dominant_Emotions': df['Dominant_Emotion'].value_counts().head(10).to_dict() if 'Dominant_Emotion' in df.columns else {},
                        'Date_Range': f"{df['Message_Date'].min()} to {df['Message_Date'].max()}" if 'Message_Date' in df.columns else 'Unknown'
                    }
                    
                    # Save JSON
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
                    
                    print(f"✓ Updated summary: {json_path}")
                    
                except Exception as e:
                    print(f"❌ Error generating summary for {filename}: {e}")
    
    def compare_old_vs_new(self, csv_file):
        """Compare old vs new sentiment analysis results"""
        
        print(f"\n{'='*70}")
        print(f"COMPARISON: Old vs New Sentiment Analysis")
        print(f"File: {csv_file}")
        print(f"{'='*70}\n")
        
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        if 'Language_Old' not in df.columns:
            print("No old data to compare (Language_Old column not found)")
            return
        
        # Language changes
        print("📊 Language Detection Changes:")
        lang_changes = df[df['Language_Old'] != df['Language']]
        print(f"   Total changes: {len(lang_changes)} ({len(lang_changes)/len(df)*100:.1f}%)")
        
        if len(lang_changes) > 0:
            print("\n   Sample changes:")
            for idx, row in lang_changes.head(10).iterrows():
                print(f"   {row['Language_Old']} → {row['Language']}: {row['Message_Text'][:50]}...")
        
        # Emotion changes
        print("\n😊 Dominant Emotion Changes:")
        emotion_changes = df[df['Dominant_Emotion_Old'] != df['Dominant_Emotion']]
        print(f"   Total changes: {len(emotion_changes)} ({len(emotion_changes)/len(df)*100:.1f}%)")
        
        # Show emotion distribution comparison
        print("\n   Old emotion distribution:")
        old_emotions = df['Dominant_Emotion_Old'].value_counts().head(5)
        for emotion, count in old_emotions.items():
            print(f"      {emotion}: {count}")
        
        print("\n   New emotion distribution:")
        new_emotions = df['Dominant_Emotion'].value_counts().head(5)
        for emotion, count in new_emotions.items():
            print(f"      {emotion}: {count}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    import sys
    
    print("="*70)
    print("TELEGRAM COLLECTOR - SENTIMENT REPROCESSING")
    print("="*70)
    print()
    print("This will re-analyze sentiment for all existing collected data")
    print("⚠️  This will overwrite existing Language/Emotions columns")
    print("    (Old values will be saved as Language_Old, etc.)")
    print()
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled")
        return
    
    reprocessor = SentimentReprocessor()
    
    if len(sys.argv) > 1:
        # Process specific file
        filepath = sys.argv[1]
        reprocessor.reprocess_csv(filepath)
        
        # Show comparison
        response = input("\nShow old vs new comparison? (y/n): ")
        if response.lower() == 'y':
            reprocessor.compare_old_vs_new(filepath)
    else:
        # Process all files
        reprocessor.reprocess_all()

if __name__ == '__main__':
    main()


# ============================================================================
# QUICK SCRIPTS
# ============================================================================

# Quick script 1: Just reprocess messages_data.csv
def reprocess_messages_only():
    """Quick script to reprocess just messages_data.csv"""
    reprocessor = SentimentReprocessor()
    reprocessor.reprocess_csv('output/messages_data.csv')
    print("\n✓ Done! Check output/messages_data.csv")

# Quick script 2: Reprocess and show comparison
def reprocess_and_compare():
    """Reprocess and show before/after comparison"""
    reprocessor = SentimentReprocessor()
    reprocessor.reprocess_csv('output/messages_data.csv')
    reprocessor.compare_old_vs_new('output/messages_data.csv')

# Quick script 3: Process specific channel
def reprocess_channel(channel_username):
    """Reprocess specific channel"""
    import re
    safe_username = re.sub(r'[^\w\-_]', '_', channel_username)
    filepath = f'output/per_channel/{safe_username}.csv'
    
    reprocessor = SentimentReprocessor()
    reprocessor.reprocess_csv(filepath)
    reprocessor.compare_old_vs_new(filepath)