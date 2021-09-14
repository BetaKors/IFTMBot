import logging
import discord
import pickle
import utils
import os

from assignment_scraper import load_assignment_groups

from datetime import datetime, timedelta
from discord.ext import commands, tasks


class Assignments(commands.Cog, name='Tarefas'):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('IFTMBot')
        self.groups = []
        self.load_assignments.start()
    
    def cog_unload(self):
        if self.groups:
            with open('tarefas.pkl', 'wb') as f:
                pickle.dump(self.groups, f, pickle.HIGHEST_PROTOCOL)
        self.load_assignments.cancel()

    @commands.command(name='tarefas')
    async def assignments(self, ctx, page: int=None):
        if page is None:
            await self._list_assignments(ctx)
        else:
            await self._assignment_info(ctx, page)

    @tasks.loop(seconds=1)
    async def load_assignments(self):
        self.last_updated = datetime.now()

        self.logger.debug('Loading assignments...')
        self._load_groups()
        self.logger.debug('Assignments loaded!')

        when_to_update = self.last_updated + timedelta(minutes=30)
        
        self.logger.debug(f'Updating at {when_to_update}')
        await utils.wait_until(when_to_update)

    async def _list_assignments(self, ctx):
        note1 = '\n`*tarefas <página>` para mais informações\n'
        note2 = f'\n`Atualizado pela última vez {utils.dt_as_formatted_str(self.last_updated).lower()}`'

        embed = discord.Embed(
            title='Lista de tarefas',
            color=0xf92659
        )

        utils.set_default_footer(embed)
        
        for group in self.groups[:5]:
            value = ''.join(
                f'\n**[{a.dt.strftime("%d/%m")}] {a.subject}: {a.title}**\n'
                for a in group.assignments
            )

            embed.add_field(
                name=group.course_name,
                value=value
            )

        if embed.fields:
            utils.add_to_embed(embed, note1 + note2)

            await ctx.reply(embed=embed)
        
        else:
            raise commands.errors.CommandInvokeError()

    async def _assignment_info(self, ctx, page: int):
        if page > self.page_number:
            raise utils.IFTMBotError('Essa página não existe!')

        note = f'\n\n`Atualizado pela última vez às {utils.dt_as_formatted_str(self.last_updated)}`'
      
        embed = discord.Embed(
            title=f'Tarefas (Página {page} de {self.page_number})',
            color=0xf92659
        )

        utils.set_default_footer(embed)

        for group in self.groups:
            if len(group.assignments) < page:
                continue

            # determina se a nota será adicionada ou não (sim se o grupo for o último da lista)
            n = note if group == self.groups[-1] else ''

            embed.add_field(
                name=group.course_name,
                value=group.assignments[page-1].get_value(n)
            )

        if embed.fields:
            utils.add_to_embed(embed, note)

            await ctx.reply(embed=embed)

        else:
            raise commands.errors.CommandInvokeError()

    def _load_groups(self):
        if os.path.exists('./tarefas.pkl'):
            modified_unix_time = os.path.getmtime('./tarefas.pkl')

            motified_dt = utils.unix_timestamp_to_local_dt(modified_unix_time).replace(tzinfo=None)
            
            seconds_since = (datetime.now() - motified_dt).total_seconds()
            minutes_since = seconds_since // 60
        
        else:
            minutes_since = 0

        if minutes_since < 30:
            groups = self._load_save()
        else:
            groups = load_assignment_groups()

        # só atualize os grupos caso a lista groups tiver algo
        # se ela não tiver é porque algo deu errado, então mantenha os grupos que já estavam carregados (se eles estivessem carregados)
        if not self.groups or groups:
            self.groups = groups
        else:
            self.groups = self._load_save()

        self._clean_assignments()

        if self.groups:
            self.page_number = max(
                len(group.assignments)
                for group in self.groups
            )
        
        else:
            self.page_number = -1

    def _clean_assignments(self):
        # quando o ava fica offline o bot não consegue atualizar as tarefas,
        # então precisamos fazer isso para limpar as tarefas que já passaram
        now = datetime.now().date()
        
        for group in self.groups:
            for a in reversed(group.assignments):
                if a.dt.replace(tzinfo=None).date() < now:
                    group.assignments.remove(a)


    def _load_save(self):
        with open('./tarefas.pkl', 'rb') as f:
            return pickle.load(f)


def setup(bot):
    cog = Assignments(bot)
    bot.add_cog(cog)
