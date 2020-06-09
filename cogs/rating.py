import discord
from database import *
from discord.ext import commands
import typing

class Ratings(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command(name="profile")
  async def _profile(self, ctx, user: typing.Optional[discord.User]=None):
    channel = ctx.channel
    
    if user == None:
      user = ctx.author
    
    listings = sales(str(user.id))

    stats = profile(user.id)

    if not stats:
      await channel.send(f"{str(user)} hasn't used this trading service yet.")
      return

    m=f"> ***{str(user)}'s Listings:***\n"
    
    if not listings:
      m += "None\n"
    
    for l in listings:
      item = l["Item_ID"].upper()
      price = l["Price"]
      m += f"**{item}**: {price} coins\n"
    
    m += f"\n> {stats[0]} vouch(es), {stats[1]} report(s)."

    await channel.send(m)

  @commands.command()
  async def vouch(self, ctx, *, user: discord.User):
    voucher = ctx.author
    
    if user == voucher:
      await ctx.send("You can't vouch yourself.")
      return
    
    error = feedback(str(user.id), 1, str(voucher.id))

    if error == 0:
      await ctx.send("That user has not made any offers yet.")
      return
    
    if error == 1:
      await ctx.send("You haven't been involved yet. Make a listing or intiate a trade offer first.")
      return

    if error == 2:
      await ctx.send("You have already vouched.")
      return
    
    await ctx.send(f"You have vouched {str(user)}.")

  @commands.command()
  async def report(self, ctx, *, user: discord.User):
    voucher = ctx.author
    
    if user == voucher:
      await ctx.send("You can't report yourself.")
      return
    
    error = feedback(str(user.id), -1, str(voucher.id))

    if error == 0:
      await ctx.send("That user has not made any offers yet.Make a listing or intiate a trade offer first.")
      return
    
    if error == 1:
      await ctx.send("You haven't been involved yet.")
      return

    if error == 2:
      await ctx.send("You have already reported.")
      return
    
    await ctx.send(f"You have reported {str(user)}.")

  @commands.command()
  async def unrate(self, ctx, *, user: discord.User):
    voucher = ctx.author
    
    if user == voucher:
      await ctx.send("You can't unrate yourself.")
      return
    
    feedback(str(user.id), 0, str(voucher.id))

    await ctx.send(f"You have cleared your rating of {str(user)}.")

def setup(client):
  client.add_cog(Ratings(client))