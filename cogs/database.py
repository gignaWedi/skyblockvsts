import discord
from discord.ext import commands

from google.cloud import datastore

dbclient = datastore.Client()

class Database(commands.Cog):
  def __init__(self, client):
    self.client = client
    
  def find(self, id, item):
    query = dbclient.query(kind="Sale")
    
    result = query.add_filter("Item_ID", "=", item).add_filter("Discord_ID", "=", id).fetch()
    trade = list(result)
    return trade 

  def get_item_stats(self, item):
    ekey = dbclient.key("Item",item)
    item = dbclient.get(ekey)
    return dict(item)

  def set_demand(self, item, demand):
    ekey = dbclient.key("Item",item)
    item = dbclient.get(ekey)
    item["Demand"] = demand
    dbclient.put(item)

  def remove_trade(self, id, item):
    keys = []
    for e in self.find(id, item): 
      keys.append(e.key)
    dbclient.delete_multi(keys)
    return keys 

  def remove_all(self, id):
    query = dbclient.query(kind="Sale")
    result = query.add_filter("Discord_ID", "=", id).fetch()
    
    keys = []
    for e in list(result): 
      keys.append(e.key)
    dbclient.delete_multi(keys) 
    
    return keys

  def add_user(self, id):
    ekey = dbclient.key("User",id)
    
    user = dbclient.get(ekey)
    
    if not user:
      e = datastore.Entity(key=ekey)
      e.update({
        "Vouchers" : [],
        "Reporters" : [],
        "Vouches" : 0,
        "Reports" : 0
      })
      dbclient.put(e)

  def new_trade(self, id, item, price):
    self.add_user(id)
    
    ent = self.find(id, item)
    if ent:
      ent[0]["Price"] = price
      dbclient.put(ent[0])
      return
      
    e = datastore.Entity(key = dbclient.key("Sale"))
    e["Discord_ID"] = id
    e["Item_ID"] = item
    e["Price"] = price
    dbclient.put(e)

  def search(self, item,id,listings=5):  
    self.add_user(id)
    
    query = dbclient.query(kind="Sale")
    query.add_filter("Item_ID", "=", item)

    remove = self.find(id, item)
    
    results = query.fetch(limit=listings+1)
    results = list(results)
  
    for r in remove:
      if r in results:
        results.remove(r)
    
    return sorted(results, key=lambda x: x["Price"])

  def item_list(self):
    query = dbclient.query(kind="Item")
    result = list(query.fetch())
    items = []
    for e in result:
      items.append(e.key.name)
    items = sorted(items)
    return items

  def sales(self, id):
    query = dbclient.query(kind="Sale")
    results = query.add_filter("Discord_ID", "=", id).fetch()
    return [(e["Item_ID"],e["Price"]) for e in results]
    
  def profile(self, id):
    ekey = dbclient.key("User",id)
    user = dbclient.get(ekey) 
    if not user:
      return
    return (user["Vouches"],user["Reports"])

  def feedback(self, id, value, invoker):
    e1key = dbclient.key("User",id)
    e2key = dbclient.key("User",invoker)
    
    user = dbclient.get(e1key)
    
    if not user:
      return 0
    
    invoker = dbclient.get(e2key)
    
    if not invoker:
      return 1
    
    
    vouchers = user["Vouchers"]
    reporters = user["Reporters"]
    
    if vouchers is None:
      vouchers = []
    if reporters is None:
      reporters = []
    
    if value > 0:
      if str(invoker) in vouchers:
        return 2

      vouchers.append(str(invoker))
      if str(invoker) in reporters:
        reporters.remove(str(invoker))
    
    if value < 0:
      if str(invoker) in reporters:
        return 2

      reporters.append(str(invoker))
      if str(invoker) in vouchers:
        vouchers.remove(str(invoker))
    
    if value == 0:
      if str(invoker) in vouchers:
        vouchers.remove(str(invoker))
      
      if str(invoker) in reporters:
        reporters.remove(str(invoker))
    
    user["Vouches"] = len(vouchers)
    user["Reports"] = len(reporters)
    
    dbclient.put(user)
    return 999

  def item_id(self, alias):
    query = dbclient.query(kind="Item")
    result = list(query.fetch())
    for e in result:
      if alias in e["Aliases"]:
        return e.key.name
      
  def alias(self, item):
    ekey = dbclient.key("Item",item)
    item = dbclient.get(ekey)
    
    return item["Aliases"]
   
def setup(client):
  client.add_cog(Database(client))
