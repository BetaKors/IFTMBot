import logging
import discord
import utils

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
        
        when_to_update = self._calculate_update_dt()
        self.logger.debug(f'Updating at {when_to_update}')
        
        await utils.wait_until(when_to_update)

    async def _list_assignments(self, ctx):
        note1 = '\n`*tarefas <página>` para mais informações\n'
        note2 = f'\n`Atualizado pela última vez às {self.last_updated.strftime("%H:%M:%S")}`'

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
            self._add_to_embed(embed, note1 + note2)

            await ctx.reply(embed=embed)
        
        else:
            raise commands.errors.CommandInvokeError()

    async def _assignment_info(self, ctx, page: int):
        last_updated_time = self.last_updated.strftime('%H:%M:%S')
        note = f'\n\n`Atualizado pela última vez às {last_updated_time}`'
      
        embed = discord.Embed(
            title=f'Tarefas (Página {page} de {self.page_number})',
            color=0xf92659
        )

        utils.set_default_footer(embed)

        for group in self.groups:
            # determina se a nota será adicionada ou não (sim se o grupo for o último da lista)
            n = note if group == self.groups[-1] else ''

            embed.add_field(
                name=group.course_name,
                value=group.assignments[page-1].get_value(n)
            )

        if embed.fields:
            self._add_to_embed(embed, note)

            await ctx.reply(embed=embed)

        else:
            raise commands.errors.CommandInvokeError()
    
    def _add_to_embed(self, embed, val):
        last_field = embed.fields[-1]
        embed.set_field_at(
            -1,
            name=last_field.name,
            value=last_field.value + val
        )

    # calcula quando atualizar as tarefas
    # é o menor entre 1 hora a partir do momento que a função for chamada ou o horário da tarefa mais próxima
    def _calculate_update_dt(self):
        now = datetime.now()
        one_hour_from_now = now + timedelta(hours=1)

        if not self.groups:
            return one_hour_from_now

        closest_assignment_dt = min(
            a.dt
            for group in self.groups
            for a in group.assignments
            if a.dt.replace(tzinfo=None) > now
        )

        # é necessario setar tzinfo pra None porque não é possível fazer comparações entre datetimes que tem tzinfo (como closest_assignment_dt) e que não tem (como one_hour_from_now)
        return min(
            closest_assignment_dt.replace(tzinfo=None),
            one_hour_from_now
        )
    
    def _load_groups(self):
        groups = load_assignment_groups()

        # só atualize os grupos caso a lista groups tiver algo
        # se ela não tiver é porque algo deu errado, então mantenha os grupos que já estavam carregados (se eles estivessem carregados)
        if not self.groups or groups:
            self.groups = groups
        
        if self.groups:
            self.page_number = max(
                len(group.assignments)
                for group in self.groups
            )
        
        else:
            self.page_number = -1


def setup(bot):
    cog = Assignments(bot)
    bot.add_cog(cog)
