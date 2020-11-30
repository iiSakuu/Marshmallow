import math
import random
import discord
import os
from discord.ext import commands


class Actions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def slap(self, ctx, member: discord.Member):
        '''Slap your enemies (or friends) with varying force'''
        slap_strength = random.randint(1, 110)
        intensity = math.ceil(slap_strength / 10)

        f = discord.File(
            f'gifs//slap//{intensity}.gif',
            filename=f'{intensity}.gif'
        )

        slapparoo = discord.Embed(
            description=f'**{ctx.author.display_name}** slaps **{member.display_name}**',
            colour=0xffb5f7,
            timestamp=ctx.message.created_at
        )
        slapparoo.set_footer(
            text=f'Force: {slap_strength}'
        )
        slapparoo.set_image(
            url=f'attachment://{intensity}.gif'
        )

        if member.id == ctx.author.id:
            await ctx.send("Sorry, you can't slap yourself.")

        elif member.id == 331890706866110465:
            await ctx.send(
                '**W-why would you slap me? ):**',
                file=f,
                embed=slapparoo
            )

        elif member.id == 712041909496971266:
            await ctx.send(
                'Access denied.'
            )

        else:
            await ctx.send(
                file=f,
                embed=slapparoo
            )

    @commands.command()
    async def hug(self, ctx, member: discord.Member):
        '''Give someone you like a nice hug'''
        result_hug = random.choice(os.listdir('.//gifs//hug'))

        hugfile = discord.File(
            f'gifs//hug//{result_hug}',
            filename=f'{result_hug}'
        )

        givehug = discord.Embed(
            description=f'**{ctx.author.display_name}** hugs **{member.display_name}**',
            colour=0xffb5f7,
            timestamp=ctx.message.created_at
        )
        givehug.set_image(
            url=f'attachment://{result_hug}'
        )

        await ctx.send(
            file=hugfile,
            embed=givehug
        )

    @commands.command()
    async def kiss(self, ctx, member: discord.Member):
        '''A virtual kiss for your friends and loved ones'''
        result_kiss = random.choice(os.listdir('.//gifs//kiss'))

        kissfile = discord.File(
            f'gifs//kiss//{result_kiss}',
            filename=f'{result_kiss}'
        )
        givekiss = discord.Embed(
            description=f'**{ctx.author.display_name}** kisses **{member.display_name}**',
            colour=0xffb5f7,
            timestamp=ctx.message.created_at
        )
        givekiss.set_image(
            url=f'attachment://{result_kiss}'
        )

        await ctx.send(
            file=kissfile,
            embed=givekiss
        )

    @commands.command()
    async def boop(self, ctx, member: discord.Member):
        '''For when you feel the need to boop someone'''
        result_boop = random.choice(os.listdir('.//gifs//boop'))

        boopfile = discord.File(
            f'gifs//boop//{result_boop}',
            filename=f'{result_boop}'
        )

        giveboop = discord.Embed(
            description=f'**{ctx.author.display_name}** boops **{member.display_name}** right on the snoot!',
            colour=0xffb5f7,
            timestamp=ctx.message.created_at
        )
        giveboop.set_image(
            url=f'attachment://{result_boop}'
        )

        await ctx.send(
            file=boopfile,
            embed=giveboop
        )

    @commands.command()
    async def poke(self, ctx, member: discord.Member):
        '''Poke your worst enemy or closest friend'''
        result_poke = random.choice(os.listdir('.//gifs//poke'))

        pokefile = discord.File(
            f'gifs//poke//{result_poke}',
            filename=f'{result_poke}'
        )
        givepoke = discord.Embed(
            description=f'**{ctx.author.display_name}** pokes **{member.display_name}**',
            colour=0xffb5f7,
            timestamp=ctx.message.created_at
        )
        givepoke.set_image(
            url=f'attachment://{result_poke}'
        )

        await ctx.send(
            file=pokefile,
            embed=givepoke
        )

    @commands.command(aliases=['shook'])
    async def shock(self, ctx):
        '''Display your utmost shock in the best way'''
        result_shock = random.choice(os.listdir('.//gifs//shook'))

        shockfile = discord.File(
            f'gifs//shook//{result_shock}',
            filename=f'{result_shock}'
        )
        shooketh = discord.Embed(
            colour=0xffb5f7,
            timestamp=ctx.message.created_at
        )
        shooketh.set_image(
            url=f'attachment://{result_shock}'
        )

        await ctx.send(
            file=shockfile,
            embed=shooketh
        )


def setup(bot):
    bot.add_cog(Actions(bot))
