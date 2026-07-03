import discord
from discord.ext import commands
import re

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bad_words = [
            "elma",
            "armut",
            "yasak"
        ]

    def normalize(self, text: str):
        text = text.lower()

        cevir = str.maketrans({
            "ç": "c",
            "ğ": "g",
            "ı": "i",
            "ö": "o",
            "ş": "s",
            "ü": "u"
        })

        return text.translate(cevir)

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        content = self.normalize(message.content)

        for word in self.bad_words:
            if re.search(rf"\b{word}\b", content):
                try:
                    await message.delete()
                    await message.channel.send(
                        f"⚠️ {message.author.mention} yasaklı kelime kullandı.",
                        delete_after=5
                    )
                except:
                    pass
                return

async def setup(bot):
    await bot.add_cog(AutoMod(bot))