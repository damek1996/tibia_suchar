import os
import discord
from discord import app_commands
from discord.ext import tasks, commands
from google import genai  # Nowa biblioteka
import datetime
import pytz
import asyncio

# --- KONFIGURACJA ---
TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Nowa konfiguracja Klienta Google GenAI
client = genai.Client(api_key=GEMINI_KEY)

class TibiaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        if not daily_joke_loop.is_running():
            daily_joke_loop.start()

bot = TibiaBot()
POLAND_TZ = pytz.timezone("Europe/Warsaw")
TARGET_TIME = datetime.time(hour=9, minute=0, tzinfo=POLAND_TZ)

async def get_ai_joke():
    """Pobiera suchara używając najnowszego modelu"""
    prompt = (
        "Jesteś prowadzącym Tibijską Familiadę. Napisz krótki, suchy żart o grze Tibia "
        "(slang: depo, hunt, PK, kick, red skull). Styl Karola Strasburgera. "
        "Na koniec dodaj 'tutu-tutu'!"
    )
    # Używamy najnowszego modelu gemini-2.0-flash
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text

@tasks.loop(time=TARGET_TIME)
async def daily_joke_loop():
    if not CHANNEL_ID: return
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        joke = await get_ai_joke()
        await channel.send(f"☀️ **PORANNY SUCHAR DNIA** ☀️\n\n{joke}")

@bot.tree.command(name="daj_suchara", description="Generuje świeżego, tibijskiego suchara!")
async def daj_suchara(interaction: discord.Interaction):
    # Najpierw wysyłamy szybką odpowiedź, żeby Discord nie zerwał połączenia (unikamy 404)
    await interaction.response.send_message("🔍 Karol Strasburger szuka kartki z żartem...", ephemeral=False)
    
    try:
        joke = await get_ai_joke()
        # Edytujemy poprzednią wiadomość zamiast wysyłać nową
        await interaction.edit_original_response(content=f"🤣 **Suchar na prośbę {interaction.user.display_name}:**\n\n{joke}")
    except Exception as e:
        print(f"Błąd AI: {e}")
        await interaction.edit_original_response(content="Niestety, kartka z żartem wpadła do wody w Venore. Spróbuj za chwilę!")

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}!')
    await bot.change_presence(activity=discord.Game(name="Tibijska Familiada | /daj_suchara"))

bot.run(TOKEN)
