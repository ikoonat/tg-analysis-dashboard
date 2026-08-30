import asyncio
import argparse
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors import ChannelPrivateError, UsernameNotOccupiedError, FloodWaitError
from datetime import datetime
import os
import re
import pandas as pd
import signal
import gc  # Garbage collection for memory management
import sys
from config import Config
from sentiment_analyzer import SentimentAnalyzer
from data_processor import DataProcessor

class TelegramCollector:
    def __init__(self):
        self.config = Config()
        self.client = TelegramClient('session_name', self.config.API_ID, self.config.API_HASH)
        self.analyzer = SentimentAnalyzer(self.config)
        self.processor = DataProcessor(self.config)
        self.visited_channels = set()
        self.should_stop = False
        self.messages_since_save = 0
        self.auto_save_interval = 500  # Auto-save every 500 messages
        self._last_api_request = 0.0
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n⚠ Interrupt received! Saving data before exit...")
        self.should_stop = True
    
    async def auto_save_progress(self):
        """Save progress periodically"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.processor.shares_data or self.processor.messages_data or self.processor.original_posts_data:
            print(f"\n💾 Auto-saving progress... ({len(self.processor.messages_data)} messages collected)")
            
            # Create backup directory
            backup_dir = os.path.join(self.config.OUTPUT_DIR, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Save with timestamp - use chunking for large datasets
            if self.processor.shares_data:
                backup_file = os.path.join(backup_dir, f'shares_backup_{timestamp}.csv')
                df = pd.DataFrame(self.processor.shares_data)
                df.to_csv(backup_file, index=False, encoding='utf-8-sig', chunksize=1000)
                del df  # Free memory
            
            if self.processor.messages_data:
                backup_file = os.path.join(backup_dir, f'messages_backup_{timestamp}.csv')
                df = pd.DataFrame(self.processor.messages_data)
                df.to_csv(backup_file, index=False, encoding='utf-8-sig', chunksize=1000)
                del df  # Free memory
            
            if self.processor.original_posts_data:
                backup_file = os.path.join(backup_dir, f'original_backup_{timestamp}.csv')
                df = pd.DataFrame(self.processor.original_posts_data)
                df.to_csv(backup_file, index=False, encoding='utf-8-sig', chunksize=1000)
                del df  # Free memory
            
            # Force garbage collection to free memory
            gc.collect()
            
            print(f"✓ Progress saved to backups/ folder")
            self.messages_since_save = 0
        
    async def start(self):
        """Initialize Telegram client"""
        await self.client.start(phone=self.config.PHONE)
        print("Connected to Telegram")

    async def _wait_before_api_request(self):
        """Keep direct Telegram requests spaced apart."""
        now = asyncio.get_running_loop().time()
        wait_time = self.config.API_REQUEST_DELAY - (now - self._last_api_request)
        if wait_time > 0:
            await self._sleep_with_stop(wait_time)
        self._last_api_request = asyncio.get_running_loop().time()

    async def _sleep_with_stop(self, seconds):
        """Sleep in short intervals so Ctrl+C can stop a long wait."""
        remaining = seconds
        while remaining > 0 and not self.should_stop:
            interval = min(remaining, 1)
            await asyncio.sleep(interval)
            remaining -= interval

    async def _wait_for_flood(self, seconds, reason):
        """Honor Telegram's requested wait and add a safety buffer."""
        total_wait = seconds + self.config.FLOOD_WAIT_BUFFER
        print(f"Telegram rate limit ({reason}). Waiting {total_wait} seconds...")
        await self._sleep_with_stop(total_wait)
    
    def load_recon_list(self):
        """Load initial channels from reconlist.txt"""
        try:
            with open(self.config.RECON_LIST, 'r', encoding='utf-8') as f:
                channels = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(channels)} channels from {self.config.RECON_LIST}")
            return channels
        except FileNotFoundError:
            print(f"Error: {self.config.RECON_LIST} not found")
            return []
    
    async def get_channel_info(self, username):
        """Get channel information with rate limit handling"""
        if self.should_stop:
            return None

        username = username.lstrip('@')
        for attempt in range(self.config.MAX_RATE_LIMIT_RETRIES + 1):
            try:
                await self._wait_before_api_request()
                entity = await self.client.get_entity(username)
                await self._wait_before_api_request()
                await self.client(GetFullChannelRequest(entity))

                return {
                    'id': entity.id,
                    'username': username,
                    'title': entity.title,
                    'entity': entity
                }
            except FloodWaitError as e:
                await self._wait_for_flood(e.seconds, f"channel {username}")
                if self.should_stop or attempt >= self.config.MAX_RATE_LIMIT_RETRIES:
                    return None
            except (ChannelPrivateError, UsernameNotOccupiedError) as e:
                print(f"Cannot access channel {username}: {e}")
                return None
            except ValueError as e:
                print(f"Channel {username} not found or invalid: {e}")
                return None
            except Exception as e:
                print(f"Error accessing channel {username}: {e}")
                return None
    
    def _show_message_progress(self, channel, message_count, limit, depth, channel_position, channel_total):
        """Show one compact, approximate progress line in the terminal."""
        channel_name = str(channel['username'])[:24]
        if limit:
            completed = min(message_count / limit, 1)
            bar_width = 20
            filled = int(completed * bar_width)
            bar = '#' * filled + '-' * (bar_width - filled)
            progress = f"[{bar}] {message_count}/{limit}"
        else:
            progress = f"{message_count} messages"

        line = (
            f"Depth {depth} | Channel {channel_position}/{channel_total} | "
            f"@{channel_name} | {progress}"
        )
        sys.stdout.write(f"\r{line:<110}")
        sys.stdout.flush()

    async def collect_messages(self, channel, limit=None, year=None, min_forwards=0,
                               depth=1, channel_position=1, channel_total=1):
        """Collect messages from a channel with rate limit handling"""
        print(f"\nCollecting messages from {channel['username']}...")
        
        forwarded_messages = []
        original_messages = []
        forwarded_channels = set()
        
        # Process counter for periodic cleanup
        message_count = 0
        
        try:
            async for message in self.client.iter_messages(
                channel['entity'],
                limit=limit
            ):
                # Check for interruption
                if self.should_stop:
                    print(f"Stopping collection from {channel['username']} due to interrupt...")
                    break

                await self._sleep_with_stop(self.config.MESSAGE_DELAY)
                
                # Filter by year if specified
                if year and message.date.year != year:
                    continue
                
                message_count += 1
                self._show_message_progress(
                    channel,
                    message_count,
                    limit,
                    depth,
                    channel_position,
                    channel_total,
                )
                
                # Periodic memory cleanup every 100 messages
                if message_count % 100 == 0:
                    gc.collect()
                
                # Check if message is forwarded
                if message.fwd_from:
                    forwards_count = getattr(message, 'forwards', 0) or 0
                    
                    # Apply minimum forwards filter
                    if forwards_count < min_forwards:
                        continue
                    
                    # Try to get the original channel
                    try:
                        if message.fwd_from.from_id:
                            try:
                                await self._wait_before_api_request()
                                fwd_channel = await self.client.get_entity(message.fwd_from.from_id)
                            except FloodWaitError as e:
                                await self._wait_for_flood(e.seconds, "forward source")
                                if self.should_stop:
                                    continue
                                await self._wait_before_api_request()
                                fwd_channel = await self.client.get_entity(message.fwd_from.from_id)
                            
                            fwd_channel_info = {
                                'id': fwd_channel.id,
                                'username': getattr(fwd_channel, 'username', str(fwd_channel.id)),
                                'title': getattr(fwd_channel, 'title', 'Unknown')
                            }
                            
                            # Add to forwarded channels set
                            forwarded_channels.add(fwd_channel_info['username'])
                            
                            # Analyze sentiment (this is CPU intensive)
                            sentiment = self.analyzer.analyze_sentiment(message.text or '')
                            
                            # Create message info
                            message_info = {
                                'id': message.id,
                                'url': f"https://t.me/{channel['username']}/{message.id}",
                                'date': message.date,
                                'text': message.text or '',
                                'forwards': forwards_count
                            }
                            
                            # Record the share relationship
                            self.processor.add_share(fwd_channel_info, channel, message_info)
                            
                            # Record the message with sentiment
                            self.processor.add_message(channel, message, sentiment, is_forward=True)
                            
                            forwarded_messages.append(message)
                            self.messages_since_save += 1
                            
                            # Auto-save progress
                            if self.auto_save_interval and self.messages_since_save >= self.auto_save_interval:
                                await self.auto_save_progress()
                    
                    except FloodWaitError as e:
                        await self._wait_for_flood(e.seconds, "message processing")
                        continue
                    except ChannelPrivateError:
                        # Silently skip private channels - this is expected
                        continue
                    except Exception as e:
                        # Only log unexpected errors
                        error_msg = str(e)
                        if "private" not in error_msg.lower() and "permission" not in error_msg.lower():
                            print(f"Error processing forwarded message: {e}")
                        continue
                
                # Track original posts (not forwards)
                elif not self.config.TRACK_FORWARDS_ONLY and message.text:
                    sentiment = self.analyzer.analyze_sentiment(message.text)
                    self.processor.add_original_post(channel, message, sentiment)
                    self.processor.add_message(channel, message, sentiment, is_forward=False)
                    original_messages.append(message)
                    self.messages_since_save += 1
                    
                    # Auto-save progress
                    if self.auto_save_interval and self.messages_since_save >= self.auto_save_interval:
                        await self.auto_save_progress()
        
        except FloodWaitError as e:
            await self._wait_for_flood(e.seconds, "message collection")
            print("Collection paused after the rate limit; continuing with the next channel.")
        except Exception as e:
            print(f"Error collecting messages from {channel['username']}: {e}")
        
        # Final cleanup for this channel
        gc.collect()
        sys.stdout.write("\r" + " " * 110 + "\r")
        sys.stdout.flush()
        print(f"Collected {len(forwarded_messages)} forwarded messages from {channel['username']}")
        print(f"Collected {len(original_messages)} original posts from {channel['username']}")
        print(f"Found {len(forwarded_channels)} unique forwarded channels")
        
        return list(forwarded_channels)
    
    async def snowball_sample(self, initial_channels, depth=2, message_limit=1000, 
                              year=None, min_forwards=0):
        """Perform snowball sampling with rate limiting"""
        print(f"\n{'='*60}")
        print(f"Starting snowball sampling with {len(initial_channels)} initial channels")
        print(f"Depth: {depth}, Message limit: {message_limit}")
        if year:
            print(f"Filtering for year: {year}")
        print(f"Minimum forwards threshold: {min_forwards}")
        backup_status = (
            f"Every {self.auto_save_interval} messages"
            if self.auto_save_interval else "Disabled"
        )
        print(f"Incremental progress backup: {backup_status}")
        print(f"\nTip: Press Ctrl+C at any time to save progress and exit gracefully")
        print(f"{'='*60}\n")
        
        current_level = initial_channels
        
        for level in range(depth):
            if self.should_stop:
                print("\n⚠ Stopping snowball sampling due to interrupt...")
                break
                
            print(f"\n--- LEVEL {level + 1} ---")
            next_level = set()
            
            channel_total = len(current_level)
            for channel_position, username in enumerate(current_level, start=1):
                if self.should_stop:
                    print("\n⚠ Stopping channel processing due to interrupt...")
                    break
                    
                if username in self.visited_channels:
                    print(f"Already visited {username}, skipping")
                    continue
                
                self.visited_channels.add(username)
                
                channel = await self.get_channel_info(username)
                if not channel:
                    print(f"Skipping {username} - could not access")
                    continue
                
                # Collect messages and find forwarded channels
                try:
                    forwarded = await self.collect_messages(
                        channel,
                        limit=message_limit,
                        year=year,
                        min_forwards=min_forwards,
                        depth=level + 1,
                        channel_position=channel_position,
                        channel_total=channel_total,
                    )
                    
                    next_level.update(forwarded)
                except Exception as e:
                    print(f"Error collecting messages from {username}: {e}")
                    continue
                
                # Leave a generous gap between channel histories.
                if not self.should_stop:
                    print(f"Waiting {self.config.CHANNEL_DELAY} seconds before next channel...")
                    await self._sleep_with_stop(self.config.CHANNEL_DELAY)
            
            # Cleanup after each level
            gc.collect()
            
            current_level = list(next_level)
            print(f"Found {len(current_level)} new channels for next level")
            
            if not current_level or self.should_stop:
                if not current_level:
                    print("No new channels found, stopping")
                break
    
    async def run_collection(self, message_limit='1000', year=None, min_forwards=0, depth=2,
                           skip_wordclouds=False, incremental_backups=True, mask_mode='none'):
        """Main collection workflow with optional incremental backups."""
        if not incremental_backups:
            self.auto_save_interval = None
        try:
            # Create output directory
            os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
            
            # Load initial channels
            initial_channels = self.load_recon_list()
            if not initial_channels:
                print("No channels to process")
                return
            
            # Start client
            await self.start()
            
            # Convert message limit
            limit = self.config.MESSAGE_LIMITS.get(message_limit, int(message_limit))
            
            # Perform snowball sampling
            await self.snowball_sample(
                initial_channels,
                depth=depth,
                message_limit=limit,
                year=year,
                min_forwards=min_forwards
            )
            
        except KeyboardInterrupt:
            print("\n\n⚠ Keyboard interrupt detected!")
            self.should_stop = True
        except Exception as e:
            print(f"\n\n❌ Unexpected error: {e}")
            self.should_stop = True
        finally:
            # Always save data at the end
            print("\n" + "="*60)
            print("SAVING FINAL DATA")
            print("="*60)
            
            # Save data to CSV
            shares_df, messages_df, original_df = self.processor.save_to_csv()
            
            # Save per-channel data for analysis app
            if not messages_df.empty:
                self.processor.save_per_channel_data(messages_df, self.config.OUTPUT_DIR)
            
            # Skip word cloud generation if requested (saves CPU)
            if skip_wordclouds:
                print("\nSkipping word cloud generation (can be done later)")
            else:
                # Generate word clouds by language with alternating color schemes
                print("\nGenerating overall word clouds by language...")
                color_schemes = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
                
                for idx, language in enumerate(self.config.LANGUAGE_FILES):
                    if not messages_df.empty:
                        lang_messages = messages_df[messages_df['Language'] == language]
                        if not lang_messages.empty and len(lang_messages) > 0:
                            texts = lang_messages['Message_Text'].dropna().tolist()
                            if texts:
                                # Use different colormap for each language
                                colormap = color_schemes[idx % len(color_schemes)]
                                
                                output_path = os.path.join(
                                    self.config.OUTPUT_DIR,
                                    f'wordcloud_{language}.png'
                                )
                                try:
                                    title = f'{language.title()} - All Channels'
                                    self.analyzer.generate_wordcloud(texts, output_path, language, colormap, title, mask_mode)
                                except Exception as e:
                                    print(f"Error generating {language} word cloud: {e}")
                            else:
                                print(f"No text found for {language} word cloud")
                        else:
                            print(f"No {language} messages found for word cloud")
                
                # Generate ONE word cloud per channel in their primary language
                print("\nGenerating per-channel word clouds (one per channel, primary language)...")
                
                # FIX: Check if messages_df has data and the required column
                if messages_df.empty or 'Channel_Username' not in messages_df.columns:
                    print("No messages data available for per-channel word clouds")
                else:
                    channel_counts = messages_df['Channel_Username'].value_counts()
                    
                    for idx, channel_username in enumerate(channel_counts.index):
                        if pd.isna(channel_username):
                            continue
                        
                        channel_data = messages_df[messages_df['Channel_Username'] == channel_username]
                        
                        # Skip if too few messages
                        if len(channel_data) < 5:
                            continue
                        
                        # Determine primary language for this channel
                        language_counts = channel_data['Language'].value_counts()
                        if language_counts.empty:
                            continue
                        
                        primary_language = language_counts.index[0]  # Most common language
                        
                        # Filter to only messages in primary language
                        lang_channel_data = channel_data[channel_data['Language'] == primary_language]
                        texts = lang_channel_data['Message_Text'].dropna().tolist()
                        
                        if not texts or len(texts) < 3:
                            print(f"Skipping {channel_username} - insufficient {primary_language} text")
                            continue
                        
                        # Use different colormap for variety
                        colormap = color_schemes[idx % len(color_schemes)]
                        
                        safe_username = re.sub(r'[^\w\-_]', '_', str(channel_username))
                        output_path = os.path.join(
                            self.config.OUTPUT_DIR,
                            'per_channel',
                            f'wordcloud_{safe_username}_{primary_language}.png'
                        )
                        
                        # Create title with channel name and language
                        channel_name = channel_data['Channel_Name'].iloc[0] if not channel_data.empty else channel_username
                        title = f'{channel_username}\n({primary_language.title()}, {len(texts)} messages)'
                        
                        try:
                            self.analyzer.generate_wordcloud(texts, output_path, primary_language, colormap, title, mask_mode)
                            print(f"  ✓ Generated for @{channel_username} ({primary_language}, {len(texts)} msgs)")
                        except Exception as e:
                            print(f"  ✗ Error for {channel_username}: {e}")
            
            # Final cleanup
            gc.collect()
            
            print(f"\n{'='*60}")
            print("Collection complete!")
            print(f"Total channels visited: {len(self.visited_channels)}")
            print(f"Total shares collected: {len(self.processor.shares_data)}")
            print(f"Total messages analyzed: {len(self.processor.messages_data)}")
            print(f"Total original posts: {len(self.processor.original_posts_data)}")
            if self.should_stop:
                print("\n⚠ Note: Collection was interrupted. Data has been saved.")
            print(f"{'='*60}\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main entry point with interactive prompts"""
    parser = argparse.ArgumentParser(description="Run Telegram snowball collection")
    parser.add_argument(
        "--no-progress-backup",
        action="store_true",
        help="Disable incremental backups; final CSV files are still saved",
    )
    args = parser.parse_args()

    print("\n" + "="*60)
    print("TELEGRAM SNOWBALL COLLECTOR & ANALYZER")
    print("="*60 + "\n")
    
    # Interactive configuration
    print("Configuration options:")
    print("\n1. Message limit per channel:")
    print("   - 100, 500, 1000, all, or custom number")
    message_limit = input("Enter message limit (default: 1000): ").strip() or "1000"
    
    print("\n2. Filter by year (optional):")
    year_input = input("Enter year (YYYY) or press Enter to skip: ").strip()
    year = int(year_input) if year_input else None
    
    print("\n3. Minimum forwards threshold:")
    min_forwards = int(input("Enter minimum forwards to include (default: 0): ").strip() or "0")
    
    print("\n4. Snowball depth:")
    depth = int(input("Enter depth (1-5, default: 2): ").strip() or "2")
    
    print("\n5. Generate word clouds? (takes extra CPU)")
    skip_wc = input("Skip word clouds? (y/N): ").strip().lower() == 'y'

    print("\n6. Word-cloud shape:")
    print("   1 = normal, 2 = perfect circle, 3 = Telegram mask")
    mask_choice = input("Choose shape (default: 1): ").strip() or "1"
    mask_mode = {'1': 'none', '2': 'circle', '3': 'telegram'}.get(mask_choice, 'none')

    incremental_backups = not args.no_progress_backup
    if not args.no_progress_backup:
        print("\n7. Save progress incrementally?")
        incremental_backups = input("Enable incremental backups? (Y/n): ").strip().lower() != 'n'
    
    # Run collector
    collector = TelegramCollector()
    await collector.run_collection(
        message_limit=message_limit,
        year=year,
        min_forwards=min_forwards,
        depth=depth,
        skip_wordclouds=skip_wc,
        incremental_backups=incremental_backups,
        mask_mode=mask_mode
    )

if __name__ == '__main__':
    asyncio.run(main())