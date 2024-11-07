import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv('heheha.env')
token = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@client.event
async def on_ready():
    print(f'Hi, I am a Bot for coding!!!')

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(token)
