import constants
import logging
import discord
import utils

from traceback import format_exception
from discord.utils import get, find
from discord.ext import commands
from json import load


class Events(utils.HiddenCog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('IFTMBot')
        with open('error_messages.json', 'r', encoding='utf-8') as f:
            self.error_msgs = load(f)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('Bot started successfully!')
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name=f'IFTMBot | {constants.PREFIX}help'
            )
        )
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        t = type(error)
        name = t.__name__
        msg = str(error)

        if t is not utils.IFTMBotError or not msg:
            if name in self.error_msgs.keys():
                msg = self.error_msgs[name]

        embed = discord.Embed(color=0xff0000)
        utils.set_default_footer(embed)

        embed.add_field(
            name=f':x: ERRO :x:',
            value=msg if msg else 'Oops! Algo deu errado!'
        )

        if t is not utils.IFTMBotError:
            self.logger.error(
                '\n'.join(format_exception(t, error, error.__traceback__))
            )

        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        self._greet_goodbye(member, 'Bem-vindo')

        role_name = 'Bots' if member.bot else 'Membro'
        role = get(member.guild.roles, name=role_name)

        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_leave(self, member):
        self._greet_goodbye(member, 'Adeus')

    # sshh não consegui pensar em um nome melhor pra esse método
    async def _greet_goodbye(self, member, message):
        channel = find(lambda c: 'boas' in c.name, member.guild.text_channels)

        embed = discord.Embed(color=0xf92659)
        embed.set_thumbnail(url=member.avatar_url)
        utils.set_default_footer(embed)

        embed.add_field(
            name=message,
            value=f'{message}, {member.name}!'
        )

        await channel.send(embed=embed)


def setup(bot):
    cog = Events(bot)
    bot.add_cog(cog)