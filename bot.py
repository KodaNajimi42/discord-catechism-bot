# Original bot created by Louie Polk
# Modified and deployed by Koda Khan
# 07/05/2025

import os
import re
import discord
from discord.ext import commands
from discord import app_commands

# --- Configuration ---
LOCAL_FILE_PATH = "catechism.txt"

# --- Global variable to cache Catechism text (loaded from local file) ---
CACHED_CATECHISM_CONTENT = None

# --- Offline Text Retrieval Function ---
def get_catechism_text_offline(file_path: str = LOCAL_FILE_PATH) -> str | None:
    """
    Reads the Catechism text content from a local file.
    """
    if not os.path.exists(file_path):
        print(f"Local file '{file_path}' not found.")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"Successfully loaded Catechism text from: {file_path}")
        return content
    except IOError as e:
        print(f"Error reading local file '{file_path}': {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        return None

# --- Quote Search Function ---
def find_catechism_quote(text_content: str, quote_id: str) -> str | None:
    """
    Searches for a specific Catechism quote within the provided text content.
    Handles cleaning of extra spaces and filters out random numbers.
    """
    # Refined regex to find the paragraph associated with the quote_id.
    # It looks for the number at the start of a line, followed by any whitespace/newlines,
    # then captures everything until the next line that starts with a number, or the end of the document.
    paragraph_start_pattern = r"(?:\n|^)\s*" + re.escape(quote_id) + r"[\s\n]+(.+?)(?=\n\s*\d+|\Z)"
    
    paragraph_match = re.search(paragraph_start_pattern, text_content, re.DOTALL)

    if paragraph_match:
        found_text = paragraph_match.group(1).strip()
        
        # Clean the text
        cleaned_text = clean_catechism_text(found_text)
        return cleaned_text
    return None

def clean_catechism_text(text: str) -> str:
    """
    Improved cleaning function that preserves Bible verse references and handles parentheses correctly.
    """
    # Remove extra spaces between words (multiple spaces become single space)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove standalone numbers that are NOT part of:
    # - Bible verse references (like "Rom 5:29", "1 Cor 3:16", "Mt 5:3-12")
    # - Years (like "1994", "2000")
    # - Other legitimate number contexts
    
    # First, protect Bible verse references by temporarily replacing them
    # Common patterns: "Book Chapter:Verse", "1 Book Chapter:Verse", "Book Chapter:Verse-Verse"
    bible_refs = []
    bible_pattern = r'\b(?:[1-3]?\s*[A-Za-z]+\s+\d+:\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)\b'
    
    def replace_bible_ref(match):
        bible_refs.append(match.group(0))
        return f"__BIBLE_REF_{len(bible_refs)-1}__"
    
    text = re.sub(bible_pattern, replace_bible_ref, text)
    
    # Also protect years (4-digit numbers that could be years)
    year_refs = []
    year_pattern = r'\b(?:1[0-9]{3}|20[0-9]{2})\b'
    
    def replace_year_ref(match):
        year_refs.append(match.group(0))
        return f"__YEAR_REF_{len(year_refs)-1}__"
    
    text = re.sub(year_pattern, replace_year_ref, text)
    
    # Now remove standalone numbers that are likely section references or footnote numbers
    # This targets isolated numbers that appear alone, not as part of other text
    text = re.sub(r'\b\d+\b(?!\s*[:.]\d)', '', text)
    
    # Remove extra spaces that might be left after removing numbers
    text = re.sub(r'\s+', ' ', text)
    
    # Fix parentheses spacing issues - remove spaces before closing parentheses
    text = re.sub(r'\s+\)', ')', text)
    # Remove spaces after opening parentheses
    text = re.sub(r'\(\s+', '(', text)
    
    # Restore Bible verse references
    for i, bible_ref in enumerate(bible_refs):
        text = text.replace(f"__BIBLE_REF_{i}__", bible_ref)
    
    # Restore year references
    for i, year_ref in enumerate(year_refs):
        text = text.replace(f"__YEAR_REF_{i}__", year_ref)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

# --- Discord Bot Setup ---
# Replace this line:
# bot.run('your_actual_bot_token_here')
DISCORD_BOT_TOKEN = 'YOUR_DISCORD_BOT_TOKEN_HERE'

intents = discord.Intents.default()
intents.message_content = True # Required to read message content from users

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """
    Event that fires when the bot successfully connects to Discord.
    Loads the Catechism text from the local file and syncs slash commands.
    """
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    print("Bot invite URL with recommended permissions:")
    print(f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=2147486720&scope=bot%20applications.commands")
    print("Loading Catechism text from local file...")
    global CACHED_CATECHISM_CONTENT

    if not os.path.exists(LOCAL_FILE_PATH):
        print(f"ERROR: Local file '{LOCAL_FILE_PATH}' not found. Please ensure the file exists in the same directory as this script.")
        print("Bot will not be able to find quotes without this file.")
        return
    
    CACHED_CATECHISM_CONTENT = get_catechism_text_offline()
    if CACHED_CATECHISM_CONTENT:
        print("Catechism text loaded successfully from local file.")
    else:
        print("Failed to load Catechism text from local file. Bot may not function correctly.")
    
    # Sync slash commands globally and to current guilds
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s) globally")
        
        # Also sync to all guilds the bot is in for immediate updates
        for guild in bot.guilds:
            try:
                guild_synced = await bot.tree.sync(guild=guild)
                print(f"Synced {len(guild_synced)} slash command(s) to {guild.name}")
            except Exception as guild_e:
                print(f"Failed to sync to guild {guild.name}: {guild_e}")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

@bot.tree.command(name='ping', description='Test bot responsiveness and latency')
async def ping_slash(interaction: discord.Interaction):
    """
    Slash command to test bot responsiveness and latency.
    """
    latency = round(bot.latency * 1000)  # Convert to milliseconds
    await interaction.response.send_message(f'Pong! 🏓 Latency: {latency}ms')

@bot.event
async def on_message(message):
    """
    Event that fires when a message is sent in any channel the bot can see.
    Checks for "CCC [number]" patterns and responds automatically.
    """
    # Ignore messages from the bot itself to prevent infinite loops
    if message.author == bot.user:
        return

    # Regex to find "CCC" followed by an optional dot and a number
    # It's case-insensitive and captures the number.
    match = re.search(r"[Cc][Cc][Cc]\.?\s*(\d+)", message.content)

    if match:
        quote_id = match.group(1) # Extract the captured number
        print(f"Detected CCC quote request: {quote_id}")  # Debug line

        if not CACHED_CATECHISM_CONTENT:
            await message.channel.send("Sorry, the Catechism text is not loaded. Please ensure the 'catechism.txt' file exists.")
            return

        found_quote = find_catechism_quote(CACHED_CATECHISM_CONTENT, quote_id)

        if found_quote:
            # Truncate the quote if it's too long for a Discord embed (max 4096 characters for description).
            if len(found_quote) > 4000: # Leave some room for formatting
                found_quote = found_quote[:4000] + "...\n(Quote too long, truncated.)"
            
            # Create a rich embed with Vatican colors
            embed = discord.Embed(
                title=f"📖 CCC {quote_id}",
                description=found_quote,
                color=0xFFD700  # Vatican yellow/gold hex color
            )
            
            # Add footer with bot info
            embed.set_footer(
                text="Catechism Bot • Made by Louiepolk",
                icon_url="https://cdn.discordapp.com/attachments/1234567890/example.png"  # Optional: Add bot avatar
            )
            
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(f"Could not find Catechism quote with ID: `{quote_id}`. Please check the number.")
    
    # This line is important: it allows other commands (if any are defined with `bot.command`)
    # to still be processed after our on_message event.
    await bot.process_commands(message)

if __name__ == "__main__":
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        print("ERROR: Invalid Discord bot token. Please check your token.")
    except Exception as e:
        print(f"An error occurred while running the bot: {e}")
