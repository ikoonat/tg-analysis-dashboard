import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors import ChannelPrivateError, UsernameNotOccupiedError
from datetime import datetime
import os
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
        
    async def start(self):
        """Initialize Telegram client"""
        await self.client.start(phone=self.config.PHONE)
        print("Connected to Telegram")
    
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
        """Get channel information"""
        try:
            # Remove @ if present
            username = username.lstrip('@')
            
            entity = await self.client.get_entity(username)
            full_channel = await self.client(GetFullChannelRequest(entity))
            
            return {
                'id': entity.id,
                'username': username,
                'title': entity.title,
                'entity': entity
            }
        except (ChannelPrivateError, UsernameNotOccupiedError) as e:
            print(f"Cannot access channel {username}: {e}")
            return None
    
    async def collect_messages(self, channel, limit=None, year=None, min_forwards=0):
        """Collect messages from a channel"""
        print(f"\nCollecting messages from {channel['username']}...")
        
        messages = []
        forwarded_channels = set()
        
        try:
            async for message in self.client.iter_messages(
                channel['entity'],
                limit=limit
            ):
                # Filter by year if specified
                if year and message.date.year != year:
                    continue
                
                # Check if message is forwarded
                if message.fwd_from:
                    forwards_count = getattr(message, 'forwards', 0)
                    
                    # Apply minimum forwards filter
                    if forwards_count < min_forwards:
                        continue
                    
                    # Try to get the original channel
                    try:
                        if message.fwd_from.from_id:
                            fwd_channel = await self.client.get_entity(message.fwd_from.from_id)
                            fwd_channel_info = {
                                'id': fwd_channel.id,
                                'username': getattr(fwd_channel, 'username', str(fwd_channel.id)),
                                'title': getattr(fwd_channel, 'title', 'Unknown')
                            }
                            
                            # Add to forwarded channels set
                            forwarded_channels.add(fwd_channel_info['username'])
                            
                            # Analyze sentiment
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
                            self.processor.add_message(channel, message, sentiment)
                            
                            messages.append(message)
                    
                    except Exception as e:
                        print(f"Error processing forwarded message: {e}")
                        continue
        
        except Exception as e:
            print(f"Error collecting messages from {channel['username']}: {e}")
        
        print(f"Collected {len(messages)} forwarded messages from {channel['username']}")
        print(f"Found {len(forwarded_channels)} unique forwarded channels")
        
        return list(forwarded_channels)
    
    async def snowball_sample(self, initial_channels, depth=2, message_limit=1000, 
                              year=None, min_forwards=0):
        """Perform snowball sampling"""
        print(f"\n{'='*60}")
        print(f"Starting snowball sampling with {len(initial_channels)} initial channels")
        print(f"Depth: {depth}, Message limit: {message_limit}")
        if year:
            print(f"Filtering for year: {year}")
        print(f"Minimum forwards threshold: {min_forwards}")
        print(f"{'='*60}\n")
        
        current_level = initial_channels
        
        for level in range(depth):
            print(f"\n--- LEVEL {level + 1} ---")
            next_level = set()
            
            for username in current_level:
                if username in self.visited_channels:
                    print(f"Already visited {username}, skipping")
                    continue
                
                self.visited_channels.add(username)
                
                channel = await self.get_channel_info(username)
                if not channel:
                    continue
                
                # Collect messages and find forwarded channels
                forwarded = await self.collect_messages(
                    channel,
                    limit=message_limit,
                    year=year,
                    min_forwards=min_forwards
                )
                
                next_level.update(forwarded)
                
                # Rate limiting
                await asyncio.sleep(1)
            
            current_level = list(next_level)
            print(f"Found {len(current_level)} new channels for next level")
            
            if not current_level:
                print("No new channels found, stopping")
                break
    
    async def run_collection(self, message_limit='1000', year=None, min_forwards=0, depth=2):
        """Main collection workflow"""
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
        
        # Save data to CSV
        shares_df, messages_df = self.processor.save_to_csv()
        
        # Generate word clouds by language
        for language in self.config.LANGUAGE_FILES:
            lang_messages = messages_df[messages_df['Language'] == language]
            if not lang_messages.empty:
                texts = lang_messages['Message_Text'].tolist()
                output_path = os.path.join(
                    self.config.OUTPUT_DIR,
                    f'wordcloud_{language}.png'
                )
                self.analyzer.generate_wordcloud(texts, output_path, language)
        
        print(f"\n{'='*60}")
        print("Collection complete!")
        print(f"Total channels visited: {len(self.visited_channels)}")
        print(f"Total shares collected: {len(self.processor.shares_data)}")
        print(f"Total messages analyzed: {len(self.processor.messages_data)}")
        print(f"{'='*60}\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main entry point with interactive prompts"""
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
    
    # Run collector
    collector = TelegramCollector()
    await collector.run_collection(
        message_limit=message_limit,
        year=year,
        min_forwards=min_forwards,
        depth=depth
    )

if __name__ == '__main__':
    asyncio.run(main())