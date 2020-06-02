from airtable import Airtable

items = Airtable("appqJlcI4lSTzhtDN", "Item")
trades = Airtable("appqJlcI4lSTzhtDN", "Trade_Ad")

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

def new_trade(id, item, price):
  if not items.search('Item_ID', item):
    return 
  
  g = find(id, item)
  if g:
    return trades.update(g[0], {"Price": price})

  n = 1
  while trades.match("Trade_ID", str(n)):
    n+=1
  
  return trades.insert({"Trade_ID": str(n), "Discord_ID":id, "Item_ID":item, "Price":price})

def search(item, listings=5):
  return [d["fields"] for d in trades.search("Item_ID", item, sort="Price", max_records=listings)]

def item_list():
  return [d["fields"]["Item_ID"] for d in items.get_all(sort="Item_ID")]

def sales(id):
  return [d["fields"] for d in trades.search("Discord_ID", id)]
