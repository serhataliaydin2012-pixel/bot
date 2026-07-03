import discord
from discord.ext import commands
import asyncio
import sys
from keep_alive import keep_alive  # Uyku engelleyiciyi dahil ettik

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          
intents.guilds = True           

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print("----------------------------------------")
    print(f"BAŞARILI! Bot aktif: {bot.user.name}")
    print("----------------------------------------")

@bot.command()
async def test(ctx):
    await ctx.send(f"🤖 Bot bulut üzerinden mükemmel çalışıyor, {ctx.author.mention}!")

# KÜFÜR GUARD SİSTEMİ
YASAKLI_KELIMELER = ["elma", "armut", "yasaklikelime"]

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    mesaj_icerigi = message.content.lower()

    for kelime in YASAKLI_KELIMELER:
        if kelime in mesaj_icerigi:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, lütfen bu sunucuda yasaklı kelimeler kullanma!")
            except Exception as e:
                print(f"Mesaj silinirken hata: {e}")
            return 

    await bot.process_commands(message)

# Uyku engelleyiciyi başlatıyoruz
keep_alive()

import os
bot.run(os.environ['DISCORD_TOKEN'])