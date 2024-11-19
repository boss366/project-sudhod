import os
import discord
import yt_dlp
import asyncio
import random
import json

from dotenv import load_dotenv
from discord.ext import commands
from discord import Interaction
from discord import FFmpegPCMAudio
from discord import app_commands
from discord.ui import Button, View

queue = []

load_dotenv('Token.env')
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

with open('quest.json', 'r') as file:
    data = json.load(file)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.tree.sync()

# commandเอาไว้เข้า
@client.tree.command(name="join", description="Make the bot join your voice channel.")
async def join(interaction: discord.Interaction):
    if interaction.user.voice is None:
        await interaction.response.send_message("คุณยังไม่ได้เอาผมเข้าช่องดิสเลย!", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    
    await channel.connect()
    await interaction.response.send_message(f"เข้ามาในช่อง {channel} แล้วจ้าา!")

# commandเอาไว้ออก
@client.tree.command(name="leave",description="Make the bot leave your voice channel.")
async def leave(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await interaction.response.send_message("ออกจากช่องดิสแล้วจ้าาา!")
    else:
        await interaction.response.send_message("คุณยังไม่ได้เอาผมเข้าช่องดิสเลย!")

# ตรงนี้เป็นcommandเล่นเพลง
@client.tree.command(name="play",description="Make the bot play a song.")
async def play(interaction: discord.Interaction, url: str):
    try:
        await interaction.response.defer()
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'noplaylist': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info['title']
        
        vc = interaction.guild.voice_client

        if not vc:
            channel = interaction.user.voice.channel
            vc = await channel.connect()

        if interaction.guild.voice_client is None:
            if interaction.user.voice:
                channel = interaction.user.voice.channel
                await channel.connect()
            else:
                await interaction.followup.send("Join a voice channel first!")
                return

        if vc.is_playing():
            queue.append(url)
            await interaction.followup.send(f"Add queue: {title}")
        else:
            await play_song(interaction, url)

    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")

# ตรงนี้เป็นcommandทำให้เล่นเพลงได้แบบต่อเนื่อง
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

# อันนี้เป็นcommandเอาไว้ข้ามเพลง
@client.tree.command(name="skip",description="Skip the current song.")
async def skip(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("ยังไม่ได้เช้าช่องดิสเลยนะ :P")
        return

    if interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop() 
    else:
        await interaction.response.send_message("ไม่มีเพลงให้ข้ามนะ :D")

@client.tree.command(name="coding",description="Show a coding question.")
async def send_botton(interaction: discord.Interaction):
    button1 = Button(label="Level 1", style=discord.ButtonStyle.green)
    button1.callback = button1_callback

    
    button2 = Button(label="Level 2", style=discord.ButtonStyle.grey)
    button2.callback = button2_callback

    # Create a view to hold the button
    view = View()
    view.add_item(button1)
    view.add_item(button2)

    # Send a message with the button
    await interaction.response.send_message("You can click the button dai na ja :P", view=view)

level_1_questions = data["level 1"]
level_2_questions = data["level 2"]
random_question1 = random.choice(level_1_questions)
random_question2 = random.choice(level_2_questions)

# ตรงนี้เป็นcommandเอาไว้สุ่มข้อความ
async def button1_callback(interaction: discord.Interaction):
    random_question1 = random.choice(level_1_questions)
    question_text1 = random_question1.get("question", "No question found!")
    input_text1 = random_question1.get("input", "No input found!")
    output_text1 = random_question1.get("output", "No output found!")

    await interaction.response.send_message(f"**Question:** \n{question_text1} \n**input:** \n{input_text1} \n**output:** \n{output_text1}")

async def button2_callback(interaction: discord.Interaction):
    random_question2 = random.choice(level_2_questions)
    question_text2 = random_question2.get("question", "No question found!")
    input_text2 = random_question2.get("input", "No input found!")
    output_text2 = random_question2.get("output", "No output found!")

    await interaction.response.send_message(f"**Question:** \n{question_text2} \n**input:** \n{input_text2} \n**output:** \n{output_text2}")

client.run(token)
