import discord
from discord.ext import commands
import typing
import re
import time
import math
import asyncio
from threading import Thread

d_lst=[]

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

  def cog_check(self, ctx):
    return 718522244996923524 in [r.id for r in self.client.get_guild(717177487091695677).get_member(ctx.author.id).roles]
  
  def convert(self, item):
    database = self.client.get_cog("Database")
    if item not in database.item_list():
      item = database.item_id(item)
      if not item:
        return
    return item
  
  def debounce(self, item, id):
    db = self.client.get_cog("Database")
    num=50 
    debounce_time=20
    def decay(x):
      return x * math.exp(-1/num)
    
    entry = (item,id)
    if entry not in d_lst:
      d_lst.append(entry)
      d = get_item_stats(item)["Demand"]
      set_demand(item, decay(d)+1)
      for key in item_list():
        if key != item:
          demand = get_item_stats(key)["Demand"]
          set_demand(key, decay(demand))
          
      time.sleep(debounce_time)
      d_lst.remove(entry)
      
  @commands.command()
  async def sell(self, ctx, price: int, *, item): 
    db = self.client.get_cog("Database")
    channel = ctx.channel
    user = ctx.author
    item = item.lower()
    item = self.convert(item)
    if not item:
      await channel.send(f'"{item}" is not a valid item name. Use -list to see the list of valid item names.')
      return
    
    if price > 1_000_000_000_000:
      await channel.send("Too large of a price. Price cap is 1 trillion coins.")
      return

    db.new_trade(str(user.id), item, price)
    await channel.send(f"New posting of {item.upper()} for {price} coins created.")
  
  @commands.command()
  async def stats(self, ctx, *,item):
    db = self.client.get_cog("Database")
    item = self.convert(item.lower())
    if not item:
      await channel.send(f'"{item}" is not a valid item name. Use -list to see the list of valid item names.')
      return
    
    stats = db.get_item_stats(item)
    m = f"> ***Stats for {item.upper()}***\n"
    for key in stats:
      if key not in ["Aliases"]:
        m += f"{key}: {stats[key]:.3f}\n"
    
    await ctx.send(m)
  
  @commands.command(name = "list")
  async def _list(self, ctx):
    db = self.client.get_cog("Database")
    channel = ctx.channel
    
    if isinstance(channel, discord.TextChannel):
      await ctx.send("The Item ID list has been sent to you via DMs.")

    n = 0

    m = "> ***Item ID List:***\n```\n"
    for i in db.item_list():
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
    db = self.client.get_cog("Database")
    item = self.convert(item.lower())
    if not item:
      await channel.send(f'"{item}" is not a valid item name. Use -list to see the list of valid item names.')
      return
      
    names = db.alias(item)
	
    if not names:
      await ctx.send(f"{item.upper()} has no known aliases.")
      return

    names  = '\n'.join(names)
    await ctx.send(f"Aliases for {item.upper()}:\n{names}")

  @commands.command()
  async def purge(self, ctx):
    db = self.client.get_cog("Database")
    channel = ctx.channel
    user = ctx.author

    await channel.send("Are you sure you want to purge all of your listings? (y/n):")
    msg = await self.client.wait_for("message", check=check2(user), timeout=30)
    
    g = db.remove_all(str(user.id))
    if not g:
      await channel.send("You have no listings.")
      return
    
    await channel.send(f"{len(g)} listing(s) removed.")

  @commands.command()
  async def remove(self, ctx, *, item):
    channel = ctx.channel
    user = ctx.author
    db = self.client.get_cog("Database")
    
    item = self.convert(item.lower())
    if not item:
      await channel.send(f'"{item}" is not a valid item name. Use -list to see the list of valid item names.')
      return
    
    g = db.remove_trade(str(user.id), item)
    if not g:
      await channel.send(f"You have no listings for {item.upper()}.")
      return
    
    await channel.send(f"Removed listing for {item.upper()}.")

  #@commands.Cog.listener()
  async def on_command(self, ctx):
    pass
    

  @commands.command()
  async def buy(self, ctx, *, item):
    channel = ctx.channel
    user = ctx.author
    num = 5
    item = item.lower()

    if item.isnumeric():
      return
    
    db = self.client.get_cog("Database")
    item = self.convert(item)
    if not item:
      await channel.send(f'"{item}" is not a valid item name. Use -list to see the list of valid item names.')
      return
    
    entry = (item,id)
    t = Thread(target=self.debounce, args=entry)
    t.start()
    listings = db.search(item, str(user.id), num)
    
    if not listings:
      await channel.send(f"There are no listings for {item.upper()}")
      return

    m = f"> ***Listings for {item.upper()}:*** (To choose, use -buy <number>, e.g. -buy 1)\n"
    for i, l in enumerate(listings, 1):
      price = l["Price"]
      user_id = l["Discord_ID"]
      stats = db.profile(str(user_id))

      m += f"{i}. {price} coins. {stats[0]} vouches, {stats[1]} reports.\n"
    

    await channel.send(m)
    msg = await self.client.wait_for("message", check=check(user), timeout=30)
    
    listing = int(msg.content.split()[1])
    if  listing > len(listings) or listing <= 0:
      await channel.send("That is not a valid listing number.")
      return
    
    listing = listings[listing-1]
    sellerid = int(listing["Discord_ID"])

    seller = self.client.get_user(sellerid)
    
    stats = db.profile(str(sellerid))

    await channel.send("Sending notice to seller.")
    await seller.send(f"{str(user)} ({stats[0]} vouches, {stats[1]} reports) has taken interest in your {item.upper()} sale. DM the user if you wish to intiate a sale. If this listing is outdated, use -remove {item.lower()} to remove it.") 

def setup(client):
  client.add_cog(Market(client))