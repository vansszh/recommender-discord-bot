import discord
from discord.ext import commands

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='search')
    async def search_servers(self, ctx, *, keyword: str):
        from main import recommender
        
        keyword_lower = keyword.lower()
        matching_servers = []
        
        for server in recommender.servers:
            server_name = server.get('name', '').lower()
            server_desc = server.get('description', '').lower()
            server_tags = [tag.lower() for tag in server.get('tags', [])]
            
            if (keyword_lower in server_name or 
                keyword_lower in server_desc or 
                any(keyword_lower in tag for tag in server_tags)):
                matching_servers.append(server)
        
        if not matching_servers:
            embed = discord.Embed(
                title="No Results Found",
                description=f"No servers found matching: **{keyword}**",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"Search Results for '{keyword}'",
            description=f"Found {len(matching_servers)} matching server(s)",
            color=discord.Color.blue()
        )
        
        for idx, server in enumerate(matching_servers[:5], 1):
            name = server.get('name', 'Unknown Server')
            description = server.get('description', 'No description')
            tags = server.get('tags', [])
            invite_link = server.get('invite_link', 'No invite')
            
            field_value = f"{description}\n"
            if tags:
                field_value += f"**Categories:** {', '.join(tags)}\n"
            field_value += f"**Invite:** {invite_link}"
            
            embed.add_field(
                name=f"{idx}. {name}",
                value=field_value,
                inline=False
            )
        
        if len(matching_servers) > 5:
            embed.set_footer(text=f"Showing 5 of {len(matching_servers)} results")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Search(bot))
