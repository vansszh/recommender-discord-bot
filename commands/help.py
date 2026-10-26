import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="Server Recommendation Bot",
            description="Find Discord servers based on your interests!",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="Mention the Bot",
            value="Just mention or ping the bot and chat naturally! The AI will understand your interests and recommend servers.",
            inline=False
        )
        embed.add_field(
            name="!search <keyword>",
            value="Search for servers by keyword in our database.",
            inline=False
        )
        embed.add_field(
            name="!categories",
            value="View all available server categories in our database.",
            inline=False
        )
        embed.add_field(
            name="!popular",
            value="View the most popular servers across all categories.",
            inline=False
        )
        embed.add_field(
            name="!random",
            value="Get random server recommendations to discover new communities.",
            inline=False
        )
        embed.add_field(
            name="!reload (Admin)",
            value="Reload the servers list from servers.json",
            inline=False
        )
        
        embed.set_footer(text="Mini Project by Vansh Sharma (Reg No: 2427010625) and Aditya Aman (Reg No: 2427010672)")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
