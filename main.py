import constants
import logging
import glob
import log
import os

from discord.ext import commands
from time import perf_counter
from help import Help

logger = logging.getLogger('IFTMBot')
log.setup_logger()

bot = commands.Bot(
    command_prefix=constants.PREFIX,
    case_insensitive=True,
    help_command=Help()
)

# TESTE

@bot.is_owner
@bot.command(aliases=['r'], hidden=True)
async def reload(ctx):
    logger.debug(f'User {ctx.author.name} started a reload.')
    t  = perf_counter()
    _load_reload()
    t2 = perf_counter()
    logger.debug(f'Reload took {t2 - t:2f}s')
    await ctx.message.delete()


@bot.is_owner
@bot.command(aliases=['update'], hidden=True)
async def update_assignments(ctx):
    bot.reload_extension('cogs.assignments')
    await ctx.message.delete()


def _load_reload():
    extensions = [
        f'cogs.{os.path.basename(file)[:-3]}'
        for file in glob.glob('./cogs/*.py')
        if file != './cogs\\__init__.py'
    ]

    for loaded_extension in list(bot.extensions.keys()):
        if loaded_extension not in extensions:
            logger.debug(f'Unloading extension {loaded_extension}')
            bot.unload_extension(loaded_extension)

    for extension in extensions:
        if extension in bot.extensions.keys():
            # ignorando assignments.py no reload para que ele não fique abrindo o ava todo reload
            if extension == 'cogs.assignments':
                logger.debug('Ignoring the reload of cogs.assignments')
                continue
            logger.debug(f'Reloading extension {extension}')
            bot.reload_extension(extension)        
        else:
            logger.debug(f'Loading extension {extension}')
            bot.load_extension(extension)


_load_reload()

with open('./token.txt', 'r') as f:
    token = f.readline().strip()

bot.run(token)
