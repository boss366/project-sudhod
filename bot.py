import os
from dotenv import load_dotenv
import discord

load_dotenv('heheha.env')
token = os.getenv('DISCORD_TOKEN')

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(token)

print(f"Token loaded: {token}")  # Verify if the token is loaded correctly
