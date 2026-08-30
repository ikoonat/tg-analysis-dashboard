import pandas as pd
from datetime import datetime
import csv
import os
import re
from urllib.parse import urlsplit, urlunsplit

class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.interaction_counter = 1
        self.shares_data = []
        self.messages_data = []
        self.original_posts_data = []
        self.links_data = {}
    
    def add_share(self, from_channel, to_channel, message_info):
        """Add a share/forward relationship"""
        self.shares_data.append({
            'Interaction_ID': self.interaction_counter,
            'From_Channel_ID': from_channel['id'],
            'From_Channel_Username': from_channel['username'],
            'From_Channel_Name': from_channel['title'],
            'To_Channel_ID': to_channel['id'],
            'To_Channel_Username': to_channel['username'],
            'To_Channel_Name': to_channel['title'],
            'Message_ID': message_info['id'],
            'Message_URL': message_info['url'],
            'Message_Date': message_info['date'],
            'Message_Text_Preview': message_info['text'][:100] if message_info['text'] else '',
            'Forwards_Count': message_info.get('forwards', 0)  # Added forwards count
        })
        
        self.interaction_counter += 1
    
    def _extract_urls(self, text):
        """Extract URLs while preserving repeats for later tallying."""
        if not text:
            return []
        
        # Regex pattern to match URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        # Also catch URLs without http/https
        www_pattern = r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        www_urls = re.findall(www_pattern, text)
        
        return [self._normalize_url(url) for url in urls + www_urls]

    def _normalize_url(self, url):
        """Normalize URL spelling so equivalent repeats share one tally."""
        url = url.strip().rstrip('.,;:!?)]}')
        if url.lower().startswith('www.'):
            url = f'https://{url}'

        try:
            parts = urlsplit(url)
            scheme = parts.scheme.lower()
            hostname = (parts.hostname or '').lower()
            hostname = re.sub(r'^www\.', '', hostname)
            if not scheme or not hostname:
                return url

            netloc = hostname
            if parts.port:
                netloc = f'{netloc}:{parts.port}'
            return urlunsplit((scheme, netloc, parts.path, parts.query, ''))
        except ValueError:
            return url
    
    def add_link(self, channel, message, url):
        """Add a link/URL found in a message"""
        url = self._normalize_url(url)
        domain = self._extract_domain(url)
        if url not in self.links_data:
            self.links_data[url] = {
                'Channel_ID': channel['id'],
                'Channel_Username': channel['username'],
                'Channel_Name': channel['title'],
                'Message_ID': message.id,
                'Message_URL': f"https://t.me/{channel['username']}/{message.id}",
                'Message_Date': message.date,
                'Link_URL': url,
                'Link_Domain': domain,
                'Views': getattr(message, 'views', 0),
                'Forwards': getattr(message, 'forwards', 0),
                'Share_Count': 0,
                'Source_Channels': set(),
                'Source_Message_IDs': set(),
            }

        link = self.links_data[url]
        link['Share_Count'] += 1
        link['Source_Channels'].add(str(channel['username']))
        link['Source_Message_IDs'].add(str(message.id))
    
    def _extract_domain(self, url):
        """Extract domain from URL"""
        try:
            # Remove protocol
            domain = re.sub(r'^https?://', '', url)
            domain = re.sub(r'^www\.', '', domain)
            # Get just the domain part
            domain = domain.split('/')[0]
            return domain
        except:
            return url
    
    def add_message(self, channel, message, sentiment_data, is_forward=False):
        """Add message data with sentiment analysis"""
        # Extract URLs from message text
        urls = self._extract_urls(message.text) if message.text else []
        
        # Store links separately
        for url in urls:
            self.add_link(channel, message, url)
        
        self.messages_data.append({
            'Interaction_ID': self.interaction_counter - 1,
            'Channel_ID': channel['id'],
            'Channel_Username': channel['username'],
            'Channel_Name': channel['title'],
            'Message_ID': message.id,
            'Message_URL': f"https://t.me/{channel['username']}/{message.id}",
            'Message_Date': message.date,
            'Message_Text': message.text or '',
            'Language': sentiment_data['language'],
            'Emotions': str(sentiment_data['emotions']),
            'Dominant_Emotion': sentiment_data['dominant_emotion'],
            'Has_Media': message.media is not None,
            'Views': getattr(message, 'views', 0),
            'Forwards': getattr(message, 'forwards', 0),
            'Is_Forward': is_forward,
            'Link_Count': len(urls)  # Add link count to messages
        })
    
    def add_original_post(self, channel, message, sentiment_data):
        """Add original post data"""
        # Extract URLs from message text
        urls = self._extract_urls(message.text) if message.text else []
        
        # Store links separately
        for url in urls:
            self.add_link(channel, message, url)
        
        self.original_posts_data.append({
            'Channel_ID': channel['id'],
            'Channel_Username': channel['username'],
            'Channel_Name': channel['title'],
            'Message_ID': message.id,
            'Message_URL': f"https://t.me/{channel['username']}/{message.id}",
            'Message_Date': message.date,
            'Message_Text': message.text or '',
            'Language': sentiment_data['language'],
            'Emotions': str(sentiment_data['emotions']),
            'Dominant_Emotion': sentiment_data['dominant_emotion'],
            'Has_Media': message.media is not None,
            'Views': getattr(message, 'views', 0),
            'Forwards': getattr(message, 'forwards', 0),
            'Link_Count': len(urls)  # Add link count
        })
    
    def save_to_csv(self):
        """Save collected data to CSV files"""
        # Save shares data
        if self.shares_data:
            shares_df = pd.DataFrame(self.shares_data)
            # Sort by forwards count (most viral first)
            if 'Forwards_Count' in shares_df.columns:
                shares_df = shares_df.sort_values('Forwards_Count', ascending=False)
            shares_df.to_csv(self.config.SHARES_CSV, index=False, encoding='utf-8-sig')
            print(f"Shares data saved to {self.config.SHARES_CSV}")
            print(f"Total shares collected: {len(self.shares_data)}")
        else:
            print("No shares data to save")
            shares_df = pd.DataFrame()
        
        # Save messages data
        if self.messages_data:
            messages_df = pd.DataFrame(self.messages_data)
            # Sort by date (most recent first)
            if 'Message_Date' in messages_df.columns:
                messages_df = messages_df.sort_values('Message_Date', ascending=False)
            messages_df.to_csv(self.config.MESSAGES_CSV, index=False, encoding='utf-8-sig')
            print(f"Messages data saved to {self.config.MESSAGES_CSV}")
            print(f"Total messages collected: {len(self.messages_data)}")
            
            # Print summary statistics
            if not messages_df.empty:
                print(f"\nMessage Statistics:")
                print(f"  - Forwarded messages: {len(messages_df[messages_df['Is_Forward'] == True])}")
                print(f"  - Original posts: {len(messages_df[messages_df['Is_Forward'] == False])}")
                if 'Language' in messages_df.columns:
                    print(f"  - Language breakdown:")
                    for lang, count in messages_df['Language'].value_counts().head(5).items():
                        print(f"    • {lang}: {count}")
        else:
            print("No messages data to save")
            messages_df = pd.DataFrame()
        
        # Save original posts data
        if self.original_posts_data:
            original_df = pd.DataFrame(self.original_posts_data)
            # Sort by forwards count (most viral original posts first)
            if 'Forwards' in original_df.columns:
                original_df = original_df.sort_values('Forwards', ascending=False)
            original_df.to_csv(self.config.ORIGINAL_POSTS_CSV, index=False, encoding='utf-8-sig')
            print(f"Original posts data saved to {self.config.ORIGINAL_POSTS_CSV}")
            print(f"Total original posts collected: {len(self.original_posts_data)}")
        else:
            print("No original posts data to save")
            original_df = pd.DataFrame()
        
        # Save links data
        if self.links_data:
            links_df = pd.DataFrame(self._link_rows())
            # Sort by views (most viewed links first)
            if 'Views' in links_df.columns:
                links_df = links_df.sort_values('Views', ascending=False)
            
            links_csv = os.path.join(os.path.dirname(self.config.MESSAGES_CSV), 'links_collected.csv')
            links_df.to_csv(links_csv, index=False, encoding='utf-8-sig')
            print(f"Links data saved to {links_csv}")
            print(f"Unique URLs collected: {len(self.links_data)}")
            print(f"Total URL shares counted: {int(links_df['Share_Count'].sum())}")
            
            # Print link statistics
            if not links_df.empty:
                print(f"\nLink Statistics:")
                print(f"  - Unique domains: {links_df['Link_Domain'].nunique()}")
                print(f"  - Top 5 domains:")
                for domain, count in links_df['Link_Domain'].value_counts().head(5).items():
                    print(f"    • {domain}: {count} unique URLs")
        else:
            print("No links data to save")
            links_df = pd.DataFrame()
        
        return shares_df, messages_df, original_df

    def _link_rows(self):
        """Convert URL aggregates to CSV-safe rows."""
        rows = []
        for link in self.links_data.values():
            row = link.copy()
            row['Source_Channels'] = '; '.join(sorted(row['Source_Channels']))
            row['Source_Message_IDs'] = '; '.join(sorted(row['Source_Message_IDs']))
            row['Unique_Channel_Count'] = len(link['Source_Channels'])
            row['Unique_Message_Count'] = len(link['Source_Message_IDs'])
            rows.append(row)
        return rows
    
    def save_per_channel_data(self, messages_df, output_dir):
        """Save data grouped by channel for analysis app"""
        if messages_df.empty:
            print("No messages to export per channel")
            return
        
        # Validate required columns exist
        required_columns = ['Channel_Username', 'Channel_Name', 'Is_Forward', 'Views', 'Forwards', 'Language', 'Dominant_Emotion', 'Message_Date']
        missing_columns = [col for col in required_columns if col not in messages_df.columns]
        
        if missing_columns:
            print(f"Warning: Missing columns in messages_df: {missing_columns}")
            print("Skipping per-channel data export")
            return
        
        # Create per-channel directory
        per_channel_dir = os.path.join(output_dir, 'per_channel')
        os.makedirs(per_channel_dir, exist_ok=True)
        
        # Also save per-channel link data
        if self.links_data:
            links_df = pd.DataFrame(self._link_rows())
            expanded_rows = []
            for _, row in links_df.iterrows():
                for channel_username in row['Source_Channels'].split('; '):
                    channel_row = row.copy()
                    channel_row['Channel_Username'] = channel_username
                    expanded_rows.append(channel_row)
            links_df = pd.DataFrame(expanded_rows)
            self._save_per_channel_links(links_df, per_channel_dir)
        
        # Group by channel
        channels = messages_df['Channel_Username'].unique()
        
        print(f"\nExporting data for {len(channels)} channels...")
        
        exported_count = 0
        for channel_username in channels:
            if pd.isna(channel_username):
                continue
            
            channel_data = messages_df[messages_df['Channel_Username'] == channel_username]
            
            # Skip channels with too few messages
            if len(channel_data) < 1:
                continue
            
            # Clean filename
            safe_username = re.sub(r'[^\w\-_]', '_', str(channel_username))
            filename = os.path.join(per_channel_dir, f'{safe_username}.csv')
            
            # Save channel-specific CSV
            try:
                channel_data.to_csv(filename, index=False, encoding='utf-8-sig')
                
                # Create channel summary
                summary = {
                    'Channel_Username': channel_username,
                    'Channel_Name': channel_data['Channel_Name'].iloc[0] if not channel_data.empty else 'Unknown',
                    'Total_Messages': len(channel_data),
                    'Forwarded_Messages': int(len(channel_data[channel_data['Is_Forward'] == True])),
                    'Original_Posts': int(len(channel_data[channel_data['Is_Forward'] == False])),
                    'Total_Views': int(channel_data['Views'].sum()),
                    'Total_Forwards': int(channel_data['Forwards'].sum()),
                    'Avg_Views': float(channel_data['Views'].mean()),
                    'Avg_Forwards': float(channel_data['Forwards'].mean()),
                    'Languages': channel_data['Language'].value_counts().to_dict(),
                    'Dominant_Emotions': channel_data['Dominant_Emotion'].value_counts().head(5).to_dict(),
                    'Date_Range': f"{channel_data['Message_Date'].min()} to {channel_data['Message_Date'].max()}"
                }
                
                # Save summary JSON
                import json
                summary_file = os.path.join(per_channel_dir, f'{safe_username}_summary.json')
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
                
                exported_count += 1
                
            except Exception as e:
                print(f"  Error exporting {channel_username}: {e}")
                continue
        
        print(f"Per-channel data saved to {per_channel_dir}/")
        print(f"Successfully exported {exported_count} channel files")
        
        # Create master channel index
        channel_index = []
        for channel_username in channels:
            if pd.isna(channel_username):
                continue
            channel_data = messages_df[messages_df['Channel_Username'] == channel_username]
            
            if len(channel_data) < 1:
                continue
                
            safe_username = re.sub(r'[^\w\-_]', '_', str(channel_username))
            channel_index.append({
                'Channel_Username': channel_username,
                'Channel_Name': channel_data['Channel_Name'].iloc[0] if not channel_data.empty else 'Unknown',
                'Message_Count': len(channel_data),
                'Forward_Count': int(len(channel_data[channel_data['Is_Forward'] == True])),
                'Original_Count': int(len(channel_data[channel_data['Is_Forward'] == False])),
                'Total_Views': int(channel_data['Views'].sum()),
                'Total_Forwards': int(channel_data['Forwards'].sum()),
                'CSV_File': f'{safe_username}.csv'
            })
        
        if channel_index:
            index_df = pd.DataFrame(channel_index)
            # Sort by message count (most active channels first)
            index_df = index_df.sort_values('Message_Count', ascending=False)
            index_file = os.path.join(per_channel_dir, '_channel_index.csv')
            index_df.to_csv(index_file, index=False, encoding='utf-8-sig')
            print(f"Channel index saved to {index_file}")
        else:
            print("No channels to include in index")
    
    def _save_per_channel_links(self, links_df, per_channel_dir):
        """Save links grouped by channel"""
        if links_df.empty:
            return
        
        print(f"\nExporting links for each channel...")
        
        channels = links_df['Channel_Username'].unique()
        
        for channel_username in channels:
            if pd.isna(channel_username):
                continue
            
            channel_links = links_df[links_df['Channel_Username'] == channel_username]
            
            if len(channel_links) == 0:
                continue
            
            # Clean filename
            safe_username = re.sub(r'[^\w\-_]', '_', str(channel_username))
            filename = os.path.join(per_channel_dir, f'{safe_username}_links.csv')
            
            # Save channel-specific links CSV
            try:
                channel_links.to_csv(filename, index=False, encoding='utf-8-sig')
                
                # Print summary for this channel
                unique_domains = channel_links['Link_Domain'].nunique()
                total_links = len(channel_links)
                print(f"  ✓ {channel_username}: {total_links} links, {unique_domains} domains")
                
            except Exception as e:
                print(f"  ✗ Error exporting links for {channel_username}: {e}")
        
        print(f"Per-channel links saved to {per_channel_dir}/")