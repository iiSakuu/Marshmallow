import random
import math
from discord.ext import commands
import discord

fortoonresponses = [
    'The fortune you seek is in another cookie',
    'All fortunes are wrong except this one',
    'Never wear your best pants when you go to fight for freedom',
    'Fortune not found? Abort, Retry, Ignore',
    'Some men dream of fortunes, others dream of cookies',
    'Flattery will go far tonight',
    'The road to riches is paved with homework',
    'You will be hungry again in one hour',
    'No snowflake feels responsible in an avalanche',
    'You love Chinese food',
    'I am worth a fortune',
    'You will recieve a fortune cookie',
    'Some fortune cookies contain no fortune',
    'Dont eat the paper',
    'Change is inevitable, except for vending machines',
    'You think its a secret, but they know',
    'Only listen to the fortune cookie; disregard all other fortune telling units.',
    'It is a good day to have a good day',
    'You will die alone and poorly dressed.',
    'Do not mistake temptation for opportunity.',
    'If you look back, you will soon be going that way',
    "Don't behave with cold manners.",
    'He who laughs last is laughing at you',
    'Actions speak louder than fortune cookies',
    'A foolish man listens to his heart. A wise man listens to fortune cookies.',
    'You can always find happiness at work on Friday.',
    'All fortunes are wrong except this one',
    'Count your blessings by thinking of those who love you',
    'Love is the triumph of imagination over intelligence',
    'Love is the only medicine for a broken heart',
    'A secret admirer is now plotting how to win your heart.',
    "There will come a time when you wish you'd wish you'd given love a chance.",
    "Don't let heartbreak slow down your quest to find love",
    'To love, is to forgive',
    'Excitement and intrigue follow you closely wherever you go.',
    'Friendship is the first step towards love',
    'Never lose the ability to find beauty in ordinary things',
    'No one can make you feel inferior without your consent',
    'The dream is within you',
    'Hope is what keeps us alive',
    'Trust those who return your acts of kindness. Respond with kinder gestures',
    'Your many hidden talents will become obvious to those around you',
    'Learn to take responsibility for your actions',
    'Nature, love and patience are the three best physicians',
    'Change can hurt, but it leads to a path to something better',
    "Never give up. You're not a failure if you don't give up",
    'A friend only asks for your time, not your money.',
    'Your first love has never forgotten you.',
    "Pay as you go, if you can't pay then don't go",
    ]

eightballresponses = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes - definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful."
]

class Fun(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command(aliases=['8ball','ball8'])
    async def _8ball(self, ctx, *, question):

        eightball = discord.Embed(
            title='Your Question:',
            description=f'{question}',
            color=0xffb5f7
        )
        eightball.add_field(
            name='The Answer?',
            value=random.choice(eightballresponses)
        )

        await ctx.send('Shaking the 8ball...', embed=eightball)

    @commands.command()
    async def owocounter(self, ctx):
        await ctx.send('Daily OwO is at: ' + str(self.bot.owo_counter))

    @commands.command()
    async def fortunecookie(self, ctx):

        fortune = discord.Embed(
            title='Fortune Cookie',
            description='All truths in the world have been revealed.',
            color=0xffb5f7
        )

        fortune.add_field(
            name='Your fortune is...',
            value=random.choice(fortoonresponses)
        )

        await ctx.send(
            f'{ctx.author.mention} has cracked open a fortune cookie!',
            embed=fortune
        )

    @commands.command(aliases=['F', 'respect'])
    async def f(self, ctx):
        '''Press F to pay respect'''
        self.bot.f_counter += 1

        respects = discord.Embed(
            description="You've successfully pressed F",
            colour=0xffb5f7,
            timestamp=ctx.message.created_at
        )
        respects.set_footer(
            text=f'{self.bot.f_counter} people have paid respect today.'
        )

        await ctx.send(
            embed=respects
        )

    @commands.command(aliases=['uwu', 'owo', 'owoify'])
    async def owoconverter(self, ctx, *, message):
        '''Unleash your inner owo'''

        message_received = message

        first_pass = message_received.replace('r', 'w')
        second_pass = first_pass.replace('l', 'w')

        ending = [
            ' uwu',
            ' owo',
            ' x3',
            ' -////-',
            ' >///<',
            ' >w<',
            ' :3',
            'ᵘʷᵘ',
            ' >:3c'
        ]

        final_translation = (second_pass + random.choice(ending))

        owo_translater = discord.Embed(
            description=f'**Your text:**\n {message} \n **Translated:** \n {final_translation}',
            colour=0xffb5f7,
            timestamp=ctx.message.created_at
        )
        owo_translater.set_author(
            name=ctx.message.author.display_name,
            icon_url=ctx.message.author.avatar_url
        )
        owo_translater.set_footer(
            text='Normal -> OwO'
        )

        await ctx.send(embed=owo_translater)

    @commands.command()
    async def lovetester(self, ctx, person1 : discord.Member, person2: discord.Member):
        if person2 is None:
            person2 = ctx.author

def setup(bot):
    bot.add_cog(Fun(bot))
