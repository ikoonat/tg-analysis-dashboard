# Telegram Collector

This program reads Telegram channels, analyzes their messages, and saves the results as files. These instructions are for the `TELEGRAM-COLLECTOR` folder only.

## Before you start

You need:

- Windows PowerShell
- Python 3.11 or newer
- Telegram API information: an API ID, API hash, and phone number
- The channel names you want to collect

Get Telegram API information from <https://my.telegram.org>. Keep this information private.

## Step 1: Add the Telegram information

The `.env` file must be in this folder, next to `collector.py`.

If you were given an `.env` file, copy it into this folder. It should contain these three lines:

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890
```

Do not rename the file to `.env.txt`. Do not share the completed `.env` file or upload it to GitHub.

If you need a template, copy `.env_demo` and rename the copy to `.env`, then replace the example values with your real information.

## Step 2: List the channels

Open `reconlist.txt` and put one public Telegram channel username on each line. The `@` symbol is optional.

Example:

```text
channel_one
@channel_two
```

Save the file when finished.

## Step 3: Install the program

Open PowerShell in this `TELEGRAM-COLLECTOR` folder and run:

```powershell
.\setup-venv.ps1
```

This creates a private folder named `.venv` and installs the program's packages there. You only need to do this once, or again after `requirements.txt` changes.

## Optional: add fonts for word clouds

The program can create word clouds for all configured languages. To improve font coverage and add visual variety, place licensed `.ttf` or `.otf` files in a language folder inside `fonts`.

Use the language name as the filename when possible:

```text
fonts/
	arabic/
		NotoNaskhArabic-Regular.ttf
	latin/
		Archivo-Regular.ttf
		Archivo-Bold.ttf
```

Each word randomly uses one of the fonts in its language folder. Latin-script languages use `fonts\latin` when they do not have their own folder. If no project font is available, the program uses an installed Windows font. See `fonts\README.md` for more information.

If Windows blocks the script, run this once in the same PowerShell window and then repeat the setup command:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Step 4: Start a collection

Run:

```powershell
.\run-collector.ps1
```

The program will ask questions. Press **Enter** to accept the default shown in parentheses.

1. **Message limit:** how many messages to read from each channel. Start with `100` for a small test, or press Enter for `1000`.
2. **Year:** enter a year such as `2024`, or press Enter to include all years.
3. **Minimum forwards:** enter `0` to include everything, or enter a higher number to keep only widely forwarded messages.
4. **Snowball depth:** press Enter to use `2`. This controls how far the program follows related channels.
5. **Skip word clouds:** type `y` and press Enter to skip word clouds. Press Enter to generate them.
6. **Word-cloud shape:** choose normal, a perfect circle, or the Telegram mask.
7. **Incremental backups:** press Enter to save progress every 500 messages. Type `n` for a small quick run where only final files are saved.

While a channel is being read, the PowerShell window shows the current snowball depth, channel position, and approximate message progress. For example:

```text
Depth 1 | Channel 2/4 | @example_channel | [##########----------] 500/1000
```

When the message limit is set to `all`, the display shows the number of messages seen without a percentage.

On the first run, Telegram may ask for a login code sent to your phone. Enter the code in PowerShell. Telegram may also ask for your two-step verification password.

Keep PowerShell open until the program says **Collection complete!** You can stop it with `Ctrl+C`; the program will try to save the data before exiting.

## Telegram rate limits

The collector is deliberately slow to reduce pressure on Telegram:

- It waits between direct API requests and message processing.
- It waits several seconds between channel histories.
- If Telegram sends a `FloodWait`, the collector waits for Telegram's requested time plus a small safety buffer.
- It makes only a limited number of rate-limit retries and then moves on rather than retrying forever.

Do not run multiple collector copies with the same Telegram account at the same time. A large collection can take a long time; that is expected and helps avoid rate limits.

For a quick run without incremental backup files, start the collector with:

```powershell
.\run-collector.ps1 -NoProgressBackup
```

This skips the backup question. Final CSV files are still saved when the run ends or is interrupted.

## Where the results go

The program saves files in the `output` folder:

- `telegram_shares.csv`: relationships between channels
- `messages_data.csv`: analyzed messages
- `original_posts.csv`: original posts
- `links_collected.csv`: one row per normalized URL, including `Share_Count`, `Unique_Channel_Count`, and `Unique_Message_Count`
- `per_channel/`: channel-specific files and word clouds
- `backups/`: automatic progress backups

The Telegram login session is saved locally as `session_name.session`, so later runs normally do not require another login. Keep this file private too.

Repeated URL forms such as `www.example.com`, `http://example.com`, and `https://example.com` are combined when they refer to the same host and path. The URL tally counts every occurrence found in collected message text.

## Running it again

After the first setup, make sure `.env` and `reconlist.txt` are still in this folder, then run:

```powershell
.\run-collector.ps1
```

There is no need to activate the environment manually. The launcher uses `TELEGRAM-COLLECTOR\.venv` automatically.
