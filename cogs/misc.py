import random
import os
from discord.ext import commands
import discord
import asqlite
import psutil
import urllib.parse
import pendulum


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()
        self.bot.invite_url = f'https://discordapp.com/oauth2/authorize?client_id=331890706866110465&scope=bot&permissions=1375202551'

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
        guilds = [guild for guild in self.bot.guilds]

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

        ramUsage = self.process.memory_full_info().uss / 1024**2
        cpuUsage = self.process.cpu_percent() / psutil.cpu_count()
        now = pendulum.now()
        uptime = (now - self.bot.start_time)

        marshinfo = discord.Embed(
            title="Marshmallow's info",
            colour=0xffb5f7,
            timestamp=ctx.message.created_at
        )
        marshinfo.add_field(
            name='Nickname',
            value=member.display_name
        )
        marshinfo.add_field(
            name='Joined at',
            value=member.joined_at.strftime('%a, %#d, %B, %Y, %I:%M %p UTC')
        )
        marshinfo.add_field(
            name='Library',
            value=f'discord.py {discord.__version__}'
        )
        marshinfo.add_field(
            name='Servers',
            value=f'{len(guilds)}'
        )
        marshinfo.add_field(
            name='Member count',
            value=f'{len(self.bot.users)}'
        )
        marshinfo.add_field(
            name='Commands',
            value=len(self.bot.commands)
        )
        marshinfo.add_field(
            name='Latency',
            value=f'{round(self.bot.latency * 1000)}ms'
        )
        marshinfo.add_field(
            name='Memory Usage',
            value=f'{ramUsage:.2f}MiB'
        )
        marshinfo.add_field(
            name='CPU Usage',
            value=f'{cpuUsage:.2f}%'
        )
        marshinfo.add_field(
            name='Uptime',
            value=uptime.in_words(locale='en')
        )
        marshinfo.add_field(
            name='Links',
            value=f'[Invite me!]({self.bot.invite_url})'
        )
        marshinfo.set_thumbnail(url=member.avatar_url)
        marshinfo.set_footer(
            text=f'Requested by {ctx.author.display_name}',
            icon_url=ctx.author.avatar_url
        )

        if member.id == 331890706866110465:
            await ctx.send(embed=marshinfo)
        else:
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

    @commands.command()
    async def leavechannel(self, ctx, channel: discord.TextChannel):

        leave_channel = await ctx.bot.con.fetchone('SELECT * FROM Guild_Settings WHERE guild_id=$1', ctx.guild.id)

        if leave_channel is None:
            await ctx.bot.con.execute('INSERT INTO Guild_Settings (guild_id, leave_message_channel) VALUES ($1, $2)', ctx.guild.id, channel.id)
        else:
            await ctx.bot.con.execute('UPDATE Guild_Settings SET leave_message_channel=$1 WHERE guild_id=$2', channel.id, ctx.guild.id)
        await ctx.send('Updated your channel.')

    @commands.command()
    async def setleave(self, ctx, message: str):
        '''Sets whether or not you want Marshmallow to send leave messages
           Example: >>setleave TRUE'''

        checkleave = await ctx.bot.con.fetchone('SELECT * FROM Guild_Settings WHERE guild_id=$1', ctx.guild.id)

        if message == 'TRUE':
            await ctx.bot.con.execute('UPDATE Guild_Settings SET leave_message=$1 WHERE guild_id=$2', message, ctx.guild.id)
            await ctx.send('Updated to ``TRUE``.')

        elif message == 'FALSE':
            await ctx.bot.con.execute('UPDATE Guild_Settings SET leave_message=$1 WHERE guild_id=$2', message, ctx.guild.id)
            await ctx.send('Updated to ``FALSE``.')

        else:
            await ctx.send('Please provide either `TRUE` or `FALSE`.')

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        checkleave = await self.bot.con.fetchone('SELECT * FROM Guild_Settings WHERE guild_id=$1', member.guild.id)

        if checkleave['leave_message'] == 'FALSE':
            return

        guild_info = self.bot.get_guild(member.guild.id)
        leave_message_channel_id = checkleave['leave_message_channel']
        leave_message_channel = guild_info.get_channel(leave_message_channel_id)

        leave = discord.Embed(
            title='A user has left the server!',
            colour=0xffb5f7
        )
        leave.add_field(name='\u200b', value=f'{member.name}')
        leave.set_thumbnail(url=member.avatar_url)
        leave.set_footer(text=f'ID: {member.id}')

        await leave_message_channel.send(
            embed=leave
        )

def setup(bot):
    bot.add_cog(Misc(bot))
