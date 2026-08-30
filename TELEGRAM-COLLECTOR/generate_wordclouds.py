"""
Generate word clouds from existing CSV data
Run this script after data collection to create word clouds
"""

import pandas as pd
import os
import re
from config import Config
from sentiment_analyzer import SentimentAnalyzer

def generate_wordclouds_from_csv():
    """Generate word clouds from messages CSV"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    config = Config()
    analyzer = SentimentAnalyzer(config)
    
    # Load messages CSV
    messages_csv = config.MESSAGES_CSV
    
    if not os.path.exists(messages_csv):
        print(f"Error: {messages_csv} not found!")
        print("Make sure you've run the collector first.")
        return
    
    print(f"Loading data from {messages_csv}...")
    messages_df = pd.read_csv(messages_csv, encoding='utf-8-sig')
    
    if messages_df.empty:
        print("No messages found in CSV!")
        return
    
    print(f"Loaded {len(messages_df)} messages")
    
    # Check if required columns exist
    required_columns = ['Message_Text', 'Language', 'Channel_Username']
    missing = [col for col in required_columns if col not in messages_df.columns]
    
    if missing:
        print(f"Error: Missing required columns: {missing}")
        return

    messages_df['Language'] = (
        messages_df['Language'].astype(str).str.strip().str.lower()
    )
    
    # Color schemes for variety
    color_schemes = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']

    print("\nWord-cloud shape:")
    print("1 = normal, 2 = perfect circle, 3 = Telegram mask")
    mask_choice = input("Choose shape (default: 1): ").strip() or "1"
    mask_mode = {'1': 'none', '2': 'circle', '3': 'telegram'}.get(mask_choice, 'none')
    
    # ============================================================================
    # Generate OVERALL word clouds by language
    # ============================================================================
    print("\n" + "="*60)
    print("GENERATING OVERALL WORD CLOUDS BY LANGUAGE")
    print("="*60)
    
    for idx, language in enumerate(config.LANGUAGE_FILES):
        print(f"\nProcessing {language}...")
        
        # Filter messages by language
        lang_messages = messages_df[messages_df['Language'] == language]
        
        if lang_messages.empty or len(lang_messages) == 0:
            print(f"  ✗ No {language} messages found")
            continue
        
        # Get all text
        texts = lang_messages['Message_Text'].dropna().tolist()
        
        if not texts:
            print(f"  ✗ No text found for {language}")
            continue
        
        print(f"  Found {len(texts)} {language} messages")
        
        # Use different colormap for each language
        colormap = color_schemes[idx % len(color_schemes)]
        
        # Output path
        output_path = os.path.join(
            config.OUTPUT_DIR,
            f'wordcloud_{language}.png'
        )
        
        # Generate word cloud
        try:
            title = f'{language.title()} - All Channels ({len(texts)} messages)'
            analyzer.generate_wordcloud(texts, output_path, language, colormap, title, mask_mode)
            print(f"  ✓ Generated {language} word cloud")
        except Exception as e:
            print(f"  ✗ Error generating {language} word cloud: {e}")
    
    # ============================================================================
    # Generate PER-CHANNEL word clouds (one per channel, primary language)
    # ============================================================================
    print("\n" + "="*60)
    print("GENERATING PER-CHANNEL WORD CLOUDS")
    print("="*60)
    
    # Create per_channel directory
    per_channel_dir = os.path.join(config.OUTPUT_DIR, 'per_channel')
    os.makedirs(per_channel_dir, exist_ok=True)
    
    # Get channel counts
    channel_counts = messages_df['Channel_Username'].value_counts()
    
    print(f"\nFound {len(channel_counts)} channels")
    print(f"Processing channels with 5+ messages...\n")
    
    generated_count = 0
    skipped_count = 0
    
    for idx, channel_username in enumerate(channel_counts.index):
        if pd.isna(channel_username):
            continue
        
        # Get all messages for this channel
        channel_data = messages_df[messages_df['Channel_Username'] == channel_username]
        
        # Skip if too few messages
        if len(channel_data) < 5:
            skipped_count += 1
            continue
        
        # Determine primary language for this channel
        language_counts = channel_data['Language'].value_counts()
        
        if language_counts.empty:
            print(f"  ✗ {channel_username}: No language data")
            skipped_count += 1
            continue
        
        primary_language = language_counts.index[0]  # Most common language
        
        # Filter to only messages in primary language
        lang_channel_data = channel_data[channel_data['Language'] == primary_language]
        texts = lang_channel_data['Message_Text'].dropna().tolist()
        
        if not texts or len(texts) < 3:
            print(f"  ✗ {channel_username}: Insufficient {primary_language} text ({len(texts)} msgs)")
            skipped_count += 1
            continue
        
        # Use different colormap for variety
        colormap = color_schemes[idx % len(color_schemes)]
        
        # Clean filename
        safe_username = re.sub(r'[^\w\-_]', '_', str(channel_username))
        output_path = os.path.join(
            per_channel_dir,
            f'wordcloud_{safe_username}_{primary_language}.png'
        )
        
        # Create title with channel name and language
        channel_name = channel_data['Channel_Name'].iloc[0] if 'Channel_Name' in channel_data.columns else channel_username
        title = f'{channel_username}\n({primary_language.title()}, {len(texts)} messages)'
        
        # Generate word cloud
        try:
            analyzer.generate_wordcloud(texts, output_path, primary_language, colormap, title, mask_mode)
            print(f"  ✓ {channel_username} ({primary_language}, {len(texts)} msgs)")
            generated_count += 1
        except Exception as e:
            print(f"  ✗ {channel_username}: Error - {e}")
            skipped_count += 1
    
    # ============================================================================
    # Summary
    # ============================================================================
    print("\n" + "="*60)
    print("WORD CLOUD GENERATION COMPLETE")
    print("="*60)
    print(f"Per-channel word clouds generated: {generated_count}")
    print(f"Channels skipped (too few messages): {skipped_count}")
    print(f"\nOutput directory: {config.OUTPUT_DIR}")
    print(f"Per-channel directory: {per_channel_dir}")
    print("="*60 + "\n")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("WORD CLOUD GENERATOR FROM CSV")
    print("="*60 + "\n")
    
    print("This script will generate word clouds from your collected data.")
    print("Make sure you have already run the collector and have a messages CSV file.\n")
    
    try:
        input("Press Enter to continue...")
    except EOFError:
        # Handle case where input() fails in some environments
        print("Continuing automatically...")
    
    try:
        generate_wordclouds_from_csv()
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")


if __name__ == '__main__':
    print("Script starting...")  # Debug line
    main()
    print("\nScript finished!")
    input("Press Enter to exit...")