import traceback
from discord.ext import commands
import discord


class Administration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_messages=True)
    @commands.command(aliases=['purge'])
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('Permissions not detected.')
        else:
            traceback.print_exc()

    @commands.has_permissions(kick_members=True)
    @commands.command(aliases=['kickaroo', 'boot'])
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f'Kicked {member.mention}')

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('Permissions not detected.')
        else:
            traceback.print_exc()

    @commands.has_permissions(ban_members=True)
    @commands.command(aliases=['banaroo', 'banishtotheshadowrealm'])
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'Banned {member.mention}')

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('Permissions not detected.')
        else:
            traceback.print_exc()

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return

    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        a_pillow = discord.utils.get(ctx.guild.roles, name='pillow')
        if a_pillow is None:
            a_pillow = await ctx.guild.create_role(
                name='pillow',
                colour=discord.Colour(0xffb5f7)
            )
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(
                    a_pillow,
                    send_messages=False,
                    attach_files=False,
                    add_reactions=False
                )
            for channel in ctx.guild.voice_channels:
                await channel.set_permissions(
                    a_pillow,
                    speak=False,
                    stream=False
                )
        await member.add_roles(a_pillow, reason=reason)
        await ctx.message.add_reaction(emoji='👌')

    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        unpillow = discord.utils.get(member.roles, name='pillow')
        if unpillow is not None:
            await member.remove_roles(unpillow, reason=reason)
            await ctx.message.add_reaction(emoji='👌')

def setup(bot):
    bot.add_cog(Administration(bot))
