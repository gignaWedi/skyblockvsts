import discord
from discord.ext import commands

class Greetings(commands.Cog):
  def __init__(self, client):
    self.client = client
  
  @commands.command()
  async def join(self, ctx):
    if 718522244996923524 in [r.id for r in self.client.get_guild(717177487091695677).get_member(ctx.author.id).roles]:
      await ctx.send("You are already a member.")
      return

    if ctx.guild == None or ctx.guild.id != 717177487091695677:
      await ctx.send("Join the official server (https://discord.gg/fs5PbVu) and get verified with AltDentifier to get started.")
      return
    
    await ctx.send("Get verified with AltDentifier to get started.")

  
def setup(client):
  client.add_cog(Greetings(client))

  
