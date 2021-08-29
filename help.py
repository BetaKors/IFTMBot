import constants
import discord
import utils

from discord.ext import commands


class Help(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        
    async def send_bot_help(self, mapping):
        embed = self._get_help_embed()

        for cog, commands in mapping.items():
            if isinstance(cog, utils.HiddenCog):
                continue

            command_names = self._format_commands(commands)

            if command_names:
                embed.add_field(
                    name=cog.qualified_name if cog else 'Outros',
                    value=command_names,
                    inline=True
                )

        await self.get_destination().send(embed=embed)
    
    async def send_cog_help(self, cog):
        embed = self._get_help_embed()

        command_names = self._format_commands(cog.get_commands())

        embed.add_field(
            name=cog.qualified_name,
            value=command_names
        )
    
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = self._get_help_embed()

        embed.add_field(
            name=self._format_command_full(command),
            value=self._get_command_desc(command)
        )

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = self._get_help_embed()

        group_commands = self._format_commands(list(group.commands))

        note = 'Nota: subcomandos tem que ser utilizados chamando o nome do comando pai e o nome do subcomando.'
        
        embed.add_field(
            name=self._format_command_full(group),
            value=self._get_command_desc(group)
        )

        embed.add_field(
            name='Subcomandos',
            value=f'{group_commands}\n\n{note}'
        )

        await self.get_destination().send(embed=embed)

    def _get_help_embed(self):
        embed = discord.Embed(
            title='Ajuda',
            colour=0xf92659
        )

        utils.set_default_footer(embed)
        
        return embed
    
    def _format_commands(self, commands):
        f_commands = '\n'.join(self._format_command(c) for c in commands if not c.hidden)
        return f_commands if f_commands else '`Essa categoria está vazia.`'

    def _format_command(self, command):
        cmd = f'{constants.PREFIX}{command.name}'
        if isinstance(command, commands.Group):
            return f'`{cmd} (grupo)`'
        return f'`{cmd}`'

    def _format_command_full(self, command):
        params = self._get_params(command)
        aliases = self._get_aliases(command)
        return f'{constants.PREFIX}{command.name} {params} {aliases}'

    def _get_command_desc(self, command):
        desc = command.description
        return desc if desc else 'Descrição não encontrada.'

    def _get_params(self, command):
        params = []
        
        for name, param in command.clean_params.items():
            if param.default is param.empty:
                params.append(name)
            else:
                params.append(f'{name} (opcional)')
        
        params = ', '.join(params)
        
        return f'<{params}>' if params else ''

    def _get_aliases(self, command):
        aliases = '|'.join(command.aliases)
        return f'[{aliases}]' if aliases else ''
