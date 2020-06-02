import discord
import os
import re

from database import *

from keep_alive import keep_alive

client = discord.Client()

def check(author):
  def inner_check(message):
    return message.author == author and re.match(r"-buy \d+", message.content)
  return inner_check

def check2(author):
  def inner_check(message):
    return message.author == author and re.match(r"[yY]([Ee][sS])?", message.content)

@client.event
async def on_ready():
  print(client.user)
  
@client.event
async def on_message(message):
  channel = message.channel
  user = message.author
  content = message.content
  if user == client.user:
    return
  
  if re.match(r"-buy \w+( \d+)?", content):
    words = content.split(" ")
    item = words[1]

    if item.isnumeric():
      return
    
    if item not in item_list():
      await channel.send(f'"{item}" is not a valid item name. Use -list to see the list of valid item names.')
      return

    if len(words) == 3:
      listings = search(item, int(words[2]))
    else:
      listings = search(item)
    
    if not listings:
      await channel.send(f"There are no listings for {item.upper()}")
      return

    m = f"> ***Listings for {item.upper()}:*** (To choose, use -buy <number>, e.g. -buy 1)\n"
    for i, l in enumerate(listings, 1):
      price = l["Price"]
      m += f"{i}. {price} coins\n"

    await channel.send(m)
    msg = await client.wait_for("message", check=check(user), timeout=30)
   
    listing = int(msg.content.split()[1])
    if  listing > len(listings) or listing <= 0:
      await channel.send("That is not a valid listing number.")
      return
    
    listing = listings[listing-1]
    sellerid = int(listing["Discord_ID"])

    seller = client.get_user(sellerid)
    
    await channel.send("Sending notice to seller.")
    await seller.send(f"{user.name} has taken interest in your {item.upper()} sale. DM the user if you wish to intiate a sale. If this listing is outdated, use -remove {item.lower()} to remove it.")

  if re.match(r"-list", content):
    m = "> ***Item ID List:***\n"
    for i in item_list():
      m += i + "\n"
    
    await channel.send(m)
  
  if re.match(r"-sell \w+ \d+", content):
    words = content.split()
    item = words[1]
    price = int(words[2])

    if item not in item_list():
      await channel.send(f'"{item}" is not a valid item name. Use -list to see the list of valid item names.')
      return
    
    new_trade(str(user.id), item, price)
    await channel.send(f"New posting of {item.upper()} for {price} coins created.")
  
  if re.match(r"-remove \w+", content):
    item = content.split()[1]
    
    if item not in item_list():
      await channel.send(f'"{item}" is not a valid item name. Use -list to see the list of valid item names.')
      return
    
    g = remove_trade(str(user.id), item)
    if not g:
      await channel.send(f"You have no listings for {item.upper()}.")
      return
    
    await channel.send(f"Removed listing for {item.upper()}.") 
  
  if re.match(r"-sales", content):
    listings = sales(str(user.id))
    
    if not listings:
      await channel.send(f"You have no listings.")
      return
    
    m=f"> ***{user.name}'s Listings:***\n"
    for l in listings:
      item = l["Item_ID"].upper()
      price = l["Price"]
      m += f"**{item}**: {price} coins\n"
    
    await channel.send(m)
      
  if re.match(r"-purge", content):
    await channel.send("Are you sure you want to purge all of your listings? (y/n):")
    msg = await client.wait_for("message", check=check2(user), timeout=30)
    
    g = remove_all(str(user.id))
    if not g:
      await channel.send("You have no listings.")
      return
    
    await channel.send(f"{len(g)} listing(s) removed.")
  
  if re.match(r"-help", content):
    if isinstance(channel, discord.TextChannel):
      await channel.send("Commands have been sent to you via dms.")
    
    await user.send("""
    > ***Commands:***
    
    > -buy <item> [listings] 
    list listings for an item. <item> is the item id, [listings] (opt.) is the number of listings listed. Default is 5.
    e.g. -buy gold, -buy crystallized_iron 10
    > -help
    brings up this menu.
    > -list
    lists all item ids.
    > -purge
    removes all of your listings.
    > -remove <item>
    remove your listing for a particular item.
    e.g. -remove gold
    > -sell <item> <price>
    add a listing for an item. <item> is item id, <price> is listing price.
    e.g. -sell gold 1000000
    > -sales
    list all of your listings.
    """)

keep_alive()
token = os.environ.get("DISCORD_BOT_SECRET")
client.run(token)