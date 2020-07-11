import random
import os
from discord.ext import commands
import discord
import asqlite


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
            await ctx.send(f"Here's your avatar! \n{member.avatar_url}")
        else:
            await ctx.send(f"Here's {member.mention}'s avatar! \n{member.avatar_url}")

    # userinfocommand
    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        picklechips = await ctx.bot.con.fetchone('SELECT month, day, year FROM Birthdays WHERE userid=$1', member.id)
        roles = [role for role in member.roles]

        userinfos = discord.Embed(
            title=f"{member.name}'s user info",
            colour=0xffb5f7,
            timestamp=ctx.message.created_at
        )
        userinfos.add_field(name='Username', value=member.name)
        userinfos.add_field(name='Nickname', value=member.display_name)
        userinfos.add_field(
            name='Created at',
            value=member.created_at.strftime('%a, %#d, %B, %Y, %I:%M %p UTC'),
            inline=False
        )
        userinfos.add_field(
            name='Joined at',
            value=member.joined_at.strftime('%a, %#d, %B, %Y, %I:%M %p UTC')
        )
        userinfos.add_field(
            name=f'Roles ({len(roles) - 1})',
            value=' '.join([role.mention for role in roles if not role.is_default()]),
            inline=False
        )
        userinfos.add_field(name='Top role:', value=member.top_role.mention)
        if picklechips is not None:
            userinfos.add_field(
                name='Birthday',
                value=f'{picklechips["month"]} {picklechips["day"]} {picklechips["year"]}'
            )
        userinfos.set_thumbnail(url=member.avatar_url)
        userinfos.set_footer(text=f'ID: {member.id}')

        await ctx.send(embed=userinfos)

    @commands.command(name='birthdayadd')
    async def birthdayadd(self, ctx, month, day: int, year: int):
        '''Example: >>birthdayadd April 1 1999
           Shows up on your user info.'''


        if day > 31:
            await ctx.send("Sorry, we don't accept aliens.")
        else:
            pekopeko = await ctx.bot.con.fetchone('SELECT * FROM Birthdays WHERE userid=$1', ctx.author.id)
            if pekopeko is not None:
                await ctx.bot.con.execute('UPDATE Birthdays SET month=$1, day=$2, year=$3 WHERE userid=$4', month, day, year, ctx.author.id)
                await ctx.send('Your birthday has been updated.')
            else:
                await ctx.bot.con.execute('INSERT INTO Birthdays (userid, month, day, year) VALUES ($1, $2, $3, $4)', ctx.author.id, month, day, year)
                await ctx.send('Your birthday has been added into the database.')

    @commands.command()
    async def ping(self, ctx):
        pong = discord.Embed(title='Pong!', color=0xffd6f1)
        pong.add_field(
            name='Latency',
            value=(f'{round(self.bot.latency * 1000)}ms')
        )
        await ctx.message.add_reaction(emoji='🏓')
        await ctx.send(embed=pong)

    @commands.command()
    async def roll(self, ctx, dice: str):
        # I wish this was better, soon^tm
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Format has to be in NdN!')
            return
        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.send(result)


    @commands.command()
    async def marshmallow(self, ctx):
        '''Sends random pictures of marshmallows'''
        result_marshmallow = random.choice(os.listdir('.//images//Marshmallows'))

        marshfile = discord.File(
            f'images//Marshmallows//{result_marshmallow}',
            filename=f'{result_marshmallow}'
        )
        givemarshmallow = discord.Embed(
            colour=0xffb5f7,
            timestamp=ctx.message.created_at
        )
        givemarshmallow.set_image(
            url=f'attachment://{result_marshmallow}'
        )

        await ctx.send(
            "Here's your marshmallow.",
            file=marshfile,
            embed=givemarshmallow
        )


def setup(bot):
    bot.add_cog(Misc(bot))
