import discord
from discord.ext import commands
import json
import os
from typing import List, Dict
from dotenv import load_dotenv
import re
import requests

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

user_conversations = {}

GROQ_API_KEY = os.getenv('groq_api')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class ServerRecommender:
    
    def __init__(self, servers_file='servers.json'):
        self.servers_file = servers_file
        self.servers = self.load_servers()
    
    def load_servers(self) -> List[Dict]:
        try:
            if os.path.exists(self.servers_file):
                with open(self.servers_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Warning: {self.servers_file} not found. Using empty server list.")
                return []
        except Exception as e:
            print(f"Error loading servers: {e}")
            return []
    
    def find_matching_servers(self, interests: List[str], limit: int = 5) -> List[Dict]:
        if not self.servers:
            return []
        
        normalized_interests = [interest.lower().strip() for interest in interests]
        
        scored_servers = []
        for server in self.servers:
            score = 0
            server_tags = [tag.lower() for tag in server.get('tags', [])]
            
            for interest in normalized_interests:
                for tag in server_tags:
                    if interest == tag:
                        score += 10
                    elif interest in tag or tag in interest:
                        score += 5
            
            invite_link = server.get('invite_link')
            has_valid_invite = invite_link and invite_link not in [None, 'null', 'No invite available'] and invite_link.startswith('http')
            
            if score > 0 and has_valid_invite:
                scored_servers.append((score, server))
        
        scored_servers.sort(reverse=True, key=lambda x: x[0])
        return [server for score, server in scored_servers[:limit]]
    
    def get_all_categories(self) -> List[str]:
        categories = set()
        for server in self.servers:
            for tag in server.get('tags', []):
                categories.add(tag)
        return sorted(list(categories))

recommender = ServerRecommender()

def call_ai_api(prompt: str) -> str:
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {GROQ_API_KEY}'
        }
        
        data = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            print(f"Groq API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return None

def extract_interests_with_ai(user_message: str) -> List[str]:
    try:
        all_categories = recommender.get_all_categories()
        categories_str = ', '.join(all_categories) if all_categories else 'music, gaming, art, coding, anime, sports, memes, movies'
        
        prompt = f"""You are a helpful assistant that extracts user interests from text.

Available categories: {categories_str}

User message: "{user_message}"

Extract all interests/keywords from the user's message that match or relate to the available categories. Return ONLY a comma-separated list of interests, nothing else.

Examples:
- "I like music and gaming" -> music, gaming
- "I enjoy playing minecraft and watching anime" -> gaming, minecraft, anime
- "I'm into coding and tech stuff" -> coding

Now extract from the user message above:"""
        
        response_text = call_ai_api(prompt)
        if not response_text:
            return []
        
        interests = [i.strip() for i in response_text.split(',')]
        interests = [i for i in interests if i and len(i) > 0]
        
        return interests
    except Exception as e:
        print(f"Error extracting interests: {e}")
        return []

async def generate_ai_response(user_message: str, context: str = "") -> str:
    try:
        prompt = f"""You are a friendly Discord server recommendation bot. Your job is to chat naturally with users and help them find Discord servers.

{context}

User message: "{user_message}"

Respond in a friendly, conversational way. If the user hasn't shared their interests yet, ask them what they're interested in. Keep responses short (2-3 sentences max)."""
        
        response_text = call_ai_api(prompt)
        if not response_text:
            return "Hey! I'm here to help you find Discord servers. What are your interests?"
        
        return response_text
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "Hey! I'm here to help you find Discord servers. What are your interests?"

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    
    recommender.servers = recommender.load_servers()
    print(f'Loaded {len(recommender.servers)} servers from {recommender.servers_file}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    bot_mentioned = bot.user in message.mentions or message.reference and message.reference.resolved and message.reference.resolved.author == bot.user
    
    if bot_mentioned:
        async with message.channel.typing():
            user_msg = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
            
            if not user_msg:
                user_msg = "hi"
            
            interests = extract_interests_with_ai(user_msg)
            
            if interests and len(interests) > 0:
                user_conversations[message.author.id] = {
                    'state': 'processing_interests',
                    'interests': interests
                }
                
                matching_servers = recommender.find_matching_servers(interests)
                
                await send_recommendations(message.channel, interests, matching_servers, message.author)
            else:
                user_conversations[message.author.id] = {'state': 'awaiting_interests'}
                
                ai_response = await generate_ai_response(user_msg, "The user hasn't mentioned specific interests yet. Ask them what they're interested in.")
                await message.reply(ai_response)
        
        return
    
    if message.author.id in user_conversations:
        state = user_conversations[message.author.id].get('state')
        
        if state == 'awaiting_interests':
            async with message.channel.typing():
                interests = extract_interests_with_ai(message.content)
                
                if interests and len(interests) > 0:
                    matching_servers = recommender.find_matching_servers(interests)
                    
                    del user_conversations[message.author.id]
                    
                    await send_recommendations(message.channel, interests, matching_servers, message.author)
                else:
                    await message.reply("I couldn't detect any interests from your message. Can you mention specific topics like music, gaming, coding, anime, etc?")
            
            return
    
    await bot.process_commands(message)

async def send_recommendations(channel, interests: List[str], servers: List[Dict], user: discord.User = None):
    
    embed = discord.Embed(
        title="Recommended Discord Servers",
        description=f"Based on your interests: **{', '.join(interests)}**",
        color=discord.Color.green()
    )
    
    if not servers:
        embed.color = discord.Color.orange()
        embed.description = f"Sorry, I don't have any servers with valid invite links matching: **{', '.join(interests)}**"
        embed.add_field(
            name="Where to find servers:",
            value="Try searching on:\n• [DISBOARD](https://disboard.org/servers)\n• [Discord.me](https://discord.me/servers)\n• [Top.gg](https://top.gg/servers)",
            inline=False
        )
        
        if user:
            await channel.send(f"{user.mention}", embed=embed)
        else:
            await channel.send(embed=embed)
        return
    
    for idx, server in enumerate(servers, 1):
        name = server.get('name', 'Unknown Server')
        description = server.get('description', 'No description available')
        invite_link = server.get('invite_link', 'No invite link')
        tags = server.get('tags', [])
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
    
    embed.set_footer(text=f"Found {len(servers)} matching servers | Mention me again for more recommendations")
    
    if user:
        await channel.send(f"{user.mention}", embed=embed)
    else:
        await channel.send(embed=embed)

async def load_commands():
    commands_dir = 'commands'
    if not os.path.exists(commands_dir):
        print(f"Commands directory not found: {commands_dir}")
        return
    
    for filename in os.listdir(commands_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'commands.{filename[:-3]}')
                print(f'Loaded command: {filename}')
            except Exception as e:
                print(f'Failed to load {filename}: {e}')

async def main():
    async with bot:
        await load_commands()
        
        TOKEN = os.getenv('TOKEN')
        
        if not TOKEN:
            print("Error: TOKEN environment variable not set!")
            return
        
        await bot.start(TOKEN)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
