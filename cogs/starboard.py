import asqlite
import discord
from discord.ext import commands

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def setstarboard(self, ctx, channel: discord.TextChannel):
        '''Set the channel for your starboard
           Example: >>setstarboard #starboard'''

        starboardchannel = await ctx.bot.con.fetchone('SELECT * FROM Guild_Settings where guild_id=$1', ctx.guild.id)

        if starboardchannel is None:
            await ctx.bot.con.execute('INSERT INTO Guild_Settings (guild_id, starboard_channel_id) VALUES ($1, $2)', ctx.guild.id, channel.id)
            await ctx.send('Starboard registered.')
        else:
            await ctx.bot.con.execute('UPDATE Guild_Settings SET starboard_channel_id=$1 WHERE guild_id=$2', channel.id, ctx.guild.id)
            await ctx.send('Updated')

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def setstars(self, ctx, stars: int):
        '''Set the minimum amount of stars required for your starboard
           Example: >>setstars 4'''

        starcheck = await ctx.bot.con.fetchone('SELECT * FROM Guild_Settings where guild_id=$1', ctx.guild.id)

        if starcheck is None:
            await ctx.send('You need to set your channel before you can do this.')
        else:
            await ctx.bot.con.execute('UPDATE Guild_Settings SET minimum_stars=$1 WHERE guild_id=$2', stars, ctx.guild.id)
            await ctx.send('Updated your star count.')

    @commands.command()
    async def starcount(self, ctx):
        '''Check the amount of stars required for a repost to happen'''

        checkstarcount = await ctx.bot.con.fetchone('SELECT * FROM Guild_Settings where guild_id=$1', ctx.guild.id)

        if checkstarcount is None:
            await ctx.send('You need to set your channel before you can check your minimmum stars.')
        else:
            await ctx.send(f'Your server requires a minimum of `{checkstarcount["minimum_stars"]}` stars.')

    @commands.Cog.listener(name='on_raw_reaction_add')
    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def on_raw_reactions(self, payload):

        if str(payload.emoji) != '⭐':
            return

        steal_guild_info = self.bot.get_guild(payload.guild_id)
        steal_channel_info = steal_guild_info.get_channel(payload.channel_id)
        eat_message_info = await steal_channel_info.fetch_message(payload.message_id)
        reaction = discord.utils.find(lambda r: str(r.emoji) == '⭐', eat_message_info.reactions)

        check_requirements = await self.bot.con.fetchone('SELECT * FROM Guild_Settings WHERE guild_id=$1', steal_guild_info.id)

        if check_requirements is None or check_requirements['starboard_channel_id'] is None:
            return

        comparison = await self.bot.con.fetchone('SELECT message_id FROM Starboard WHERE starred_message_id=$1', eat_message_info.id)
        starboard_channel_id = check_requirements['starboard_channel_id']
        starboard_channel = steal_guild_info.get_channel(starboard_channel_id)

        if reaction.count < check_requirements['minimum_stars']:
            if comparison is not None:
                finish_comparison = await starboard_channel.fetch_message(comparison['message_id'])
                await finish_comparison.delete()
                await self.bot.con.execute('DELETE FROM Starboard WHERE message_id=$1', comparison['message_id'])
        elif comparison is not None:
            finish_comparison = await starboard_channel.fetch_message(comparison['message_id'])
            await finish_comparison.edit(embed=self.starboard_embed(eat_message_info, reaction), content=f'{reaction.count} ⭐')
        else:
            sent_message = await starboard_channel.send(
                f'{reaction.count} ⭐',
                embed=self.starboard_embed(eat_message_info, reaction)
            )
            await self.bot.con.execute('INSERT INTO Starboard (message_id, starred_message_id) VALUES ($1, $2)', sent_message.id, eat_message_info.id)

    def starboard_embed(self, starred_message_info, reaction):
        star_embed = discord.Embed(
            description=starred_message_info.content,
            colour=0xffd6f1,
            timestamp=starred_message_info.created_at
        )
        star_embed.set_author(
            name=starred_message_info.author.display_name,
            icon_url=starred_message_info.author.avatar_url
        )
        if starred_message_info.attachments:
            star_embed.set_image(
                url=starred_message_info.attachments[0].url
            )
        star_embed.set_footer(
            text=starred_message_info.channel.name
        )
        return star_embed


def setup(bot):
    bot.add_cog(Starboard(bot))
