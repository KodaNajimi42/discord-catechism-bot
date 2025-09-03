# discord-catechism-bot
A simple self-hosting bot that fetches information about the Catechism of the Catholic Church.

## Credits
This bot was made by Louie Polk.
Contact: louiepolk (Discord)
## My Contributions
- Updated a bit of the python code to be hosted on linux as opposed to macOS
- Server deployment and systemd configuration


# Discord Catechism Bot Setup

## Prerequisites
- Python 3.7+
- Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/discord-catechism-bot.git
cd discord-catechism-bot
```

### 2. Set up Python virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure the bot
1. Open `bot.py` in a text editor
2. Replace `YOUR_DISCORD_BOT_TOKEN_HERE` with your actual Discord bot token

### 4. Test the bot
```bash
python bot.py
```

## Systemd Service Setup (Linux)

To run the bot automatically as a system service:

### 1. Copy the service file
```bash
sudo cp systemd/discord-catechism-bot.service /etc/systemd/system/
```

### 2. Edit the service file
```bash
sudo micro /etc/systemd/system/discord-catechism-bot.service
```

Update these paths to match your setup:
- `YOUR_USERNAME` → your actual username
- `/path/to/discord-catechism-bot` → full path to your bot directory

Example:
```ini
User=john
WorkingDirectory=/home/john/discord-catechism-bot
ExecStart=/home/john/discord-catechism-bot/venv/bin/python /home/john/discord-catechism-bot/bot.py
```

### 3. Enable and start the service
```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-catechism-bot
sudo systemctl start discord-catechism-bot
```

### 4. Check service status
```bash
sudo systemctl status discord-catechism-bot
```

### 5. View logs
```bash
sudo journalctl -u discord-catechism-bot -f
```

## Usage
Once running, the bot will respond to commands in your Discord server. See the bot's help command for available features.

## Stopping the Service
```bash
sudo systemctl stop discord-catechism-bot
sudo systemctl disable discord-catechism-bot
```
