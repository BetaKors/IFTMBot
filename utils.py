import constants
import asyncio

from datetime import datetime, timezone, timedelta
from discord.ext import commands


months = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']


class HiddenCog(commands.Cog):
    """Igual a um Cog comum, mas não aparece na mensagem de ajuda."""
    pass


class IFTMBotError(commands.errors.CommandError):
    """Usado para mensagens de erro customizadas."""
    pass


async def wait_until(dt):
    await asyncio.sleep((dt - datetime.now()).total_seconds())


def dt_as_formatted_str(dt):
    r = ''
    today = datetime.today()
    tomorrow = today + timedelta(days=1)

    if dt.date() == today.date():
        r = 'Hoje'

    elif dt.date() == tomorrow.date():
        r = 'Amanhã'

    else:
        r = f'{dt.day} de {months[dt.month - 1]}'

    time = dt.strftime('%H:%M')

    return f'{r} às {time}'


def unix_timestamp_to_local_dt(timestamp):
    utc_dt = datetime.utcfromtimestamp(int(timestamp))

    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def set_default_footer(embed):
    embed.set_footer(text=f'IFTMBot | v{constants.VERSION}')


def add_to_embed(embed, value):
    last_field = embed.fields[-1]
    embed.set_field_at(
        -1,
        name=last_field.name,
        value=last_field.value + value
    )
