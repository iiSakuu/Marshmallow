import discord
from discord.ext import commands
import asqlite
import traceback

class Profiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        '''Show all your fancy info. Like userinfo, but not.'''

        if member is None:
            member = ctx.author

        query = '''
    SELECT Profiles.user_id, Profiles.description, Profiles.image_url, Profiles.colour, Profiles.fave_show, Profiles.links,
    Quotes.quote, Currency.moneys, Birthdays.month, Birthdays.day,
    Birthdays.year, Marriage.married_to, Marriage.married_user_id, Marriage.date
    FROM Profiles LEFT JOIN Quotes ON
    Profiles.favourite_quote = Quotes.id LEFT JOIN Currency ON
    Currency.user_id = Profiles.user_id LEFT JOIN Birthdays ON
    Birthdays.user_id = Profiles.user_id LEFT JOIN Marriage ON
    Marriage.user_id = Profiles.user_id WHERE Profiles.user_id=$1
    '''
        row = await ctx.bot.con.fetchone(query, member.id)

        if row is None:
            await ctx.bot.con.execute('INSERT INTO Profiles (user_id) VALUES ($1)', member.id)
            row = await ctx.bot.con.fetchone(query, member.id)

        profile_embed = discord.Embed(
            title=f"{member.name}'s profile",
            colour=row['colour'] if row['colour'] else 0xffb5f7,
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
        marriage = await ctx.bot.con.fetchone('SELECT * FROM Marriage WHERE user_id=$1 and guild_id=$2', ctx.author.id, ctx.guild.id)
        profile_embed.add_field(
            name='Married to',
            value=f'**{marriage["Married_to"]}** since {marriage["date"]}' if marriage["guild_id"] else 'Nobody. So alone ):'
        )
        profile_embed.add_field(
            name='Balance',
            value=row['moneys'] or 0
        )
        if row['year'] is not None:
            profile_embed.add_field(
                name='Birthday',
                value=f'{row["month"]} {row["day"]} {row["year"]}'
            )
        else:
            profile_embed.add_field(
                name='Birthday',
                value=f'{row["month"]} {row["day"]}'
            )
        profile_embed.add_field(
            name='Favourite Quote',
            value=row["quote"][:1024] if row["quote"] else None
        )
        profile_embed.add_field(
            name='Favourite Anime/Show',
            value=row['fave_show']
        )
        if row['image_url'] is not None:
            profile_embed.set_image(
                url=row['image_url']
            )
        profile_embed.set_thumbnail(
            url=member.avatar_url
        )
        if row['links'] is not None:
            profile_embed.set_footer(
                text=row['links']
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

    @commands.command(aliases=['setgif', 'profileimage', 'setprofileimage'])
    async def setimage(self, ctx, message: str):
        '''Set the image to be displayed on your profile
           Accepts links'''

        row = await ctx.bot.con.fetchone('SELECT image_url FROM Profiles WHERE user_id=$1', ctx.author.id)

        if row is None:
            await ctx.bot.con.execute('INSERT INTO Profiles (image_url, user_id) VALUES ($1, $2)', message, ctx.author.id)
        else:
            await ctx.bot.con.execute('UPDATE Profiles SET image_url=$1 WHERE user_id=$2', message, ctx.author.id)
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

    @commands.command(name='addbirthday',
        aliases=['birthdayadd', 'birthday', 'setbirthday'])
    async def birthdayadd(self, ctx, month, day: int, year: int = None):
        '''Example: >>birthdayadd April 1 1999
           Shows up on your profile, year isn't required.'''

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

    @commands.command(aliases=['setcolor', 'profilecolour', 'profilecolor'])
    async def setcolour(self, ctx, colour: discord.Colour):
        '''Takes hex codes'''

        row = await ctx.bot.con.fetchone('SELECT * FROM Profiles WHERE user_id=$1', ctx.author.id)

        if row is None:
            embed = discord.Embed(
                description='''Are you sure this is the colour you want to use?
                **(Y/N)**''',
                colour=colour,
                timestamp=ctx.message.created_at
            )

            await ctx.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            message = await ctx.bot.wait_for('message', check=check)
            if message.content.lower() in ['yes', 'y']:
                await ctx.bot.con.execute('INSERT INTO Profiles (user_id, colour) VALUES ($1, $2)', ctx.author.id, colour.value)
                success = discord.Embed(
                    description='Updated!',
                    colour=colour
                )
                await ctx.send(embed=success)
            elif message.content.lower() in ['no', 'n']:
                failure = discord.Embed(
                    description='Proccess aborted.',
                    colour=0xffb5f7
                )
        else:
            embed = discord.Embed(
                description='''Are you sure this is the colour you want to use?
                **(Y/N)**''',
                colour=colour,
                timestamp=ctx.message.created_at
            )
            await ctx.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            message = await ctx.bot.wait_for('message', check=check)
            if message.content.lower() in ['yes', 'y']:
                await ctx.bot.con.execute('UPDATE Profiles SET colour=$1 WHERE user_id=$2', colour.value, ctx.author.id)
                success = discord.Embed(
                    description='Updated!',
                    colour=colour
                )
                await ctx.send(embed=success)
            elif message.content.lower() in ['no', 'n']:
                failure = discord.Embed(
                    description='Proccess aborted.',
                    colour=0xffb5f7
                )
                await ctx.send(embed=failure)

    @setcolour.error
    async def setcolour_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('''You need to choose a hex colour! I recommend using
https://htmlcolorcodes.com/color-picker/.''')
        else:
            traceback.print_exc()

    @commands.command(aliases=['setanimu', 'setshow', 'setaminoo', 'setanimoo'])
    async def setanime(self, ctx, *, anime: str):
        '''Set your favourite anime or show
           Example: >>setanime Kakegurui'''

        row = await ctx.bot.con.fetchone('SELECT * FROM Profiles WHERE user_id=$1', ctx.author.id)

        if row is None:
            await ctx.bot.con.execute('INSERT INTO Profiles (user_id, fave_show) VALUES ($1, $2)', ctx.author.id, anime)
        else:
            await ctx.bot.con.execute('UPDATE Profiles SET fave_show=$1 WHERE user_id=$2', anime, ctx.author.id)

        await ctx.send('Updated.')

    @commands.command(aliases=['setsocialmedia', 'setlink'])
    async def setlinks(self, ctx, *, message: str):
        '''Puts link(s) on the footer of your profile.
        Example: >>setlink https://github.com/iiSakuu/Marshmallow'''

        row = await ctx.bot.con.fetchone('SELECT * FROM Profiles WHERE user_id=$1', ctx.author.id)

        if row is None:
            await ctx.bot.con.execute('INSERT INTO Profiles (user_id, links) VALUES ($1, $2)', ctx.author.id, message)
        else:
            await ctx.bot.con.execute('UPDATE Profiles SET links=$1 WHERE user_id=$2', message, ctx.author.id)

        await ctx.send('Updated.')


def setup(bot):
    bot.add_cog(Profiles(bot))
