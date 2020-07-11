from discord.ext import commands
import discord
import random
import math


class Maths(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def add(self, ctx, left: float, right: float):
        await ctx.send(left + right)

    @commands.command()
    async def subtract(self, ctx, left: float, right: float):
        await ctx.send(left - right)

    @commands.command()
    async def multiply(self, ctx, left: float, right: float):
        await ctx.send(left * right)

    @commands.command()
    async def divide(self, ctx, left: float, right: float):
        await ctx.send(left / right)

    @commands.command()
    async def square(self, ctx, number):
        squared_value = float(number) * float(number)
        await ctx.send(f'{number} squared is {squared_value}')

    @commands.command()
    async def squareroot(self, ctx, number: float):
        square_root = math.sqrt(number)
        await ctx.send(f'The square root of {number} is {square_root}')


def setup(bot):
    bot.add_cog(Maths(bot))
