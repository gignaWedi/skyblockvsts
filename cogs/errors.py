import discord
from discord.ext import commands

class Errors(commands.Cog):

  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_command_error(self, ctx, error):
    if isinstance(error, commands.UserInputError) or isinstance(error, commands.ConversionError):
      await ctx.send(f"Usage: {self.client.command_prefix}{ctx.command} {ctx.command.signature}")
      return
    
    if isinstance(error, commands.CheckFailure):
      await ctx.send("You are unable to use this command.")
      return
    
    self.client.on_command_error(ctx, error)
  
def setup(client):
  client.add_cog(Errors(client))