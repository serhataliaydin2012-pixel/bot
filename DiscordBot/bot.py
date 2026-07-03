import os
import threading
import discord
from discord.ext import commands
from dotenv import load_dotenv
from web.app import run as web_run

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- WEB ----------------
def start_web():
    web_run()

# ---------------- BOT ----------------
@bot.event
async def on_ready():
    print(f"Bot aktif: {bot.user}")

@bot.command()
async def test(ctx):
    await ctx.send("Bot çalışıyor ✅")

# ---------------- START ----------------
if __name__ == "__main__":
    threading.Thread(target=start_web).start()
    bot.run(TOKEN)
    