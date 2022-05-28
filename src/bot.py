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
        db.insert({'name': name, 'satiety': 0.1, 'max-satiety': math.sqrt(weight) / 2, 'weight': weight, 'money': 0, 'factory': 0, 'salary': 10,'food': 10, 'owner': str(ctx.author.id)})
        await ctx.reply("Теперь вы обладатель поросёнка. Его зовут " + name + ". Он весит всего " + str(weight) + " кг. Он голоден, покормите его")
    else: 
        await ctx.reply("У вас уже есть хряк")
@создатьхряка.error
async def missing_name(ctx, error):
   if isinstance(error, commands.MissingRequiredArgument):
       await ctx.reply("Вы не ввели имя хряка")
@bot.command()
async def кормить(ctx: commands.Context, food):
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
        elif rangePercent(satiety, max_satiety, 10, 30):
            status = 'Хряк голоден!'
        elif rangePercent(satiety, max_satiety, 5, 10):
            status = 'Хряк истощён.'
        else:
            status = 'Что с ним?'
        money = f"{round(pig['money'])} грн {round(pig['money'] % 1 * 100)} коп."
        await ctx.reply(f"Имя: {pig['name']} \nВес: {math.ceil(pig['weight'])} кг\nКорм: {pig['food']}\nБаланс: {money}\n{status}")
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
async def завод(ctx: commands.Context):
    pig = getPigWithId(ctx.author.id)
    if pig['factory'] <= 0:
        revenue = pig['salary'] + randrange(10)
        coins = revenue % 1 * 100


        db.update({'factory': 3600 * 6}, query.owner == str(ctx.author.id))
        db.update({'money': pig['money'] + revenue}, query.owner == str(ctx.author.id))
        db.update({'salary': pig['salary'] + randrange(10)}, query.owner == str(ctx.author.id))
        await ctx.reply(f'Вы пошли на завод. Следующая смена через 6 часов. +{round(revenue)} грн {round(coins)} коп.')
    else:
        await ctx.reply(f"Вы уже были на заводе, вам нужен отдых, возвращайтесь через {round(pig['factory'] / 3600)} ч.")
@bot.command()
async def купитькорм(ctx: commands.Context, count):
    if int(count) >= 1:
        global food_cost
        total_cost = food_cost * int(count)
        pig = getPigWithId(ctx.author.id)

        if pig['money'] >= total_cost:
            food_cost += total_cost / 9.8
            db.update({'food': pig['food'] + 25}, query.owner == pig['owner'])
            db.update({'money': pig['money'] - total_cost}, query.owner == pig['owner'])
            await ctx.reply(f"Количество корма теперь {pig['food'] + 25 * count}")
        else:
            await ctx.reply(f'Недостатньо коштiв')
@bot.command()
async def ценакорма(ctx: commands.Context):
    await ctx.reply(f"{round(food_cost)} грн {round(food_cost % 1 * 100)} коп. за упаковку")
@bot.command()
async def гуси(ctx: commands.Context, pigName):
    enemyPig = db.search(query.name == pigName)[0]
    pig = getPigWithId(ctx.author.id)
    rand = randrange(10)
    if enemyPig:
        if pig['money'] >= 20:
            if enemyPig['food'] >= rand:
                db.update({'money': pig['money'] - rand * 2}, query.owner == pig['owner'])
                db.update({'food': enemyPig['food'] - rand}, query.owner == enemyPig['owner'])
                await ctx.reply(f"Вы натравили гусей на {enemyPig['name']}, и гуси съели {rand} корма")
            elif enemyPig['food'] > 0:
                db.update({'money': pig['money'] - rand * 2}, query.owner == pig['owner'])
                db.update({'food': 0}, query.owner == enemyPig['owner'])
                await ctx.reply('Гуси съели весь корм!')
            else:
                await ctx.reply('Гуси уже всё съели')
        else:
            await ctx.reply(f'Недостатньо коштiв')
    else:
        await ctx.reply(f'Такого хряка не существует')
@bot.command()
async def дрочписюн(ctx: commands.Context):
    if sleeping:
        await ctx.reply(f"☎☎☏ мммм дааоаоао ☏☏☎ \n Хряк похудел на {randrange(25)}кг")
    else:
        await ctx.reply("Не время для этого")
@bot.command()
async def помощь(ctx: commands.Context):
    text = "\n>>> Команды:\n"
    text = text + " `создатьхряка *имя*`\n"
    text = text + " `покормить *кол-во корма*`\n"
    text = text + " `хряк`\n"
    text = text + " `топ`\n"
    text = text + " `завод`\n"
    text = text + " `ценакорма` (показывает цену)\n"
    text = text + " `купитькорм *кол-во* (купить x пачек)`\n"
    text = text + " `гуси *противник*`\n"
    text = text + " префикс: *!*\n"
    await ctx.reply(text)

@tasks.loop(seconds=1)
async def change_status():
    global food_cost
    global priceRises
    if priceRises:
        rand = (randrange(100) / 10000 - 0.004)
    else:
        rand = (randrange(100) / 10000 - 0.006)
    if food_cost < 8 or randrange(1000) == 2:
        priceRises = True
    elif food_cost > 15 or randrange(1000) == 1:
        priceRises = False
        
    if rand > 0 and food_cost < 100:
        food_cost += rand
    if rand < 0 and food_cost > 7.7:
        food_cost += rand


    if not sleeping:
        if db.search(query.owner != ""):
            for val in db.all():
                db.update({'satiety': val['satiety'] * 0.9995}, query.owner == val['owner'])
                db.update({'factory': val['factory'] - 1}, query.owner == val['owner'])
                if val['satiety'] < 0.001:
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
    
    if food > pig['food']:
        await ctx.reply('У вас нет столько корма')
        return
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
