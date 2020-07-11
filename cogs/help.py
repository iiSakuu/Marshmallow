import discord
from discord.ext import commands


class MyNewHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page, colour=0xffd6f1)
            await destination.send(embed=emby)


class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyNewHelp()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(client):
    client.add_cog(MyCog(client))
