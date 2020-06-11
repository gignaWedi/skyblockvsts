import discord
from discord.ext import commands
import time
from database import *
import os


class Debug(commands.Cog):
  def __init__(self, client):
    self.client = client
  
  def cog_check(self, ctx):
    return ctx.author.id == 395644655242444810

  @commands.command()
  async def ping(self, ctx):
    await ctx.send(f"Pong! {round(self.client.latency,1)}.")
  
  @commands.command(name="time")
  async def _time(self, ctx):
    await ctx.send("> Time activate.")

    start = time.time()
    print(start)

    await self.client.wait_for("message", check=lambda x: x.author == ctx.author, timeout=10)
    
    await self.client.wait_for("message", check=lambda x: x.author == self.client.user and x.channel == ctx.channel, timeout=10)
    
    end = time.time()
    delta = end - start
    await ctx.send(f"> Operation took {round(delta, 3)}.")
    
def setup(client):
  client.add_cog(Debug(client))