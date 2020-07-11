import asyncio
import discord
from discord import Game
from discord.ext.commands import Bot
from discord.ext import commands
import random
import logging
import os
import asqlite
import config

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

BOT_PREFIX = ('>>')

bot = Bot(
    command_prefix=BOT_PREFIX,
    activity=discord.Game(name='Use >>help for a list of commands')
)

bot.owo_counter = 0
bot.f_counter = 0


async def start():
    bot.con = await asqlite.connect("database.sql")
    await bot.start(config.TOKEN)


@bot.event
async def on_message(message):
    if "owo" in message.content:
        bot.owo_counter += 1
    await bot.process_commands(message)

# for Juli server


@bot.event
async def on_member_remove(member: discord.Member):
    if member.guild.id == 236959873676476417:
        channel = bot.get_channel(555428796874883072)
        leave = discord.Embed(
            title='A user has left the server!',
            colour=0xffb5f7
        )
        leave.add_field(name='\u200b', value=f'{member.name}')
        leave.set_thumbnail(url=member.avatar_url)
        leave.set_footer(text=f'ID: {member.id}')
        await channel.send(embed=leave)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('---=-=---')


async def list_guilds():
    await bot.wait_until_ready()
    while not bot.is_closed():
        print("Current servers:")
        for guild in bot.guilds:
            print(guild.name)
        await asyncio.sleep(4000)

for cog in os.listdir('.//cogs'):
    if cog.endswith('.py') and not cog.startswith('_'):
        try:
            cog = f"cogs.{cog.replace('.py', '')}"
            bot.load_extension(cog)
        except Exception as e:
            print(f'{cog} can not be loaded:')
            raise e

bot.loop.create_task(list_guilds())
bot.loop.run_until_complete(start())
