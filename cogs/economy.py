import discord
from discord.ext import commands
import asqlite
import random
import datetime


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        '''Shows how much you have in your balance'''

        if member is None:
            member = ctx.author

        money = await ctx.bot.con.fetchone('SELECT * FROM Currency WHERE user_id=$1', member.id)
        if money is None:
            await ctx.bot.con.execute('INSERT INTO Currency (user_id) VALUES ($1)', member.id)
            newmoney = await ctx.bot.con.fetchone('SELECT * FROM Currency WHERE user_id=$1', member.id)
            await ctx.send(f'Your starting balance is `{newmoney["moneys"]}`')
        else:
            await ctx.send(f'Your balance is `{money["moneys"]}` marshmallows.')

    @commands.is_owner()
    @commands.command()
    async def givemoney(self, ctx, member: discord.Member, amount: int):
        '''OP asf spawn money from nowhere - owner only for a reason
           Become the government?'''

        spawnmoneyoutofnowhere = await ctx.bot.con.fetchone('SELECT * FROM Currency WHERE user_id=$1', member.id)
        if spawnmoneyoutofnowhere is not None:
            finalamount = (amount + spawnmoneyoutofnowhere['moneys'])
            await ctx.bot.con.execute('UPDATE Currency SET moneys=$1 WHERE user_id=$2', finalamount, member.id)
        else:
            await ctx.bot.con.fetchone('INSERT INTO Currency (user_id, moneys) VALUES ($1, $2)', member.id, amount)
        await ctx.send(f'Successfully given ``{amount}`` marshmallows to **{member.name}**')

    @commands.command()
    async def daily(self, ctx):
        '''Get a daily amount of money'''

        daily_amount = random.randint(30, 255)

        row = await ctx.bot.con.fetchone('SELECT * FROM Currency WHERE user_id=$1', ctx.author.id)

        if row is None:
            await ctx.bot.con.execute('INSERT INTO Currency (user_id, moneys, daily_time) VALUES ($1, $2, $3)', ctx.author.id, daily_amount, datetime.datetime.utcnow().strftime('%#d %m %Y %H:%M'))
            embed = discord.Embed(
                description=f'You have received `{daily_amount}`.',
                colour=0xffb5f7,
                timestamp=ctx.message.created_at
            )
            await ctx.send(embed=embed)
        elif row['daily_time'] is None:
            final_daily = (daily_amount + row['moneys'])
            embed = discord.Embed(
                description=f'You have received `{daily_amount}`! You now have `{final_daily}` marshmallows in the bank.',
                colour=0xffb5f7,
                timestamp=ctx.message.created_at
            )
            await ctx.bot.con.execute('UPDATE Currency SET moneys=$1, daily_time=$2 WHERE user_id=$3', final_daily, datetime.datetime.utcnow().strftime('%#d %m %Y %H:%M'), ctx.author.id)
            await ctx.send(embed=embed)
        elif (datetime.datetime.utcnow() - datetime.datetime.strptime(row['daily_time'], '%d %m %Y %H:%M')).total_seconds() >= 86400:
            final_daily = (daily_amount + row['moneys'])
            embed = discord.Embed(
                description=f'You have received `{daily_amount}`! You now have `{final_daily}` marshmallows in the bank.',
                colour=0xffb5f7,
                timestamp=ctx.message.created_at
            )
            await ctx.bot.con.execute('UPDATE Currency SET moneys=$1, daily_time=$2 WHERE user_id=$3', final_daily, datetime.datetime.utcnow().strftime('%#d %m %Y %H:%M'), ctx.author.id)
            await ctx.send(embed=embed)
        else:
            seconds_left = (86400 - (datetime.datetime.utcnow() - datetime.datetime.strptime(row['daily_time'], '%d %m %Y %H:%M')).total_seconds())
            minutes_left, seconds_left = divmod(int(seconds_left), 60)
            hours_left, minutes_left = divmod(minutes_left, 60)
            embed = discord.Embed(
                description=f"You've already used your daily for today! You have `{hours_left}:{minutes_left}` hours until you can use it again.",
                colour=0xffb5f7,
                timestamp=ctx.message.created_at
                )
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Economy(bot))
