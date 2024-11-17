import os
import discord
import yt_dlp
import asyncio

from dotenv import load_dotenv
from discord.ext import commands
from discord import Interaction
from discord import FFmpegPCMAudio
from discord import app_commands

queue = []

load_dotenv('Token.env')
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.tree.sync()

@client.tree.command(name="join", description="Make the bot join your voice channel.")
async def join(interaction: discord.Interaction):
    channel = interaction.user.voice.channel
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f"เข้ามาในช่อง {channel} แล้วจ้าา!")
    else:
        await interaction.response.send_message("คุณยังไม่ได้เอาผมเข้าช่องดิสเลย!")

@client.tree.command(name="leave",description="Make the bot leave your voice channel.")
async def leave(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await interaction.response.send_message("ออกจากช่องดิสแล้วจ้าาา!")
    else:
        await interaction.response.send_message("คุณยังไม่ได้เอาผมเข้าช่องดิสเลย!")

@client.tree.command(name="play",description="Make the bot play a song.")
async def play(interaction: discord.Interaction, url: str):
    try:
        await interaction.response.defer()
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'noplaylist': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info['title']

        if interaction.guild.voice_client is None:
            if interaction.user.voice:
                channel = interaction.user.voice.channel
                await channel.connect()
            else:
                await interaction.followup.send("Join a voice channel first!")
                return
        
        vc = interaction.guild.voice_client

        if vc.is_playing():
            queue.append(url)
            await interaction.followup.send(f"Add queue: {title}")
        else:
            await play_song(interaction, url)

    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")

async def play_song(interaction: discord.Interaction, url: str):
    vc = interaction.guild.voice_client

    try:
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'noplaylist': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info['title']

        #ตรงส่วนนี้ทำให้บอทสามารถเล่นเพลงอันต่อไปได้
        def play_next(_):
            if queue:
                next_url = queue.pop(0)
                client.loop.create_task(play_song(interaction, next_url))
            else:
                client.loop.create_task(interaction.followup.send("ไม่มีเพลงต่อแล้ว งั้นพี่ขอออกเลยละกันนน!"))
                client.loop.create_task(vc.disconnect())

        vc.play(FFmpegPCMAudio(audio_url), after=play_next)
        await interaction.followup.send(f"Now playing: {title}")

    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")

@client.tree.command(name="skip",description="Skip the current song.")
async def skip(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("ยังไม่ได้เช้าช่องดิสเลย.")
        return

    if interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop() 
        await interaction.response.send_message("ข้ามเพลงแล้วจ้าา!")
    else:
        await interaction.response.send_message("ไม่มีเพลงให้ข้ามนะ:D")

client.run(token)
