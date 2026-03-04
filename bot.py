import os
import discord
from discord import app_commands
from discord.ext import tasks, commands
import google.generativeai as genai
import datetime
import pytz

# --- KONFIGURACJA ZMIENNYCH ---
TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Konfiguracja AI Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

class TibiaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Synchronizacja komend slash (/daj_suchara)
        await self.tree.sync()
        print("Komendy slash zsynchronizowane!")
        # Start pętli porannej (09:00)
        if not daily_joke_loop.is_running():
            daily_joke_loop.start()

bot = TibiaBot()

# Ustawienie strefy czasowej na Polskę
POLAND_TZ = pytz.timezone("Europe/Warsaw")
TARGET_TIME = datetime.time(hour=9, minute=0, tzinfo=POLAND_TZ)

async def get_ai_joke():
    """Łączy się z AI i pobiera suchara"""
    prompt = (
        "Jesteś prowadzącym Tibijską Familiadę. Napisz krótki, suchy żart o grze Tibia "
        "(użyj slangu: hunt, depo, PK, kick, red skull). Styl Karola Strasburgera. "
        "Na koniec dodaj 'tutu-tutu'!"
    )
    response = model.generate_content(prompt)
    return response.text

# --- PĘTLA AUTOMATYCZNA (09:00) ---
@tasks.loop(time=TARGET_TIME)
async def daily_joke_loop():
    if not CHANNEL_ID: return
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        joke = await get_ai_joke()
        await channel.send(f"☀️ **PORANNY SUCHAR DNIA** ☀️\n\n{joke}")

# --- KOMENDA DLA GRACZA: /daj_suchara ---
@bot.tree.command(name="daj_suchara", description="Generuje świeżego, tibijskiego suchara przez AI!")
async def daj_suchara(interaction: discord.Interaction):
    # Powiadomienie Discorda, że bot pracuje (unikamy timeoutu)
    await interaction.response.defer()
    
    try:
        joke = await get_ai_joke()
        await interaction.followup.send(f"🤣 **Suchar na prośbę {interaction.user.display_name}:**\n\n{joke}")
    except Exception as e:
        print(f"Błąd: {e}")
        await interaction.followup.send("Niestety, Karol Strasburger ma laga. Spróbuj za chwilę!")

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}!')
    await bot.change_presence(activity=discord.Game(name="Tibijska Familiada | /daj_suchara"))

bot.run(TOKEN)
