from flask import flash, request, redirect, Flask, render_template
from multiprocessing import Process
from gevent.pywsgi import WSGIServer
from discord.ext import commands
import discord
import os
import datetime


from wtforms import Form, StringField, SelectField

class ItemSearchForm(Form):
  choices = [
  ("Item","Item"),
  ("Sale","Sale") 
  ]
  
  select = SelectField("Search for:", choices=choices)
  search = StringField("")
  

from flask_table import Table, Col

class SaleResults(Table):
    discord_id = Col('Discord_ID', show=False)
    item_id = Col('Item_ID')
    price = Col('Price')

class ItemResults(Table):
    Name = Col("Name")
    Demand = Col('Demand')
    RAP = Col('RAP')
    mRAP = Col('mRAP')
    Aliases = Col("aliases", show=False)

app = Flask('')

def run():
    app.secret_key = os.urandom(24)
    server = WSGIServer(('',5000),app)
    server.serve_forever()

t = Process(target=run)
t.daemon = True
db = None
dbc = None

'''
@app.route('/')
def home():
    sales = db.search("gold smelted", listings=5)
    prices = [x["Price"] for x in sales]
    stats = [db.profile(str(x["Discord_ID"])) for x in sales]
    vouches = [s[0] for s in stats]
    reports = [s[1] for s in stats]
    
    items = zip(prices, vouches, reports)
    
    
    return render_template('index.html', items=items)
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    search = ItemSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('index.html', form=search)

@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']
    select = search.data["select"]
    
    
    if select == "Item":
        if search.data['search'] == '':
            results = [dict(Name=e.key.name, **e) for e in dbc.query(kind="Item").fetch()]
        else:
            item = m.convert(search_string)
            
            if item:
              ekey = dbc.key("Item", item)
              e = dbc.get(ekey)
              

              results = [dict(Name=e.key.name, **e)]   
       
    if not results:
        flash('No results found!')
        return redirect('/')
        
    else:
        # display results
        table = ItemResults(results)
        return render_template('results.html', table=table)


class Site(commands.Cog):  
  def __init__(self, client):
    self.client = client
    t.start()
  
def setup(client):
  global db
  global dbc
  global m
  db = client.get_cog("Database")
  m = client.get_cog("Market")
  dbc = db.dbc
  
  client.add_cog(Site(client))

def teardown(client):
  t.kill()
  t.join(10)
  if not t.exitcode:
    exit(0)
  t.close()
  client.remove_cog("Site")
  
  



