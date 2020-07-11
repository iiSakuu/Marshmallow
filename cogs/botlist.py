import dbl
import discord
from discord.ext import commands, tasks

import asyncio
import logging


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjMzMTg5MDcwNjg2NjExMDQ2NSIsImJvdCI6dHJ1ZSwiaWF0IjoxNTkzNzg4NjUyfQ.OjQECsp-m_TfWBXq4nVIF53hayctIBcB8bWGvoMzSSc'  # set this to your DBL token
        self.dblpy = dbl.DBLClient(self.bot, self.token)
        self.update_stats.start()

    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        try:
            await self.dblpy.post_guild_count()
            print('Updated.')
        except:
            import traceback
            traceback.print_exc()

    @update_stats.after_loop
    async def post_loop(self):
        if self.update_stats.failed():
            print('Failed')
            import traceback
            error = self.update_stats.get_task().exception()
            traceback.print_exception(type(error), error, error.__traceback__)



def setup(bot):
    bot.add_cog(TopGG(bot))
