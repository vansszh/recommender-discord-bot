import discord
from discord.ext import commands

class Categories(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='categories')
    async def show_categories(self, ctx):
        from main import recommender
        
        categories = recommender.get_all_categories()
        
        if not categories:
            embed = discord.Embed(
                title="No Categories Available",
                description="The server database is empty.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="Available Server Categories",
            description="Here are all the categories in our database. Mention the bot with your interests!",
            color=discord.Color.blue()
        )
        
        categories_text = ", ".join(categories)
        
        embed.add_field(
            name=f"Total Categories: {len(categories)}",
            value=categories_text,
            inline=False
        )
        
        embed.add_field(
            name="How to Use",
            value="Mention the bot and tell it what you're interested in!\nExample: @bot I like gaming and music",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Categories(bot))
