import course_parser
import discord
import logging
import utils

from datetime import datetime, timedelta
from discord.ext import commands, tasks
from discord.utils import get, find


class Notify(commands.Cog, name='Aulas'):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('IFTMBot')
        self.courses = course_parser.load_courses()

        _courses = ' | '.join(str(c) for c in self.courses)
        self.logger.debug(f'Loaded courses: {_courses}')

        self.notify.start()
        self.update_courses.start()

    def cog_unload(self):
        self.notify.cancel()
        self.update_courses.cancel()

    @commands.command(name='aulas')
    async def classes(self, ctx):
        embed = discord.Embed(color=0xf92659)
        utils.set_default_footer(embed)

        fmt  = '• {} às {}'
        fmt2 = '\\> **{} às {}**'

        now = datetime.now()

        for c in self.courses:
            value = []
            
            for cl in c.classes:
                time_since = (cl.dt - now).total_seconds() / 60
                _fmt = fmt2 if time_since < 0 and time_since > -50 else fmt

                t = cl.dt.strftime('%H:%M')

                value.append(_fmt.format(cl.name, t))

            embed.add_field(
                name=c.name,
                value='\n'.join(value)
            )

        await ctx.reply(embed=embed)
    
    @commands.is_owner()
    @commands.command(aliases=['set'], hidden=True)
    async def set_link(self, ctx, course, url):
        last_notification = ctx.message.reference.resolved

        embed = last_notification.embeds[0]
        fields = embed.fields
        field = get(fields, name=course.upper())

        value = field.value.split('\n')
        value[1] = f'**Link:** {url}'

        embed.set_field_at(
            fields.index(field),
            name=field.name,
            value='\n'.join(value)
        )

        await ctx.message.delete()
        await last_notification.edit(embed=embed)

    @tasks.loop(seconds=1)
    async def notify(self):
        await self.bot.wait_until_ready()
        
        when_to_notify = min(c.get_next_class_dt() for c in self.courses)
        
        self.logger.debug(f'Notifying at {when_to_notify}')
        
        await utils.wait_until(when_to_notify)

        embed = discord.Embed(color=0xf92659)
        utils.set_default_footer(embed)

        for c in self.courses:
            embed.add_field(
                name=c.name,
                value=c.get_notify_value()
            )

        if embed.fields:
            channel = find(
                lambda c: 'aulas' in c.name,
                get(self.bot.guilds, name='IFTM').text_channels
            )

            await channel.send(embed=embed)
            self.logger.debug('Notified!')

    @tasks.loop(seconds=1)
    async def update_courses(self):
        tomorrow = datetime.now() + timedelta(days=1)
        midnight = tomorrow.replace(hour=0, minute=0, second=1)

        await utils.wait_until(midnight)

        self.logger.debug('Updating courses...')
        
        self.courses = course_parser.load_courses()
        
        courses = ' | '.join(str(c) for c in self.courses)
        self.logger.debug(f'Updated courses: {courses}')
        
        self.notify.restart()


def setup(bot):
    cog = Notify(bot)
    bot.add_cog(cog)