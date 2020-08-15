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

    @commands.command()
    async def marry(self, ctx, member: discord.Member, *, message: str = None):
        '''Marry your friends or a partner, may include a message'''

        row = await ctx.bot.con.fetchone('SELECT * FROM Marriage WHERE user_id=$1 and guild_id=$2', ctx.author.id, ctx.guild.id)

        if row is None:
            if message is not None:
                response = discord.Embed(
                    title='A wild proposal appeared!',
                    description=f'''**{member.display_name}**, **{ctx.author.display_name}** wants to marry you with the message `{message}`!
                    Do you accept? **(Y/N)**''',
                    colour=0xffb5f7,
                    timestamp=ctx.message.created_at
                )
                await ctx.send(embed=response)
            else:
                response = discord.Embed(
                    title='A wild proposal appeared!',
                    description=f'''**{member.display_name}**, **{ctx.author.display_name}** wants to marry you!
                    Do you accept? **(Y/N)**''',
                    colour=0xffb5f7,
                    timestamp=ctx.message.created_at
                )
                await ctx.send(embed=response)

            def check(m):
                return member.id == m.author.id and m.channel == ctx.channel

            success = discord.Embed(
                description='🎊 You may now kiss the bride/groom! 🎊',
                colour=0xffb5f7,
                timestamp=ctx.message.created_at
            )

            message = await ctx.bot.wait_for('message', check=check)
            if message.content.lower() in ['yes', 'y']:
                await ctx.bot.con.execute('INSERT INTO Marriage (guild_id, user_id, married_to, married_user_id, date) VALUES ($1, $2, $3, $4, $5)', ctx.guild.id, ctx.author.id, member.name, member.id, message.created_at.strftime('%a %#d %B, %Y'))
                await ctx.bot.con.execute('INSERT INTO Marriage (guild_id, user_id, married_to, married_user_id, date) VALUES ($1, $2, $3, $4, $5)', ctx.guild.id, member.id, ctx.author.name, ctx.author.id, message.created_at.strftime('%a %#d %B, %Y'))
                await ctx.send(embed=success)
            elif message.content.lower() in ['no', 'n']:
                failure = discord.Embed(
                    description=f"Sorry **{ctx.author.display_name}**, looks like they didn't want to marry you ):",
                    colour=0xffb5f7,
                    timestamp=ctx.message.created_at
                )
                await ctx.send(embed=failure)
        else:
            await ctx.send("You're already married! You need to get a divorce before marrying again >:C")

    @commands.command()
    async def divorce(self, ctx, member: discord.Member):
        '''Divorce your partner, because you probably hate them now'''

        row = await ctx.bot.con.fetchone('SELECT * FROM Marriage WHERE user_id=$1 and guild_id=$2', ctx.author.id, ctx.guild.id)

        if row is not None:
            response = discord.Embed(
                description=f'''{ctx.author.display_name}, are you sure you want to divorce {row["married_to"]}?
                **(Y/N)**''',
                colour=0xffb5f7,
                timestamp=ctx.message.created_at
            )
            await ctx.send(embed=response)

            def check(m):
                return ctx.author.id == m.author.id and m.channel == ctx.channel

            message = await ctx.bot.wait_for('message', check=check)
            if message.content.lower() in ['yes', 'y']:
                success = discord.Embed(
                    description=f'You have successfully divorced {row["married_to"]} ):',
                    colour=0xffb5f7,
                    timestamp=ctx.message.created_at
                )
                await ctx.bot.con.execute('DELETE FROM Marriage WHERE user_id=$1 and guild_id=$2', ctx.author.id, ctx.guild.id)
                await ctx.bot.con.execute('DELETE FROM Marriage WHERE user_id=$1 and guild_id=$2', member.id, ctx.guild.id)
                await ctx.send(embed=success)
            else:
                failure = discord.Embed(
                    description='Process cancelled. Divorce papers have been ripped up.',
                    colour=0xffb5f7,
                    timestamp=ctx.message.created_at
                )
                await ctx.send(embed=failure)
        else:
            await ctx.send("Sorry, computer says no. You're either not married or not married to that person.")

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
    async def birthdays(self, ctx):
        '''Display all the birthdays set in your server'''

        members = [str(member.id) for member in ctx.guild.members]
        all_birthdays = await ctx.bot.con.fetchall(f'SELECT * FROM Birthdays WHERE user_id IN ({", ".join(members)})')

        member_info = [f'**{ctx.guild.get_member(member["user_id"]).display_name}** - {member["month"]} {member["day"]}' for member in all_birthdays]
        final = "\n".join(member_info)

        birthday_message = discord.Embed(
            title=f"{ctx.guild.name}'s birthdays",
            description=final,
            colour=0xffb5f7,
            timestamp=ctx.message.created_at
        )
        birthday_message.set_thumbnail(
            url=ctx.guild.icon_url
        )
        birthday_message.set_footer(
            text=f'Requested by {ctx.author.display_name}',
            icon_url=ctx.author.avatar_url
        )

        await ctx.send(embed=birthday_message)

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
        '''Sets the channel where messages are sent whenever someone leaves'''

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
                return
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
