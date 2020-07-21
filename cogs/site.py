from flask import flash, request, redirect, Flask, render_template
from multiprocessing import Process
from wtforms import Form, StringField, SelectField
import os

class ItemSearchForm(Form):
  search = StringField("Item")

import datetime
import discord
from discord.ext import commands

app = Flask('')
'''
@app.route('/', methods=['GET', 'POST'])
def home():
    search = ItemSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('index.html', form=search)
'''

def run():
    app.run(host='127.0.0.1',port=8080)


t = Process(target=run)
t.daemon = True
db = None

@app.route('/')
def home():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    sales = db.search("gold smelted", listings=5)
    prices = [x["Price"] for x in sales]
    stats = [db.profile(str(x["Discord_ID"])) for x in sales]
    vouches = [s[0] for s in stats]
    reports = [s[1] for s in stats]
    
    items = zip(prices, vouches, reports)
    
    
    return render_template('index.html', items=items)

class Site(commands.Cog):  
  def __init__(self, client):
    self.client = client
    t.start()
  
def setup(client):
  global db
  db = client.get_cog("Database")
  client.add_cog(Site(client))

def teardown(client):
  t.kill()
  t.join(10)
  if not t.exitcode:
    exit(0)
  t.close()
  client.remove_cog("Site")
  
  



