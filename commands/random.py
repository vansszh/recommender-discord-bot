import discord
from discord.ext import commands
import random

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='random')
    async def random_servers(self, ctx):
        from main import recommender
        
        if not recommender.servers:
            embed = discord.Embed(
                title="No Servers Available",
                description="The server database is empty.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        num_servers = min(3, len(recommender.servers))
        random_servers = random.sample(recommender.servers, num_servers)
        
        embed = discord.Embed(
            title="Random Server Recommendations",
            description="Discover new communities you might enjoy!",
            color=discord.Color.purple()
        )
        
        for idx, server in enumerate(random_servers, 1):
            name = server.get('name', 'Unknown Server')
            description = server.get('description', 'No description')
            tags = server.get('tags', [])
            invite_link = server.get('invite_link', 'No invite')
            member_count = server.get('member_count', 'Unknown')
            
            field_value = f"{description}\n"
            if tags:
                field_value += f"**Categories:** {', '.join(tags)}\n"
            field_value += f"**Members:** {member_count}\n"
            field_value += f"**Join:** {invite_link}"
            
            embed.add_field(
                name=f"{idx}. {name}",
                value=field_value,
                inline=False
            )
        
        embed.set_footer(text="Use !random again for different servers")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Random(bot))
