# Discord Media Embed Bot

A lightweight Discord bot that automatically converts user-uploaded media and supported links into clean, consistent embeds.

This project is **content-agnostic**: it does not host, store, or generate media. All embeds are created from **user-provided content** inside Discord servers.

---

## ✨ Features

* Automatically embeds:

  * Images (`png`, `jpg`, `jpeg`, `webp`)
  * GIFs (`gif`)
  * Videos (`mp4`, `webm`, `mov`)
* Supports multiple attachments in a single message
* Uses the **message text as the embed title** (if provided)
* If no text is provided, the embed shows **only the media** (no filename)
* Preserves the original uploader’s name and avatar in embeds
* Optional metadata embedding for supported links
* Server-wide refresh command to retroactively embed older messages

---

## ⚙️ Requirements

* Python **3.10+**
* A Discord bot application

Python dependencies:

```bash
pip install discord.py aiohttp beautifulsoup4
```

---

## 📁 Project Structure

```
project/
├── bot.py            # Main bot script
├── token.txt         # Your bot token (not committed)
├── serverID.txt      # Your server (guild) ID (not committed)
└── README.md
```

---

## 🔐 Setup

### 1. Create a Discord bot

1. Go to [https://discord.com/developers/applications](https://discord.com/developers/applications)
2. Create a new application
3. Add a **Bot** user
4. Enable **Message Content Intent**
5. Copy the bot token

---

### 2. Configure secrets

Create the following files **next to the bot script**:

**`token.txt`**

```
YOUR_BOT_TOKEN_HERE
```

**`serverID.txt`**

```
YOUR_SERVER_ID_HERE
```

> ⚠️ Never commit these files to a public repository.

---

### 3. Configure channel IDs

Inside the script, update the following constant:

```python
ARCHIVE_CHANNEL_ID = YOUR_ARCHIVE_CHANNEL_ID
```

This channel is used to temporarily store thumbnails when needed.

---

## ▶️ Running the bot

```bash
python bot.py
```

On startup, the bot will:

* Connect to Discord
* Sync slash commands to your server
* Begin monitoring messages for media

---

## 🧠 How it works

### Attachments

* If a message contains **text + media**, the text becomes the embed title
* If a message contains **only media**, the embed has **no title**
* Multiple attachments result in **multiple embeds**, all sharing the same title (if provided)

### Links

* Supported links are detected via regex
* Metadata (title + thumbnail) is fetched and embedded

---

## 🔁 Slash Commands

### `/refresh_server`

Scans all text channels and embeds any messages that were missed previously.

> Requires permissions to read message history and manage messages.

---

## 🔒 Permissions Required

The bot requires:

* View Channels
* Read Message History
* Send Messages
* Embed Links
* Attach Files
* Manage Messages (optional, for cleanup)

---

## 📜 Compliance & Responsibility

* This bot does **not** host or distribute content
* All media originates from Discord users
* Server owners are responsible for:

  * Marking NSFW channels appropriately
  * Moderating content
  * Complying with Discord ToS and local laws

---

## ⚠️ Disclaimer

This software is provided **as-is**, without warranty of any kind.
The author is not responsible for how this bot is deployed or used.
