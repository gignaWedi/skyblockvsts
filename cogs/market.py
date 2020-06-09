import discord
from database import *
from discord.ext import commands
import typing
import re
import time

def check(author):
  def inner_check(message):
    return message.author == author and re.match(r"-buy \d+", message.content)
  return inner_check

def check2(author):
  def inner_check(message):
    return message.author == author and re.match(r"[yY]([Ee][sS])?", message.content)
  return inner_check

class Market(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  async def sell(self, ctx, price: int, *, item):
    start = time.time() 
    channel = ctx.channel
    user = ctx.author
    item = item.lower()

    if item not in item_list():
      if not item_id(item):
        await channel.send(f'"{item}" is not a valid item name. Use -list to see the list of valid item names.')
        return
      item = item_id(item)
    
    new_trade(str(user.id), item, price)
    print(time.time()-start)
    await channel.send(f"New posting of {item.upper()} for {price} coins created.")
  
  @commands.command(name = "list")
  async def _list(self, ctx):
    channel = ctx.channel
    
    if isinstance(channel, discord.TextChannel):
      await ctx.send("The Item ID list has been sent to you via DMs.")

    n = 0

    m = "> ***Item ID List:***\n```\n"
    for i in item_list():
      m += f"{i:<30s}"

      n+=1

      if n % 5 == 0:
        m += "\n"
      if n % 60 == 0:
        await ctx.author.send(m+"```")
        m = "```\n"
    
    m+="```"
    await ctx.author.send(m)

  @commands.command(name="alias")
  async def _alias(self, ctx, *, item):
    item= item.lower()

    if item not in item_list():
      await ctx.send(f'"{item}" is not a valid item name. Use -list to see the list of valid item names.')
      return
    names = alias(item)

    if not names:
      await ctx.send(f"{item.upper()} has no known aliases.")
      return

    names  = '\n'.join(names)
    await ctx.send(f"Aliases for {item.upper()}:\n{names}")

  @commands.command()
  async def purge(self, ctx):
    channel = ctx.channel
    user = ctx.author

    await channel.send("Are you sure you want to purge all of your listings? (y/n):")
    msg = await self.client.wait_for("message", check=check2(user), timeout=30)
    
    g = remove_all(str(user.id))
    if not g:
      await channel.send("You have no listings.")
      return
    
    await channel.send(f"{len(g)} listing(s) removed.")

  @commands.command()
  async def remove(self, ctx, *, item):
    channel = ctx.channel
    user = ctx.author
    item = item.lower()

    if item not in item_list():
      if not item_id(item):
        await channel.send(f'"{item}" is not a valid item name. Use -list to see the list of valid item names.')
        return
      item = item_id(item)
    
    g = remove_trade(str(user.id), item)
    if not g:
      await channel.send(f"You have no listings for {item.upper()}.")
      return
    
    await channel.send(f"Removed listing for {item.upper()}.")

  @commands.command()
  async def buy(self, ctx, *, item):
    start = time.time() 
    channel = ctx.channel
    user = ctx.author
    num = 5
    item = item.lower()

    if item.isnumeric():
      return
    
    if item not in item_list():
      if not item_id(item):
        await channel.send(f'"{item}" is not a valid item name. Use -list to see the list of valid item names.')
        return
      item = item_id(item)

    print(time.time()-start)
    

    listings = search(item, str(user.id), num)
    
    if not listings:
      await channel.send(f"There are no listings for {item.upper()}")
      return

    m = f"> ***Listings for {item.upper()}:*** (To choose, use -buy <number>, e.g. -buy 1)\n"
    for i, l in enumerate(listings, 1):
      price = l["Price"]
      user_id = l["Discord_ID"]
      stats = profile(str(user_id))
      stats = [0,0]

      m += f"{i}. {price} coins. {stats[0]} vouches, {stats[1]} reports.\n"
    
    print(time.time()-start)

    await channel.send(m)
    msg = await self.client.wait_for("message", check=check(user), timeout=30)
    
    listing = int(msg.content.split()[1])
    if  listing > len(listings) or listing <= 0:
      await channel.send("That is not a valid listing number.")
      return
    
    listing = listings[listing-1]
    sellerid = int(listing["Discord_ID"])

    seller = self.client.get_user(sellerid)
    
    stats = profile(str(sellerid))

    await channel.send("Sending notice to seller.")
    await seller.send(f"{str(user)} ({stats[0]} vouches, {stats[1]} reports) has taken interest in your {item.upper()} sale. DM the user if you wish to intiate a sale. If this listing is outdated, use -remove {item.lower()} to remove it.") 

def setup(client):
  client.add_cog(Market(client))