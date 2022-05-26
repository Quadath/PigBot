import math
from random import randrange
import discord,asyncio,os
from discord.ext import tasks
import time
import json
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
    if not db.search(query.owner == str(ctx.author.id)):
        weight = randrange(5) + 5
        db.insert({'name': name, 'satiety': 0.1, 'max-satiety': math.sqrt(weight) / 2, 'weight': weight, 'food': '200', 'owner': str(ctx.author.id)})
        await ctx.reply("Теперь вы обладатель поросёнка. Его зовут " + name + ". Он весит всего " + str(weight) + " кг. Он голоден, покормите его")
    else: 
        await ctx.reply("У вас уже есть хряк")
@bot.command()
async def покормить(ctx: commands.Context, food):
    await feed(int(food), str(ctx.author.id), ctx)
@bot.command()
async def хряк(ctx: commands.Context):
    pig = getPigWithId(ctx.author.id)
    satiety = pig['satiety']
    max_satiety = pig['max-satiety']
    status = ''
    if satiety >= max_satiety:
        status = 'Хряк объелся и спит.'
    elif satiety < max_satiety and satiety > (max_satiety * 0.75):
        status = 'Хряк непротив покушать'
    else:
        status = 'Хряк голоден!'
    await ctx.reply(f"Имя: {pig['name']} \nВес: {pig['weight']} кг\n {status}")

@tasks.loop(seconds=1)
async def change_status():
    if db.search(query.owner != ""):
        for val in db.all():
            db.update({'satiety': val['satiety'] * 0.999}, query.owner == val['owner'])
change_status.start()

    # channel = bot.get_channel = xxx
    # await bot.change_presence(activity=discord.Game('online'))
    # print('test')
    # await bot.channel.send('here')

@bot.command()
async def context(ctx: commands.Context):
    print(ctx.message)
    await ctx.reply("Author is " + str(ctx.author) + " id: " + str(ctx.author.id))

async def feed(food, owner, ctx): 
    pig = getPigWithId(owner)
    satiety = pig['satiety']
    max_satiety = pig['max-satiety']
    weight = pig['weight']
    
    if food > (max_satiety * 2):
        await ctx.reply('Хряк не может съесть так много')
        return

    if satiety <= max_satiety * 0.75:
        db.update({'satiety': satiety + food}, query.owner == owner)
        db.update({'max-satiety': math.sqrt(weight) / 2}, query.owner == owner)
        db.update({'weight': pig['weight'] + math.sqrt(food) * (randrange(100) / 50)}, query.owner == owner)
        pig = getPigWithId(owner)
        if pig['satiety'] >= pig['max-satiety']:
            await ctx.reply(f'Ваш хряк наелся. Теперь он весит {math.ceil(pig["weight"])} кг!')
        else: 
            await ctx.reply('Хряк просит больше')        
    else:
        await ctx.reply('Хряк отказался')
def getPigWithId(id):
    return db.search(query.owner == str(id))[0]

# while True:
#     if db.search(query.owner > 0):
#         for val in db.all():
#             db.update({'satiety': val['satiety'] * 0.999}, query.owner == val['owner'])
#     time.sleep(1)

bot.run(config['token'])