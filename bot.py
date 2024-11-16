import os
import discord
import yt_dlp
import asyncio

from dotenv import load_dotenv
from discord.ext import commands
from discord import Interaction
from discord import FFmpegPCMAudio

queue = []

load_dotenv('heheha.env')
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

@client.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"เข้ามาในช่อง {channel} แล้วจ้าา!")
    else:
        await ctx.send("คุณยังไม่ได้เอาผมเข้าช่องดิสเลย!")

@client.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("ออกจากช่องดิสแล้วจ้าาา!")
    else:
        await ctx.send("คุณยังไม่ได้เอาผมเข้าช่องดิสเลย!")

@client.command()
async def play(ctx, url: str):
    if ctx.voice_client is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("Join a voice channel first!")
            return
    
    vc = ctx.voice_client

    if vc.is_playing():
        queue.append(url)
        await ctx.send("Added to the queue!")
    else:
        await play_song(ctx, url)

async def play_song(ctx, url):
    vc = ctx.voice_client

    try:
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'noplaylist': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info['title']

        #ตรงส่วนนี้ทำให้บอทสามารถเล่นเพลงอันต่อไปได้
        def play_next(_):
            if queue:
                next_url = queue.pop(0)
                client.loop.create_task(play_song(ctx, next_url))
            else:
                client.loop.create_task(ctx.send("Queue is empty. Leaving the channel!"))
                client.loop.create_task(vc.disconnect())

        vc.play(FFmpegPCMAudio(audio_url), after=play_next)
        await ctx.send(f"Now playing: {title}")

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@client.command()
async def skip(ctx):
    if ctx.voice_client is None:
        await ctx.send("I'm not connected to a voice channel.")
        return

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop() 
        await ctx.send("Skipped the current track!")
    else:
        await ctx.send("There's nothing to skip!")



client.run(token)
