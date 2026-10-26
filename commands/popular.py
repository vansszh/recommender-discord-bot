import discord
from discord.ext import commands

class Popular(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='popular')
    async def show_popular(self, ctx):
        from main import recommender
        
        if not recommender.servers:
            embed = discord.Embed(
                title="No Servers Available",
                description="The server database is empty.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        sorted_servers = sorted(
            recommender.servers,
            key=lambda s: self.parse_member_count(s.get('member_count', '0')),
            reverse=True
        )[:5]
        
        embed = discord.Embed(
            title="Most Popular Servers",
            description="Top servers by member count",
            color=discord.Color.gold()
        )
        
        for idx, server in enumerate(sorted_servers, 1):
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
        
        await ctx.send(embed=embed)
    
    def parse_member_count(self, member_str: str) -> int:
        if not isinstance(member_str, str):
            return 0
        
        member_str = member_str.replace(',', '').replace('+', '').strip()
        
        if 'k' in member_str.lower():
            try:
                return int(float(member_str.lower().replace('k', '')) * 1000)
            except:
                return 0
        elif 'm' in member_str.lower():
            try:
                return int(float(member_str.lower().replace('m', '')) * 1000000)
            except:
                return 0
        else:
            try:
                return int(member_str)
            except:
                return 0

async def setup(bot):
    await bot.add_cog(Popular(bot))
