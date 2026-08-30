# Telegram Network Dashboard

This folder contains the browser dashboard for viewing Telegram channel relationships. It displays the CSV data created by the companion `TELEGRAM-COLLECTOR` process.

## What you need

Install these programs on Windows before starting:

- Node.js 20.19 or newer, up to 24.11.1: <https://nodejs.org/>
- Windows PowerShell

The dashboard is a Node application. Its JavaScript packages are installed locally in this folder with npm. The optional `.venv` folder is kept separate for any Python tools and is not used for the dashboard's JavaScript packages.

## Quick start

### 1. Open PowerShell in this folder

Open the `TELEGRAM-NETWORK-ANALYSIS` folder in File Explorer. Right-click an empty area, choose **Open in Terminal**, and make sure the terminal is in this folder.

### 2. Prepare the local environments

Run the Node setup script:

```powershell
.\setup-node.ps1
```

This checks Node.js and npm, creates the local Python `.venv`, and installs the dashboard packages into the local `node_modules` folder.

If Windows blocks the script, run this once in the same PowerShell window, then repeat the setup command:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

The Python environment can also be created by itself with:

```powershell
.\setup-venv.ps1
```

You do not need to activate `.venv` to run the dashboard.

### 3. Collect the data

If you do not already have data, follow the instructions in `TELEGRAM-COLLECTOR\readme.md` first. The collector creates this file:

```text
TELEGRAM-COLLECTOR\output\telegram_shares.csv
```

### 4. Copy the main data file

Copy `telegram_shares.csv` from the collector's `output` folder into this folder's data folder:

```powershell
Copy-Item '..\TELEGRAM-COLLECTOR\output\telegram_shares.csv' '.\public\data\telegram_shares.csv' -Force
```

The dashboard expects the file at exactly:

```text
public\data\telegram_shares.csv
```

You can also copy the collector's optional `per_channel` folder into:

```text
public\data\per_channel\
```

That folder may contain channel CSV files, summary JSON files, and word-cloud images.

### 5. Start the dashboard

Run:

```powershell
npm run dev
```

PowerShell will show a local address, normally:

```text
http://localhost:5173/
```

Open that address in a web browser. Keep the PowerShell window open while using the dashboard. Press `Ctrl+C` in that window to stop it.

## Updating the dashboard data

Run the collector again, then copy the new file over the old one:

```powershell
Copy-Item '..\TELEGRAM-COLLECTOR\output\telegram_shares.csv' '.\public\data\telegram_shares.csv' -Force
```

Refresh the browser page to see the updated data.

## What the dashboard shows

- Channel relationships and message flows
- Incoming and outgoing connection counts
- Channel details when a node is selected
- Related channel information
- Per-channel messages and word clouds when those files are available

Use the mouse wheel to zoom, drag the background to move around, and click a channel to inspect it.

## Troubleshooting

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





Prepare the data
The dashboard expects data files in the `public/data` folder.

First, run the collector and generate output files in the collector project.

Then copy the main graph data into the analysis app:

```powershell
Copy-Item ..\TELEGRAM-COLLECTOR\output\telegram_shares.csv .\public\data\telegram_shares.csv -Force
```

Optionally, also copy the per-channel files:

```powershell
Copy-Item ..\TELEGRAM-COLLECTOR\output\per_channel\* .\public\data\per_channel\ -Recurse -Force
```

The dashboard reads files from `public/data` at runtime.
