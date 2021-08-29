import constants
import asyncio

from discord.ext import commands
from datetime import datetime


class HiddenCog(commands.Cog):
    pass


def set_default_footer(embed):
    embed.set_footer(text=f'IFTMBot | v{constants.VERSION}')


async def wait_until(dt):
    await asyncio.sleep((dt - datetime.now()).total_seconds())
