import os
import discord
from discord.ext import tasks, commands
import google.generativeai as genai
import datetime
import pytz # Obsługa stref czasowych, żeby 09:00 było polskie

# --- POBIERANIE DANYCH Z KOŃCÓWKI SYSTEMOWEJ (RAILWAY) ---
TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Konfiguracja AI Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Konfiguracja Bota Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Definicja godziny 09:00 w polskiej strefie czasowej
POLAND_TZ = pytz.timezone("Europe/Warsaw")
TARGET_TIME = datetime.time(hour=9, minute=0, tzinfo=POLAND_TZ)

@tasks.loop(time=TARGET_TIME)
async def daily_joke():
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        try:
            prompt = (
                "Jesteś prowadzącym Tibijską Familiadę. Napisz krótki, bardzo suchy żart "
                "dotyczący gry Tibia (np. o PK-erach, lootowaniu, skillowaniu lub miastach). "
                "Używaj slangu graczy. Na koniec dodaj kultowe 'tutu-tutu' lub dźwięk 'X X X'."
            )
            response = model.generate_content(prompt)
            await channel.send(f"☀️ **TIBIJSKI SUCHAR DNIA** ☀️\n\n{response.text}")
        except Exception as e:
            print(f"Błąd AI: {e}")

@bot.command()
async def suchar(ctx):
    """Komenda ręczna, gdyby ktoś chciał żart od razu"""
    prompt = "Napisz szybki suchar o Tibii w stylu Karola Strasburgera."
    response = model.generate_content(prompt)
    await ctx.send(response.text)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} wystartował pomyślnie!')
    if not daily_joke.is_running():
        daily_joke.start()

bot.run(TOKEN)
