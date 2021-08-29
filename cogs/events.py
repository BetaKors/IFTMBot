import constants
import logging
import discord
import utils

from traceback import format_exception
from discord.utils import get, find
from discord.ext import commands


class Events(utils.HiddenCog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('IFTMBot')
    
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

        embed = discord.Embed(color=0xff0000)
        utils.set_default_footer(embed)

        embed.add_field(
            name=f':x: {t.__name__} :x:',
            value='Oops! Um erro ocorreu!'
        )


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