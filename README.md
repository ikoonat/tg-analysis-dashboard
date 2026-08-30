### `TG-ANALYSIS-DASHBOARD`
telegram snowball sampling process that allows you to pull text, links, and shares/interactions between channels- do a little python based sentiment analysis with that stuff as a treat &amp; then throw it onto an easy to configure dashboard to show your friends!

---
# 🐈‍⬛ Get in loser, we're going Spelunking through Telegram
**✨ What is this?** This repository contains **two connected projects** that work together:
| 🐍 **`TELEGRAM-COLLECTOR`** | Collects public Telegram channel data, processes messages, analyzes language and emotion, and exports datasets. |
| 🕸️ **`TELEGRAM-NETWORK-ANALYSIS`** | Turns your dataset into a modular browser-based network map in a dashboard. you can put pretty much anywhere!|

---
## 📋 Table of Contents

- [Introduction](#Introduction)
- [Telegram Collector Requirements](#Requirements)
    - [Running the Collector](#Telegram-Collector-Basics)
- [Telegram Network Analysis Requirements](#Telegram-Network-Analysis-Requirements) 
    - [Running The Dashboard](#Telegram-Analysis-Basics)
- [Project Structure](#project-structure)
- [Features Guide](#features-guide)
- [FAQ & Troubleshooting](#FAQ-and-Troubleshooting)
- [Credits & Thanks](#toolsused)


---
## Introduction
### 🐍 Part I — Telegram Collector
The collector is the data gathering and analysis engine.
It can:
- connect to Telegram using your API credentials
- snowball sample telegram channels
- save raw text and other data to CSV & JSON 
- sort by language and emotional sentiment with python
- analyze sentiment and dominant emotion
- generate word clouds by language and channel
- save per-channel summaries and output files, including outbound links

### 🐛 Part II — Telegram Network Analysis
This is the Visualization Component 
It can:
- take the data you sampled & put it into an interactive dashboard
- build a basica network relation graph of channel relationships
- displays recent message history and recent interactions
- displays other per-channel summaries, including sentiment data
- includes a username search feature, fully interactive
---

## Requirements

### For the Telegram Collector
```txt You need:
- Python 3.11+
- Windows PowerShell
- Telegram API credentials from my.telegram.org
- access to the Telegram channels you want to look at
``` 

### How to get the requirements
```powershell
cd .\TELEGRAM-COLLECTOR
.\setup-venv.ps1
```
That script creates the local `.venv` and installs the Python requirements automatically.

# Step 1: Add the Telegram information
The `.env` file must be in `./TELEGRAM-COLLECTOR`, next to `collector.py`.

```.env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890
```
Get Telegram API information from <https://my.telegram.org>. Keep this information private.

Step 2: Grab a Channel you want to Check out 
Open `reconlist.txt` and put at least 1 Telegram channel username on each line. The `@` symbol is optional.

```reconlist.txt
channel_one
@channel_two
```

## Step 3: Start it up!
Run:
```powershell
.\run-collector.ps1
```
## Telegram-Collector-Basics
The program will ask questions. Press **Enter** to accept the default shown in parentheses.
1. **Message limit:** how many messages to read from each channel. Start with `100` for a small test, or press Enter for `all`.
2. **Year:** enter a year such as `2024`, or press Enter to include all years.
3. **Minimum forwards:** enter `0` to include everything, or filter for stronger sharing relationships by upping it to 3-5 or more!
4. **Snowball depth:** press Enter to use `2`. This controls how far the program follows related channels. A depth of 5 will likely take days
5. **Skip word clouds:** type `y` and press Enter to skip word clouds. Press Enter to generate them.
6. **Word-cloud shape:** choose normal, a perfect circle, or the Telegram mask.
7. **Incremental backups:** press Enter to save progress every 500 messages. Type `n` for a small quick run where only final files are saved.
   ** PLEASE NOTE THE INCREMENTAL BACKUP CURRENTLY GENERATES MASSIVE TEMP FILES **

While a channel is being read, the PowerShell window shows the current snowball depth, channel position, and approximate message progress. For example:
```text
Depth 1 | Channel 2/4 | @example_channel | [##########----------] 500/1000
```
When the message limit is set to `all`, the display shows the number of messages seen without a percentage.

On the first run, Telegram may ask for a login code sent to your phone. Enter the code in PowerShell. Telegram may also ask for your two-step verification password.
Keep PowerShell open until the program says **Collection complete!** You can stop it with `Ctrl+C`; the program will try to save the data before exiting.

### Telegram rate limits
The collector is deliberately slow to reduce pressure on Telegram:
- It waits between direct API requests and message processing.
- It waits several seconds between channel histories.
- If Telegram sends a `FloodWait`, the collector waits for Telegram's requested time plus a small safety buffer.
- It makes only a limited number of rate-limit retries and then moves on rather than retrying forever.
Do not run multiple collector copies with the same Telegram account at the same time. A large collection can take a long time; that is expected and helps avoid rate limits.
For a quick run without incremental backup files, start the collector with:

## Where the results go
The program saves files in the `./TELEGRAM-COLLECTOR/output` folder:
- `telegram_shares.csv`: relationships between channels
- `messages_data.csv`: analyzed messages
- `original_posts.csv`: original posts
- `links_collected.csv`: one row per normalized URL, including `Share_Count`, `Unique_Channel_Count`, and `Unique_Message_Count`
- `./per_channel/`: channel-specific files and word clouds
- `backups/`: automatic progress backups

The Telegram login session is saved locally as `session_name.session`, so later runs normally do not require another login. Keep this file private too.
Repeated URL forms such as `www.example.com`, `http://example.com`, and `https://example.com` are combined when they refer to the same host and path. The URL tally counts every occurrence found in collected message text.

## Running it again
After the first setup, make sure `.env` and `reconlist.txt` are still in this folder, then run:

```powershell
.\run-collector.ps1
```


---
## Telegram-Network-Analysis-Requirements
The dashboard is a Node application. Its JavaScript packages are installed locally in this folder with npm. The optional `.venv`
folder is kept separate for any Python tools and is not used for the dashboard's JavaScript packages.

Install these programs on Windows before starting:
- Node.js 20.19 or newer, up to 24.11.1: <https://nodejs.org/>
- Windows PowerShell

1. Open PowerShell in this folder and run the install script.
```powershell
cd .\TELEGRAM-NETWORK-ANALYSIS
.\setup-node.ps1
```
This checks Node.js and npm, creates the local Python `.venv`, and installs the dashboard packages into the local `node_modules` folder.
If Windows blocks the script, run this once in the same PowerShell window, then repeat the setup command:

2. Copy the main data file
Copy the entire snowball sample you ran earlier (located here: `./TELEGRAM-COLLECTOR/output` ) and place the contents, including subfolders, csv files and json files.
place those files here `./TELEGRAM-NETWORK-ANALYSIS/public/data` 

The dashboard expects the files precisely in this location:
```text
./TELEGRAM-NETWORK-ANALYSIS/public/data/telegram_shares.csv
```

Ensure you also grab the subfolders `per_channel` 
```text
./TELEGRAM-NETWORK-ANALYSIS/public/data/per_channel/{channel name}
```



---


# 🗂️ Choosing Channels
Open:
```text
TELEGRAM-COLLECTOR/reconlist.txt
```

Add one Telegram channel per line.
For example:

```text
channelname1
@channelname2
someotherchannel
```

Nice and simple. No fancy formatting required.

---

# 🚀 Running the Collector
## Step 1 — Set everything up

```powershell
cd .\TELEGRAM-COLLECTOR
.\setup-venv.ps1
```

## Step 2 — Start collecting
```powershell
cd .\TELEGRAM-COLLECTOR
.\run-collector.ps1
```

The collector will guide you through several options, including:
- 📨 Message limit
- 📅 Year / date filter
- 🔁 Minimum forwards threshold
- ❄️ Snowball depth
- ☁️ Whether to generate word clouds
- 💾 Whether to incrementally back up data during collection

### ⚠️ A note about incremental backups

> **The incremental backup feature currently generates gigantic temporary files.**

You have been warned. 😭

For your first run, it is recommended to:

1. Start with a small message count.
2. Use the defaults if you're unsure.
3. Let a test run complete successfully.
4. Increase the message limit once everything is working.

---

# 📱 Telegram Login

On the first run, Telegram may ask for:

- A login code sent to your phone
- Your two-step verification password

Enter these when prompted in PowerShell.

The local Telegram session is stored in the collector directory and can be reused to avoid repeated logins.

---

# 📦 Collector Output

When the collector finishes, you'll find results inside:

```text
TELEGRAM-COLLECTOR/output/
```

Typical outputs include:

```text
output/
├── messages_data.csv
├── original_posts.csv
├── telegram_shares.csv
├── per_channel/
├── word clouds
└── channel summaries
```

There is also a progress bar. It currently **partially estimates remaining users**, while accurately counting posts. It isn't perfect, but it should give you a useful indication that the collector is still working.

The collector is intentionally **conservative and slow** to reduce the likelihood of Telegram rate-limit problems.

---

# 🗃️ IMPORTANT: Save Your Outputs
When you've completed a run, **move the contents of `output/` somewhere safe and label the run** before starting another large collection.

For example:
```text
usernamecoolguy-network-5iterations/
```
This lets you keep separate snapshots of your research rather than accidentally overwriting your previous dataset.

---




# 🕸️ Running the Network Dashboard
```powershell
cd .\TELEGRAM-NETWORK-ANALYSIS
```

## 2. Install dependencies & Set up Node
```powershell
.\setup-node.ps1
```

---
## 3. Copy the graph data

The dashboard expects data in:

```text
TELEGRAM-NETWORK-ANALYSIS/public/data/
```

Copy the main relationship file:

```powershell
Copy-Item ..\TELEGRAM-COLLECTOR\output\telegram_shares.csv .\public\data\telegram_shares.csv -Force
```

You can also copy the per-channel data:

```powershell
Copy-Item ..\TELEGRAM-COLLECTOR\output\per_channel\* .\public\data\per_channel\ -Recurse -Force
```

The dashboard reads these files from `public/data/` at runtime.

---

# 💻 Start the Dashboard

Run:

```powershell
npm run dev
```

This should start the local development server, usually at:

```text
http://localhost:5173/
```

Open that address in your browser, and you should see it populate!


---
# 🔎 Exploring the Dashboard
Once it's running, you can:
- 🕸️ View channel relationships as a graph
- 🖱️ Click nodes to inspect individual channels
- 📨 Inspect message and forwarding patterns
- 📊 Browse channel summaries
- ☁️ Explore word clouds
- 🔍 Search usernames
- 🔎 Zoom and pan around the network

---


---

# ⚡ Quick Start
## 🐍 Collector
```powershell
cd .\TELEGRAM-COLLECTOR
.\setup-venv.ps1
.\run-collector.ps1
```

## 🕸️ Network Analysis

```powershell
cd .\TELEGRAM-NETWORK-ANALYSIS
npm install
npm run dev
```

Then open:

```text
http://localhost:5173/
```

---

## ⚠️ FAQ-and-Troubleshooting
Please keep these things in mind:
-  **Never commit `.env` or Telegram API credentials.**
-  Keep `.venv` local.
-  Keep Telegram session files private.
-  Back up your datasets before starting another collection run.
-  The collector is intentionally conservative and can take a while.
-  **Collector = data source**
-  **Dashboard = visualization layer**

---

## ⚠️ Troubleshooting
### The page says that no data is available

Check that this file exists and is named exactly:

```text
public\data\telegram_shares.csv
```

Also check that it contains the collector columns beginning with `From_Channel_ID`, `From_Channel_Username`, `To_Channel_ID`, and `To_Channel_Username`.

### `npm` or `node` is not recognized

Install Node.js, close PowerShell, open a new PowerShell window, and check:

```powershell
node --version
npm --version
```

Then run `.\setup-node.ps1` again.
### The dashboard dependencies are broken

From this folder, run:
```powershell
npm install
npm run dev
```

### PowerShell will not run a script
Run this temporary permission command, then retry the script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Useful commands
```powershell
npm run dev       # Start the dashboard for local use
npm run build     # Check that a production build succeeds
npm run preview   # Preview the production build
npm run storybook # Open the component workshop


```

# Summary

I am **not a computer software person, a coder, or anything remotely similar**. This project exists 
largely because I kept poking at Telegram until it became a project. I've also had a *lot* of help
from friends, especially with handling **right-to-left text in Arabic and Hebrew**. Without them,
and without the incredibly generous and talented people behind the open-source tools below, I
absolutely would not have been able to put this together. I've tried to indicate the specific tools 
used directly in the project, while also including projects that were particularly helpful during
my various Telegram spelunking adventures.

**thanks to all these cool people. **
# 🧰 Tools & Projects That Made This Possible
## 🧠 Language Processing
- ⭐ [`pyplutchik`](https://github.com/alfonsosemeraro/pyplutchik) — emotion / Plutchik processing
- ⭐ [`word_cloud`](https://github.com/amueller/word_cloud) — word cloud generation
- ⭐ [`python-arabic-reshaper`](https://github.com/mpcabd/python-arabic-reshaper) — Arabic text shaping
- ⭐ [`python-bidi`](https://github.com/MeirKriheli/python-bidi) — bidirectional text handling

## 🛑 Stop Words
- ⭐ [`datasets-stopwords-en`](https://github.com/stdlib-js/datasets-stopwords-en) — English
- ⭐ [`arabic-stop-words`](https://github.com/mohataher/arabic-stop-words) — Arabic
- ⭐ [`Stop-Words-Hebrew`](https://github.com/NNLP-IL/Stop-Words-Hebrew/) — Hebrew
- ⭐ [`stopwords-iso`](https://github.com/stopwords-iso/stopwords-iso) — because apparently I decided I needed practically every language imaginable

## 💭 Lexicons
- ⭐ [NRC Word-Emotion Association Lexicon](https://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm)

## 📡 Telegram Tools
- ⭐ [`Telegram-Snowball-Sampling`](https://github.com/thomasjjj/Telegram-Snowball-Sampling)
- ⭐ [`TelegramPowerToys`](https://github.com/Kenobi-Knobs/TelegramPowerToys)
- [`telegram-chat-analytics`](https://github.com/Hochinwei/telegram-chat-analytics)

## 🌐 Open Source Web / Data Tools
- [D3.js](https://d3js.org/)
- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [Storybook](https://storybook.js.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Google Fonts](https://fonts.google.com/)
- [Telethon](https://docs.telethon.dev/en/stable/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [PapaParse](https://www.papaparse.com/)

<p align="center">

### 🐈‍⬛ Made with questionable amounts of curiosity, Python, JavaScript, and caffeine.

**Happy spelunking. 🔎**

## File Structure (In case you need it)
# 📁 Repository Structure

```text
TG-ANALYSIS-DASHBOARD/
│
├── TELEGRAM-COLLECTOR/
│   ├── collector.py
│   ├── config.py
│   ├── sentiment_analyzer.py
│   ├── reprocess_sentiment.py
│   ├── requirements.txt
│   ├── .env_demo
│   ├── reconlist.txt
│   ├── lexicons/
│   ├── stopwords/
│   ├── fonts/
│   ├── output/
│   └── ...
│
├── TELEGRAM-NETWORK-ANALYSIS/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── setup-node.ps1
│   └── ...
│
├── 📖 README.md
└── ...
```

</p>
