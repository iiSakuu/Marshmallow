import random
import os
from discord.ext import commands
import discord
import asqlite
import psutil
import urllib.parse
import pendulum
import traceback


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()
        self.bot.invite_url = f'https://discordapp.com/oauth2/authorize?client_id=331890706866110465&scope=bot&permissions=1375202551'

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        '''Display yours or someone else's avatar'''


        if member is None:
            member = ctx.author

            youravatar_embed = discord.Embed(
                colour=0xffb5f7,
                timestamp=ctx.message.created_at
            )
            youravatar_embed.set_image(
                url=member.avatar_url
            )

            await ctx.send(
                f"Here's your avatar!",
                embed=youravatar_embed
            )
        else:
            avatar_embed = discord.Embed(
                colour=0xffb5f7,
                timestamp=ctx.message.created_at
            )
            avatar_embed.set_image(
                url=member.avatar_url
            )
            await ctx.send(
                f"Here's {member.mention}'s avatar!",
                embed=avatar_embed
             )

    # userinfocommand
    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

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
        userinfos.set_thumbnail(url=member.avatar_url)
        userinfos.set_footer(text=f'ID: {member.id}')

        ramUsage = self.process.memory_full_info().uss / 1024**2
        cpuUsage = self.process.cpu_percent()
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

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        '''Show all your fancy info. Like userinfo, but not.'''

        if member is None:
            member = ctx.author

        query = '''
SELECT Profiles.user_id, Profiles.description, Quotes.quote, Currency.moneys, Birthdays.month, Birthdays.day, Birthdays.year
 FROM Profiles LEFT JOIN Quotes ON
 Profiles.favourite_quote = Quotes.id LEFT JOIN Currency ON
 Currency.user_id = Profiles.user_id LEFT JOIN Birthdays ON
 Birthdays.user_id = Profiles.user_id WHERE Profiles.user_id=$1
'''
        row = await ctx.bot.con.fetchone(query, member.id)

        if row is None:
            await ctx.bot.con.execute('INSERT INTO Profiles (user_id) VALUES ($1)', member.id)
            row = await ctx.bot.con.fetchone(query, member.id)

        profile_embed = discord.Embed(
            title=f"{member.name}'s profile",
            colour=0xffb5f7,
            timestamp=ctx.message.created_at
        )
        profile_embed.add_field(
            name='Name',
            value=member.display_name
        )
        profile_embed.add_field(
            name='Description',
            value=row["description"][:1024]
        )
        profile_embed.add_field(
            name='Balance',
            value=row['moneys'] or 0
        )
        if row['month'] is not None:
            profile_embed.add_field(
                name='Birthday',
                value=f'{row["month"]} {row["day"]} {row["year"]}'
            )
        profile_embed.add_field(
            name='Favourite Quote',
            value=row["quote"][:1024] if row["quote"] else None
        )
        profile_embed.set_thumbnail(
            url=member.avatar_url
        )

        await ctx.send(embed=profile_embed)

    @commands.command(aliases=['setdescription'])
    async def setdesc(self, ctx, *, message: str):
        '''Set the description for your profile
           Example: >>setdesc potato'''

        row = await ctx.bot.con.fetchone('SELECT * FROM Profiles WHERE user_id=$1', ctx.author.id)

        if row is not None:
            await ctx.bot.con.execute('UPDATE Profiles SET description=$1 WHERE user_id=$2', message, ctx.author.id)
        else:
            await ctx.bot.con.execute('INSERT INTO Profiles (user_id, description) VALUES ($1, $2)', ctx.author.id, message)
        await ctx.send('Updated.')

    @commands.command(aliases=['favequote'])
    async def setfavequote(self, ctx, message: int):
        '''Set your all time favourite quote'''

        row = await ctx.bot.con.fetchone('SELECT * FROM Profiles WHERE user_id=$1', ctx.author.id)
        quote = await ctx.bot.con.fetchone('SELECT * FROM Quotes WHERE guild_id=$1 and quote_id=$2', ctx.guild.id, message)

        if quote is None:
            await ctx.send(f'There is no quote with the id `{message}`.')
            return

        if row is None:
            await ctx.bot.con.execute('INSERT INTO Profiles (user_id, favourite_quote) VALUES ($1, $2)', ctx.author.id, quote["id"])
        else:
            await ctx.bot.con.execute('UPDATE Profiles SET favourite_quote=$1 WHERE user_id=$2', quote["id"], ctx.author.id)
        await ctx.send(f'Updated your favourite quote to `{message}`.')

    @commands.command(name='addbirthday')
    async def birthdayadd(self, ctx, month, day: int, year: int = None):
        '''Example: >>birthdayadd April 1 1999
           Shows up on your user info.'''


        if day > 31:
            await ctx.send("Sorry, we don't accept aliens.")
        else:
            pekopeko = await ctx.bot.con.fetchone('SELECT * FROM Birthdays WHERE user_id=$1', ctx.author.id)
            if pekopeko is not None:
                await ctx.bot.con.execute('UPDATE Birthdays SET month=$1, day=$2, year=$3 WHERE user_id=$4', month, day, year, ctx.author.id)
                await ctx.send('Your birthday has been updated.')
            else:
                await ctx.bot.con.execute('INSERT INTO Birthdays (user_id, month, day, year) VALUES ($1, $2, $3, $4)', ctx.author.id, month, day, year)
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

        if checkleave is None or checkleave['leave_message'] == 'FALSE':
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

    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def addquote(self, ctx, *, message: str):
        '''Quote people's embarrasing moments eternally
           Example: >>addquote potato'''

        row = await ctx.bot.con.fetchone('SELECT quote FROM Quotes WHERE guild_id=$1 AND quote=$2', ctx.guild.id, message)

        if row is not None:
            await ctx.send('This quote is already added.')
            return

        whatthefuckwasthelastnumber = await ctx.bot.con.fetchone('SELECT COUNT(*) AS count FROM Quotes WHERE guild_id=$1', ctx.guild.id)

        quotenumber = (whatthefuckwasthelastnumber['count'] + 1)

        await ctx.bot.con.execute('INSERT INTO Quotes (guild_id, quote, quote_id) VALUES ($1, $2, $3)', ctx.guild.id, message, quotenumber)
        await ctx.send(f'Added your quote `{quotenumber}`.')

    @addquote.error
    async def addquote_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('Permissions not detected. You need `manage_messages`')
        else:
            traceback.print_exc()

    @commands.command()
    async def quote(self, ctx, message: int = None):
        '''Find a quote or have one selected for you!
           Example: >>quote 3'''

        if message is not None:
            try:
                row = await ctx.bot.con.fetchone('SELECT quote FROM Quotes WHERE guild_id=$1 and quote_id=$2', ctx.guild.id, message)
                quotemessage = discord.Embed(
                    description=f'{message}. {row["quote"]}',
                    colour=0xffb5f7,
                    timestamp=ctx.message.created_at
                )
                quotemessage.set_footer(
                    text=f'Requested by {ctx.author.display_name}',
                    icon_url=ctx.author.avatar_url
                )
                await ctx.send(embed=quotemessage)
            except OverflowError:
                await ctx.send(f"Holy- hold back on the numbers! It's way too big for me >:C")

            if row is None:
                await ctx.send(f'There is no quote under the id `{message}`')
        else:
            randomrow = await ctx.bot.con.fetchone('SELECT quote, quote_id FROM Quotes WHERE guild_id=$1 ORDER BY random()', ctx.guild.id)
            randomquote = discord.Embed(
                description=f'{randomrow["quote_id"]}. {randomrow["quote"]}',
                colour=0xffb5f7,
                timestamp=ctx.message.created_at
            )
            randomquote.set_footer(
                text=f'Requested by {ctx.author.display_name}',
                icon_url=ctx.author.avatar_url
             )
            await ctx.send(embed=randomquote)

    @commands.has_permissions(manage_messages=True)
    @commands.command(aliases=['quoteremove', 'begonequote'])
    async def removequote(self, ctx, message: int = None):
        '''Erase any embarassing moments from history
           Example: >>removequote 4'''

        row = await ctx.bot.con.fetchone('SELECT quote FROM Quotes WHERE guild_id=$1 and quote_id=$2', ctx.guild.id, message)

        if row is None:
            await ctx.send(f'There is no quote under the id `{message}`.')
        else:
            deleterow = await ctx.bot.con.execute('DELETE FROM Quotes WHERE guild_id=$1 and quote_id=$2', ctx.guild.id, message)
            await ctx.send(f'Deleted quote `{message}`.')



def setup(bot):
    bot.add_cog(Misc(bot))
