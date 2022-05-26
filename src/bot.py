import discord
import json
from random import randrange
from tinydb import TinyDB, Query
from discord.ext import commands


config = {
    'token': 'ODc4ODczODgwNTA3MzUxMTQw.Gj0-hT.oTDxCNSeoKVkUHifQGNJ3l1weua0gsj0Vh5gCI',
    'prefix': '!',
}

db = TinyDB('data.json')
bot = commands.Bot(command_prefix=config['prefix'])

query = Query()

# @bot.event
# async def on_message(ctx):
    # if ctx.author != bot.user:
        # if ctx.channel.name == "моя-свинюшня":
            # await ctx.reply(ctx.content)
@bot.command()
async def создать_хохла(ctx: commands.Context, name):
    if not getPigWithId(ctx.author.id)
        weight = randrange(5) + 2
        db.insert({'name': name, 'weight': weight, 'owner': str(ctx.author.id)})
        await ctx.reply("Теперь вы обладатель поросёнка. Его зовут " + name + ". Он весит всего " + str(weight) + " кг.")
    else: 
        await ctx.reply("У вас уже есть хряк")
@bot.command()
async def покормить(ctx: commands.Context, food):
    pig = getPigWithId(ctx.author.id)
    feed(pig["weight"], str(ctx.author.id))
    pig = getPigWithId(ctx.author.id)
    await ctx.reply("Теперь ваш хряк весит " + str(pig["weight"]) + " кг")

@bot.command()
async def context(ctx: commands.Context):
    print(ctx.message)
    await ctx.reply("Author is " + str(ctx.author) + " id: " + str(ctx.author.id))

def feed(weight, owner): 
    pig = getPigWithId(owner)
    db.update({"weight": pig["weight"] + randrange(10)}, query.owner == owner)
def getPigWithId(id):
    return db.search(query.owner == str(id))[0]

bot.run(config['token'])