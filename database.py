from airtable import Airtable

items = Airtable("appqJlcI4lSTzhtDN", "Item")
trades = Airtable("appqJlcI4lSTzhtDN", "Trade_Ad")
users = Airtable("appqJlcI4lSTzhtDN", "User")
aliases = Airtable("appqJlcI4lSTzhtDN", "Alias")

def find(id, item):
  a= {d["id"] for d in trades.search("Discord_ID", id)}
  b= {d["id"] for d in trades.search("Item_ID", item)}
  
  trade = list(a & b)
  return trade 

def remove_trade(id, item):
  return trades.batch_delete(find(id, item))

def remove_all(id):
  a= {d["id"] for d in trades.search("Discord_ID", id)}
  return trades.batch_delete(a)

def add_user(id):
  if not users.search("Discord_ID", id):
    users.insert({"Discord_ID": id, "Vouches": 0, "Reports":0})

def new_trade(id, item, price):
  add_user(id)

  if not items.search('Item_ID', item):
    return 
  
  g = find(id, item)
  if g:
    return trades.update(g[0], {"Price": price})

  n = 1
  while trades.match("Trade_ID", str(n)):
    n+=1
  
  return trades.insert({"Trade_ID": str(n), "Discord_ID":id, "Item_ID":item, "Price":price})

def search(item,id,listings=5):
  records = [j["id"] for j in trades.search("Item_ID", item, sort="Price", max_records=listings+1)]

  try:
    records.remove(find(id, item)[0])
  except:
    pass
  
  add_user(id)

  return [trades.get(d)["fields"] for d in records[:listings]]

def item_list():
  return [d["fields"]["Item_ID"] for d in items.get_all(sort="Item_ID")]

def sales(id):
  return [d["fields"] for d in trades.search("Discord_ID", id)]

def profile(id):
  try:
    g =[users.match("Discord_ID", id)["fields"][key] for key in ["Vouches", "Reports"]]
  except:
    return

  return g

def feedback(id, value, invoker):
  try:
    g = users.match("Discord_ID", id)
  except:
    return 0
  
  try:
    users.match("Discord_ID", invoker)["fields"]["Discord_ID"]
  except:
    return 1
  
  try:
    vouchers = g["fields"]["Vouchers"].lstrip().split(" ")
  except:
    vouchers = []
  
  try:
    reporters = g["fields"]["Reporters"].lstrip().split(" ")
  except:
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

  users.update(g["id"], {"Vouches":len(vouchers), "Vouchers":" ".join(vouchers).lstrip()})
  users.update(g["id"], {"Reports":len(reporters), "Reporters":" ".join(reporters).lstrip()})
  return 999

def item_id(alias):
  try:
    g =aliases.match("Alias", alias)["fields"]["Item_ID"]
  except:
    return
  
  return g

def alias(item):
  try:
    g = aliases.search("Item_ID", item)
  except:
    return
  
  return [h['fields']["Alias"] for h in g] 
