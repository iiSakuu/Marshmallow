from discord.ext import commands
import discord


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def load(self, ctx, *, message: str):
        try:
            self.bot.load_extension(f'cogs.{message}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.is_owner()
    @commands.command()
    async def unload(self, ctx, *, message: str):
        try:
            self.bot.unload_extension(f'cogs.{message}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, *, message: str):
        try:
            self.bot.unload_extension(f'cogs.{message}')
            self.bot.load_extension(f'cogs.{message}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.is_owner()
    @commands.command()
    async def say(self, ctx, *, echo: str):
        await ctx.message.delete()
        await ctx.send(echo)

    @commands.is_owner()
    @commands.command()
    async def kill(self, ctx):
        await ctx.send('Beep boop, shutting down.')
        await self.bot.logout()

    @commands.is_owner()
    @commands.command()
    async def setnick(self, ctx, member: discord.Member, message: str, *, reason=None):
        await ctx.message.delete()
        await member.edit(nick=message, reason=reason)
        await ctx.send(f'Changed my nickname to `{message}`.')


def setup(bot):
    bot.add_cog(Owner(bot))
