import discord
import typing
from discord.ext import commands
import os
import re
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = commands.Bot(command_prefix="-")

async def is_me(ctx):
  return ctx.author.id == 395644655242444810

@client.command()
@commands.check(is_me)
async def load(ctx, extension):
  client.load_extension(f"cogs.{extension}")
  await ctx.send(f"Loaded {extension}.") 

@client.command()
@commands.check(is_me)
async def unload(ctx, extension):
  client.unload_extension(f"cogs.{extension}")
  await ctx.send(f"Unloaded {extension}.") 

@client.command()
@commands.check(is_me)
async def reload(ctx, extension):
  client.unload_extension(f"cogs.{extension}")
  client.load_extension(f"cogs.{extension}")
  await ctx.send(f"Reloaded {extension}.")  

for filename in os.listdir("./cogs"):
  if filename.endswith(".py"):
    client.load_extension(f"cogs.{filename[:-3]}")

@client.event
async def on_ready():
  client.help_command.no_category = "Misc."
  print(client.user)

token = os.environ.get("DISCORD_BOT_SECRET")
client.run(token)