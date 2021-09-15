import discord
import aiohttp
import asyncio

from utils import set_default_footer

from discord.ext import commands


class IFTM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ava(self, ctx):
        embed = await self._ping_website('Ava', 'https://ava.upt.iftm.edu.br/login/index.php')

        await ctx.reply(embed=embed)

    @commands.command()
    async def virtualif(self, ctx):
        embed = await self._ping_website('VirtualIF', 'https://virtualif.iftm.edu.br/VRTL/')

        await ctx.reply(embed=embed)
    
    @commands.command(aliases=['tabela', 'tabelaperiodica'])
    async def tabela_periodica(self, ctx):
        embed = discord.Embed(color=0xf92659)
        set_default_footer(embed)

        embed.set_image(
            url='https://files.passeidireto.com/a6ac3afe-cf6f-4873-a672-29702eff8568/a6ac3afe-cf6f-4873-a672-29702eff8568.jpeg'
        )

        await ctx.reply(embed=embed)

    async def _ping_website(self, name, url):
        timeout = aiohttp.ClientTimeout(total=3)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    status = response.status == 200
        except asyncio.TimeoutError:
            status = False

        emoji = ':white_check_mark:' if status else ':x:'
        msg = 'ONLINE' if status else 'OFFLINE'

        embed = discord.Embed(
            color=0x00ff00 if status else 0xff0000
        )

        embed.add_field(
            name=f'{emoji} {msg} {emoji}',
            value=f'{name} está {msg.lower()}.'
        )

        set_default_footer(embed)

        return embed


def setup(bot):
    cog = IFTM(bot)
    bot.add_cog(cog)
