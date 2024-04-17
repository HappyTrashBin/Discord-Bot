import discord
from discord.ext import commands
from discord.ext.commands import Bot

bot = Bot(command_prefix='!', intents=discord.Intents.all())

Censore = ["Fuck","fuck","Damn","damn"]

@bot.event
async def on_ready():
    print(f"{bot.user} is ready")

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    embed = discord.Embed(
        title="Новый участник",
        description=f"{member.name}#{member.discriminator}",
        color=0xffffff
    )
    await channel.send(embed=embed)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    for content in message.content.split():
        for censored_word in Censore:
            if content.lower() == censored_word:
                await message.delete()
                await message.channel.send(f"{message.author.mention} сообщение содержит запрещённые слова")

@bot.event
async def on_command_error(ctx, error):
    print(error)
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

@bot.command(name="hello",aliases=["Привет","привет"], usage="hello")
async def hello(ctx):
    await ctx.send(f"Привет, {ctx.author.mention}")

@bot.command(name="kick",aliases=["Кик","кик"], usage="kick <@user> <Причина (необязательно)>")
@commands.has_permissions(kick_members=True, administrator=True)
async def kick(ctx, member: discord.Member, *, reason="Нарушение правил"):
    await ctx.send(f"Администратор {ctx.author.mention} исключил пользователя {member.mention}")
    await member.kick(reason=reason)
    await ctx.message.delete()

@bot.command(name="ban",aliases=["Бан","бан"], usage="ban/Бан/бан <@user> <Причина (необязательно)>")
@commands.has_permissions(ban_members=True, administrator=True)
async def ban(ctx, member: discord.Member, *, reason="Нарушение правил"):
    await ctx.send(f"Администратор {ctx.author.mention} забанил пользователя {member.mention}")
    await member.ban(reason=reason)
    await ctx.message.delete()

@bot.command(name="mute",aliases=["Мут","мут"], usage="ban/Мут/мут <@user> <Причина (необязательно)>")
@commands.has_permissions(ban_members=True, administrator=True)
async def mute(ctx, member: discord.Member, *, reason="Нарушение правил"):
    role = discord.utils.get(member.guild.roles, id = 1229142907043188867)
    await member.add_roles(role)
    await ctx.send(f"Администратор {ctx.author.mention} замьютил пользователя {member.mention}")
    await member.ban(reason=reason)
    await ctx.message.delete()

@bot.command()
async def clear(ctx, amount: int):
    messages = await ctx.channel.purge(limit=amount+1)
    await ctx.send(f"{len(messages)-1} сообщений было очищено")


bot.run("MTIyOTEyOTY2NjgzNzg3Njg1OA.G6vD6k.SJIDXo_FSz3VFNWoT_qr6rh4DP_ZCP_hkgBERo")