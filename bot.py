import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv('heheha.env')
token = os.getenv('DISCORD_TOKEN')

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Hi I am {self.user.name}, I can help learning about coding.')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

        if message.author == self.user:
            return

        if message.content.startswith('!hello'):
            await message.channel.send('Hello World!')
    
intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(token)
