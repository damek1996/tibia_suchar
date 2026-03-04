import discord
from discord.ext import tasks, commands
import google.generativeai as genai
import datetime

# --- KONFIGURACJA ---
GEMINI_KEY = "AIzaSyAle5ezENBqiDuAH1t-TBEUR12xUFk_w6o"
DISCORD_TOKEN = "MTQ3ODg4NjMyMzMxMjkxODU3OQ.GD4360.uA9mN5OFgHxwCzjC4Xbxl-tBWnDRjXu4J9H6_Q"
CHANNEL_ID = 1413797945601425418  # Kliknij prawym na kanał na Discordzie -> Kopiuj ID

# Konfiguracja AI
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # Szybki i darmowy model

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@tasks.loop(time=datetime.time(hour=9, minute=0)) # Codziennie o 09:00
async def daily_joke():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        prompt = "Jesteś Karolem Strasburgerem w świecie gry Tibia. Napisz krótki, suchy żart o graczach, potworach lub mechanikach Tibii. Zakończ go 'tutu-tutu'!"
        response = model.generate_content(prompt)
        await channel.send(f"🏆 **TIBIJSKA FAMILIADA: SUCHAR DNIA** 🏆\n\n{response.text}")

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}! Tibijczyk gotowy do żartów.')
    if not daily_joke.is_running():
        daily_joke.start()

bot.run(DISCORD_TOKEN)
