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

sleeping = False
priceRises = True
food_cost = 10

db = TinyDB('data.json')
bot = commands.Bot(command_prefix=config['prefix'])

query = Query()

# @bot.event
# async def on_message(ctx):
    # if ctx.author != bot.user:
        # if ctx.channel.name == "моя-свинюшня":
            # await ctx.reply(ctx.content)
@bot.command()
async def создатьхряка(ctx: commands.Context, name):
    if not db.search(query.owner == str(ctx.author.id)):
        weight = randrange(5) + 5
        db.insert({'name': name, 'satiety': 0.1, 'max-satiety': math.sqrt(weight) / 2, 'weight': weight, 'money': 0, 'factory': 0, 'food': 100, 'owner': str(ctx.author.id)})
        await ctx.reply("Теперь вы обладатель поросёнка. Его зовут " + name + ". Он весит всего " + str(weight) + " кг. Он голоден, покормите его")
    else: 
        await ctx.reply("У вас уже есть хряк")
@bot.command()
async def покормить(ctx: commands.Context, food):
    if not sleeping:
        if db.search(query.owner == str(ctx.author.id)):
            await feed(int(food), str(ctx.author.id), ctx)
        else: 
            await ctx.reply('У вас нет хряка')
    else:
        await ctx.reply('Хряки спят. Возвращайтесь позже!')
@bot.command()
async def хряк(ctx: commands.Context):
    if not sleeping:
        pig = getPigWithId(ctx.author.id)
        satiety = pig['satiety']
        max_satiety = pig['max-satiety']
        status = ''
        if satiety >= max_satiety:
            status = 'Хряк объелся и спит.'
        elif rangePercent(satiety, max_satiety, 90, 100):
            status = 'Хряк бодрствует'
        elif rangePercent(satiety, max_satiety, 80, 90):
            status = 'Хряк лежит'
        elif rangePercent(satiety, max_satiety, 70, 80):
            status = 'Хряк непротив покушать'
        elif rangePercent(satiety, max_satiety, 50, 70):
            status = 'Хряк привлекает внимание'
        elif rangePercent(satiety, max_satiety, 30, 50):
            status = 'Хряк просит кушать'
        elif rangePercent(satiety, max-_atiety, 10, 30):
            status = 'Хряк голоден!'
        elif rangePercent(satiety, max_satiety, 5, 10):
            status = 'Хряк истощён.'
        else:
            status = 'Что с ним?'
        await ctx.reply(f"Имя: {pig['name']} \nВес: {math.ceil(pig['weight'])} кг\nКорм: {pig['food']}\nБаланс: {math.ceil(pig['money'])} UAH\n{status}")
    else:
        await ctx.reply('Все хряки спят. И вам рекомендую')
@bot.command()
async def топ(ctx: commands.Context):
    top = ""
    sortedPigs = sorted(db.all(), key=lambda d: d['weight'], reverse=True) 
    for pig in sortedPigs: 
        top = top + f"{pig['name']}, {math.ceil(pig['weight'])} кг\n"
    await ctx.reply(top)
@bot.command()
async def пойтиназавод(ctx: commands.Context):

    pig = getPigWithId(ctx.author.id)
    if pig['factory'] <= 0:
        revenue = 10 + randrange(10)
        db.update({'factory': 3600 * 6}, query.owner == str(ctx.author.id))
        db.update({'money': pig['money'] + revenue})
        await ctx.reply(f'Вы пошли на завод. Следующая смена через 6 часов. +{revenue} UAH')
    else:
        await ctx.reply(f'Вы уже были на заводе, вам нужен отдых')
@bot.command()
async def купитькорм(ctx: commands.Context):
    pig = getPigWithId(ctx.author.id)
    global food_cost
    if pig['money'] >= food_cost:
        db.update({'food': pig['food'] + 25}, query.owner == pig['owner'])
        db.update({'money': pig['money'] - food_cost}, query.owner == pig['owner'])
        await ctx.reply(f"Количество корма теперь {pig['food'] + 25}")
    else:
        await ctx.reply(f'Недостатньо коштiв')

@bot.command()
async def ценакорма(ctx: commands.Context):
    await ctx.reply(f"Корм стоит {round(food_cost, 2)} UAH за упаковку")
    
@bot.command()
async def дрочписюн(ctx: commands.Context):
    await ctx.send(text)
    if sleeping:
        await ctx.reply("☎☎☏ мммм дааоаоао ☏☏☎")
@bot.command()
async def помощь(ctx: commands.Context):
    text = "\n>>> Команды:"
    text = text + " `создатьхряка *имя*`\n"
    text = text + " `покормить *кол-во корма*`\n"
    text = text + " `хряк`\n"
    text = text + " `топ`\n"
    text = text + " `пойтиназавод`\n"
    text = text + " `ценакорма`\n"
    text = text + " `купитькорм`\n"
    text = text + " префикс: *!*\n"

@tasks.loop(seconds=1)
async def change_status():
    global food_cost
    global priceRises
    if priceRises:
        rand = (randrange(100) / 10000 - 0.004)
    else:
        rand = (randrange(100) / 10000 - 0.006)
    if food_cost < 8:
        priceRises = True
    elif food_cost > 15:
        priceRises = False

    if rand > 0 and food_cost < 15:
        food_cost += rand
    if rand < 0 and food_cost > 8:
        food_cost += rand


    if not sleeping:
        if db.search(query.owner != ""):
            for val in db.all():
                db.update({'satiety': val['satiety'] * 0.9995}, query.owner == val['owner'])
                db.update({'factory': val['factory'] - 1}, query.owner == val['owner'])
                if val['satiety'] < 0.01:
                    db.update({'weight': val['weight'] * 0.9999}, query.owner == val['owner'])
change_status.start()

    # channel = bot.get_channel = xxx
    # await bot.change_presence(activity=discord.Game('online'))
    # print('test')
    # await bot.channel.send('here')

@bot.command()
async def context(ctx: commands.Context, pigName):
    await ctx.reply(db.search(query.name == pigName))
async def feed(food, owner, ctx): 
    pig = getPigWithId(owner)
    satiety = pig['satiety']
    max_satiety = pig['max-satiety']
    weight = pig['weight']
    
    if food > (max_satiety * 2):
        await ctx.reply('Хряк не может съесть так много')
        return

    if satiety <= max_satiety * 0.8:
        diff = max_satiety - satiety
        if food > diff:
            revenue = diff
        db.update({'satiety': satiety + food}, query.owner == owner)
        db.update({'max-satiety': math.sqrt(weight) / 2}, query.owner == owner)
        db.update({'weight': pig['weight'] + (diff + 1) * (randrange(100) / 50)}, query.owner == owner)
        db.update({'food': pig['food'] - food}, query.owner == owner)
        pig = getPigWithId(owner)
        if pig['satiety'] >= pig['max-satiety']:
            await ctx.reply(f'Ваш хряк наелся. Корм: {pig["food"]}. Теперь он весит {math.ceil(pig["weight"])} кг!')
        else: 
            await ctx.reply('Хряк просит больше')        
    else:
        await ctx.reply('Хряк отказался')
def getPigWithId(id):
    return db.search(query.owner == str(id))[0]
def findAttributeInObjectsArray(attr, array, target):
    for obj in array:
        if obj["attr"] == target:
            return obj
def percent(num, perc):
    return num * (perc / 100)
def rangePercent(num, max, perc1, perc2):
    return num > max * (perc1 / 100) and num < max * (perc2 / 100)


# while True:
#     if db.search(query.owner > 0):
#         for val in db.all():
#             db.update({'satiety': val['satiety'] * 0.999}, query.owner == val['owner'])
#     time.sleep(1)

bot.run(config['token'])
