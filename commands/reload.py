import discord
from discord.ext import commands

class Reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='reload')
    @commands.has_permissions(administrator=True)
    async def reload_servers(self, ctx):
        from main import recommender
        
        recommender.servers = recommender.load_servers()
        
        embed = discord.Embed(
            title="Servers Reloaded",
            description=f"Successfully loaded {len(recommender.servers)} servers from {recommender.servers_file}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Reload(bot))
