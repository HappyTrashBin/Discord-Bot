import datetime
import random
import numpy as np

import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Bot

bot = Bot(command_prefix='!', intents=discord.Intents.all())
guild_id = 0000000 # id сервера
token = "_______" # токен бота
word_list_file = "word_list.txt"
channels_file = "channels.txt"

def list_to_string(list):
    string = ""
    for word in list:
        string += word + " "
    return string

def file_to_list(destination):
    try:
        file = open(destination, 'r')
        all = file.read().replace("\n", " ")
        words = all.split()
        return words
    except FileNotFoundError:
        file = open(destination, 'w')

def add_to_file(list, destination):
    file = open(destination, 'w')
    all = list_to_string(list).replace(" ", "\n")
    file.write(all)

word_list = file_to_list(word_list_file)
channels = file_to_list(channels_file)

def right_channel(ctx):
    channel_name = ctx.channel.name
    return (channel_name in channels)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=guild_id))
    print(f"{bot.user} is ready")

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    embed = discord.Embed(
        title="Новый участник",
        description=f"{member.name}",
        color=0xffffff
    )
    await channel.send(embed=embed)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    channel_name = message.channel.name
    if (channel_name in channels) and not(message.author.guild_permissions.administrator):
        for content in message.content.split():
            for censored_word in word_list:
                if content == censored_word:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} сообщение содержит запрещённые слова")

@bot.event
async def on_command_error(ctx, error):
    print(error)
    if right_channel(ctx):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention} у вас недостаточно прав для выполнения команды")
        elif isinstance(error, commands.UserInputError):
            embed = discord.Embed(
                description=f"Правильное использование команды: {ctx.prefix}{ctx.command.name}\nExample: {ctx.prefix}{ctx.command.usage}",
                color=0xffffff
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(f"{ctx.author.mention} такой команды нет")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{ctx.author.mention} в команде указан неверный аргумент")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{ctx.author.mention} у меня недостаточно прав для выполнения команды")

@bot.command(name="turn_on",aliases=["on"])
@commands.has_permissions(administrator=True)
async def turn_on(ctx):
    channel_name = ctx.channel.name
    if not(channel_name in channels):
        channels.append(channel_name)
        add_to_file(channels,channels_file)
        await ctx.send("Бот включён")
        await ctx.message.delete()
    else:
        await ctx.send("Бот уже включён")

@bot.command(name="turn_off",aliases=["off"])
@commands.has_permissions(administrator=True)
async def turn_off(ctx):
    channel_name = ctx.channel.name
    if channel_name in channels:
        channels.remove(channel_name)
        add_to_file(channels, channels_file)
        await ctx.send("Бот выключён")
        await ctx.message.delete()
    else:
        await ctx.send("Бот уже выключён")

@bot.command(name="hello",aliases=["Привет","привет"])
async def hello(ctx):
    if right_channel(ctx):
        await ctx.send(f"Привет, {ctx.author.mention}")

@bot.command(name="censore",aliases=["Censore"],usage="censore <слово>")
@commands.has_permissions(administrator=True)
async def censore(ctx, bad_word):
    if right_channel(ctx):
        if not(bad_word in word_list):
            word_list.append(bad_word)
            add_to_file(word_list, word_list_file)
            await ctx.send(f"Слово '{bad_word}' добавлено в список запрещённых")
            await ctx.message.delete()

@bot.command(name="censore_list",aliases=["ban_words"],usage="censore_list/ban_words")
async def censore_list(ctx):
    if right_channel(ctx):
        await ctx.send(list_to_string(word_list))

@bot.command(name="kick",aliases=["Kick"],usage="kick/Kick <@user> <Причина (необязательно)>")
@commands.has_permissions(kick_members=True, administrator=True)
async def kick(ctx, member: discord.Member, *, reason="Нарушение правил"):
    if right_channel(ctx):
        await ctx.send(f"Администратор {ctx.author.mention} исключил пользователя {member.mention}")
        await member.kick(reason=reason)
        await ctx.message.delete()

@bot.command(name="ban",aliases=["Ban"],usage="ban/Ban <@user> <Причина (необязательно)>")
@commands.has_permissions(ban_members=True, administrator=True)
async def ban(ctx, member: discord.Member, *, reason="Нарушение правил"):
    if right_channel(ctx):
        await ctx.send(f"Администратор {ctx.author.mention} забанил пользователя {member.mention}")
        await member.ban(reason=reason)
        await ctx.message.delete()

@bot.command(name="time_out",aliases=["Time_out"],usage="time_out <@user> <Причина (необязательно)>")
@commands.has_permissions(administrator=True)
async def time_out(ctx, member: discord.Member, time: int, *, reason="Нарушение правил"):
    if right_channel(ctx):
        view = discord.ui.View()

        button_day = discord.ui.Button(label="дней", style=discord.ButtonStyle.primary)
        button_hour = discord.ui.Button(label="часов", style=discord.ButtonStyle.primary)
        button_minute = discord.ui.Button(label="минут", style=discord.ButtonStyle.primary)
        async def button_day_callback(interaction):
            if interaction.user == ctx.author:
                await member.timeout(datetime.timedelta(days=time), reason=reason)
                await interaction.response.edit_message(
                    content=f"Администратор {ctx.author.mention} замьютил пользователя {member.mention} на {time} дней",
                    view=None
                )
        async def button_hour_callback(interaction):
            if interaction.user == ctx.author:
                await member.timeout(datetime.timedelta(hours=time), reason=reason)
                await interaction.response.edit_message(
                    content=f"Администратор {ctx.author.mention} замьютил пользователя {member.mention} на {time} часов",
                    view=None
                )
        async def button_minute_callback(interaction):
            if interaction.user == ctx.author:
                await member.timeout(datetime.timedelta(minutes=time), reason=reason)
                await interaction.response.edit_message(
                    content=f"Администратор {ctx.author.mention} замьютил пользователя {member.mention} на {time} минут",
                    view=None
                )

        button_day.callback = button_day_callback
        view.add_item(button_day)
        button_hour.callback = button_hour_callback
        view.add_item(button_hour)
        button_minute.callback = button_minute_callback
        view.add_item(button_minute)

        await ctx.send(f"Замьютить пользователя {member.mention} на {time}:", view=view)

@bot.command(name="clear",aliases=["Clear"],usage="clear/Clear <количество сообщений>")
async def clear(ctx, amount: int):
    if right_channel(ctx):
        messages = await ctx.channel.purge(limit=amount+1)
        await ctx.send(f"{len(messages)-1} сообщений было очищено", delete_after = 3)

@bot.command(name="clear_chat",aliases=["Clear_chat","clear_all","Clear_all"])
async def clear_chat(ctx):
    if right_channel(ctx):
        messages = await ctx.channel.purge()
        await ctx.send(f"{len(messages)-1} сообщений было очищено", delete_after = 3)

@bot.tree.command(name="calc", description="Простой калькулятор",guild=discord.Object(id=guild_id))
@app_commands.describe(a="Первое число",oper="Операция",b="Второе число")
async def calc(interaction: discord.Interaction, a: int, oper: str, b: int):
    if oper=='+':
        result = a+b
    elif oper=='-':
        result = a-b
    elif oper=='*':
        result = a*b
    elif oper=='/':
        result = a/b
    elif oper==':':
        result = a/b
    else:
        result = "Неверный оператор"

    await interaction.response.send_message(str(result))

@bot.tree.command(name="roll", description="Случайное число от 0 до 100",guild=discord.Object(id=guild_id))
async def roll(interaction: discord.Interaction):
    number = random.randint(0,100)
    await interaction.response.send_message(str(number))

class rating_dropdown(discord.ui.View):
    def __init__(self, member):
        super().__init__()
        self.member = member
    answer = None
    @discord.ui.select(
        placeholder="Оцените ваши впечатления от сервера:",
        options=[
            discord.SelectOption(label="0", value=0),
            discord.SelectOption(label="1", value=1),
            discord.SelectOption(label="2", value=2),
            discord.SelectOption(label="3", value=3),
            discord.SelectOption(label="4", value=4),
            discord.SelectOption(label="5", value=5)
        ]
    )
    async def server_rating(self, interaction: discord.Interaction, select: discord.ui.Select()):
        if interaction.user == self.member:
            self.answer = select.values
            await interaction.response.edit_message(
                content=f"Спасибо за оценку {str(self.answer[0])}!",
                view=None
            )

@bot.command(name="rating",aliases=["Rating"])
async def rating(ctx):
    if right_channel(ctx):
        await ctx.send(f"{ctx.author.mention}")
        view = rating_dropdown(member=ctx.author)
        await ctx.send(view=view)

@bot.command(name="rate",aliases=["Rate"])
async def rate(ctx, member: discord.Member):
    if right_channel(ctx):
        await ctx.send(f"{member.mention}, администратор {ctx.author.mention} вашим мнением о сервере")
        view = rating_dropdown(member=member)
        await ctx.send(view=view)


bot.run(token)