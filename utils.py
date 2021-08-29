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


def add_to_embed(embed, value):
    last_field = embed.fields[-1]
    embed.set_field_at(
        -1,
        name=last_field.name,
        value=last_field.value + value
    )
