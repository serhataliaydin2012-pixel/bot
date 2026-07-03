import os
import sys
import asyncio
import discord
import logging
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from keep_alive import keep_alive

# ==========================
# ORTAM DEĞİŞKENLERİ
# ==========================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)

# ==========================
# WINDOWS DESTEĞİ
# ==========================

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ==========================
# INTENTS
# ==========================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True

# ==========================
# BOT
# ==========================

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,
    case_insensitive=True
)

# ==========================
# BOT DURUMU
# ==========================

async def update_status():

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} Sunucu"
        ),
        status=discord.Status.online
    )

# ==========================
# EVENTLER
# ==========================

@bot.event
async def on_ready():

    logging.info("=" * 40)
    logging.info(f"Lupin Guard aktif: {bot.user}")
    logging.info(f"Sunucu Sayısı: {len(bot.guilds)}")
    logging.info("=" * 40)

    await update_status()

    try:
        synced = await bot.tree.sync()
        logging.info(f"{len(synced)} Slash Komutu senkronize edildi.")
    except Exception as e:
        logging.error(e)

# ==========================
# YARDIM KOMUTU
# ==========================

@bot.command(name="yardim")
async def help_command(ctx):

    embed = discord.Embed(
        title="🛡️ Lupin Guard",
        description="Profesyonel Moderasyon Botu",
        color=0x5865F2
    )

    embed.add_field(
        name="Moderasyon",
        value="""
`!sil`
`!ban`
`!kick`
`!timeout`
`!warn`
""",
        inline=False
    )

    embed.add_field(
        name="AutoMod",
        value="""
Küfür Koruması
Reklam Koruması
Spam Koruması
Flood Koruması
""",
        inline=False
    )

    embed.set_footer(text="Lupin Guard v1.0")

    await ctx.send(embed=embed)

# ==========================
# TEST
# ==========================

@bot.tree.command(
    name="ping",
    description="Botun gecikmesini gösterir."
)
async def slash_ping(interaction: discord.Interaction):

    ms = round(bot.latency * 1000)

    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Gecikme: **{ms} ms**",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

# ==========================
# KEEP ALIVE
# ==========================

keep_alive()

# ==========================
# TOKEN
# ==========================

if TOKEN is None:
    raise Exception("DISCORD_TOKEN bulunamadı!")

bot.run(TOKEN)