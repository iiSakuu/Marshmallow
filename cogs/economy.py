import discord
from discord.ext import commands
import asqlite


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        '''Shows how much you have in your balance'''

        if member is None:
            member = ctx.author

        money = await ctx.bot.con.fetchone('SELECT * FROM Currency WHERE userid=$1', member.id)
        if money is None:
            await ctx.bot.con.execute('INSERT INTO Currency (userid) VALUES ($1)', member.id)
            newmoney = await ctx.bot.con.fetchone('SELECT * FROM Currency WHERE userid=$1', member.id)
            await ctx.send(f'Your starting balance is `{newmoney["moneys"]}`')
        else:
            await ctx.send(f'Your balance is `{money["moneys"]}` marshmallows.')

    @commands.is_owner()
    @commands.command()
    async def givemoney(self, ctx, member: discord.Member, amount: int):
        '''OP asf spawn money from nowhere - owner only for a reason
           Become the government?'''

        spawnmoneyoutofnowhere = await ctx.bot.con.fetchone('SELECT * FROM Currency WHERE userid=$1', member.id)
        if spawnmoneyoutofnowhere is not None:
            finalamount = (amount + spawnmoneyoutofnowhere['moneys'])
            await ctx.bot.con.execute('UPDATE Currency SET moneys=$1 WHERE userid=$2', finalamount, member.id)
        else:
            await ctx.bot.con.fetchone('INSERT INTO Currency (userid, moneys) VALUES ($1, $2)', member.id, amount)
        await ctx.send(f'Successfully given ``{amount}`` marshmallows to **{member.name}**')

def setup(bot):
    bot.add_cog(Economy(bot))
