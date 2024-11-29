import os
import discord
import yt_dlp
import asyncio
import random
import json
import uvicorn
import logging
import requests

from dotenv import load_dotenv
from discord.ext import commands
from discord import Interaction
from discord import FFmpegPCMAudio
from discord import app_commands
from discord.ui import Button, View
from discord import utils
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from threading import Thread
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Shared data between FastAPI and the Discord bot
api_data = {
    "status": "Bot is starting...",
    "commands": []
}

logging.basicConfig(level=logging.DEBUG)

MONGO_URI = os.getenv('MONGO_URI')
database = MongoClient(MONGO_URI)
db = database["chat"]
collection = db["commmand"]

queue = []

load_dotenv('Token.env')
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.reactions = True

client = commands.Bot(command_prefix='!', intents=intents)

with open('quest.json', 'r') as file:
    data = json.load(file)

role_message_id = None
role_name = "✅ verified"

class Item(BaseModel):
    question: Optional[str] = None  
    input: Optional[str] = None   
    output: Optional[str] = None   
    difficulty: int 

def fetch_quest_data():
    try:
        response = requests.get("https://ancient-fortress-64724-1c6507ef2f45.herokuapp.com/")
        response.raise_for_status()  
        quest_data = response.json()  
        return quest_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching quest data: {e}")
        return None

def run_fastapi():
    print("Starting FastAPI...")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    fastapi_thread = Thread(target=run_fastapi)
    fastapi_thread.start()

@app.get("/")
async def root():
    return {"message": "FastAPI is running alongside the Discord bot"}

@app.get("/bot-status")
async def bot_status():
    return {"status": api_data["status"]}

@app.get("/commands")
async def get_commands():
    return {"commands": api_data["commands"]}

@app.get("/quest-data")
async def get_quest_data():
    try:
        with open('quest.json', 'r') as file:
            data = json.load(file)
        return {"quest_data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the JSON file: {e}")

@app.get("/questions")
async def get_questions():
    questions = list(collection.find({}, {"_id": 0}))
    return {"questions": questions}

@app.post("/items/")
async def create_item(item: Item):
    # You can use the item data, which is automatically parsed from JSON
    return {"question": item.question, "input": item.input, "output": item.output, "difficulty": item.price}

@app.post("/add-command")
async def add_command(command: str):
    if command not in api_data["commands"]:
        api_data["commands"].append(command)
        return {"message": f"Command '{command}' added successfully"}
    else:
        raise HTTPException(status_code=400, detail="Command already exists")

@client.event
async def on_ready():
    api_data["status"] = f"Bot is online as {client.user}"
    api_data["commands"] = [
        "role", "help", "join", "leave", "play", "skip", "practice", "last_question"
    ]
    print(f'Logged in as {client.user}')
    await client.tree.sync()
    
@client.event
async def on_guild_join(guild):
    embed = discord.Embed(
        title=f"Hellooo I'm {client.user.name} ",
        description="I'm a bot to help people who interested in coding to use it more conveniently. And we also have many features to support the use. \n if you want  to know what we can do try using the **\help** command",
        color=discord.Color.green(),
    )
    embed.add_field(
        name=f"Thank you for inviting {client.user.name} to sever ",
        value="If the bot has any problems or malfunctions, you can report to jeng_7 for improvement and correction.",
        inline=False,
    )

    embed.set_footer(text="Release Date: November 20, 2024")

    # Find a suitable text channel to send the message
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            print(f"Sending intro message to heheha")
            await channel.send(embed=embed)
            break

@client.event
async def on_member_join(member):
    print(f"New member joined: {member.display_name}")
    # Send a welcome message in the default text channel or a specific channel
    channel = discord.utils.get(member.guild.text_channels, name='welcome')

    if channel:
        view = View()

        embed = discord.Embed(
            title=f"Welcome {member.display_name} To {member.guild.name} 👋🤓",
            description="Thanks you for joining our server! We hope you have a great time here! :D",
            color=discord.Color.blue(),
        )
        await channel.send(embed=embed, view=view)
    else:
        print("Default text channel not found.")

@client.event
async def on_raw_reaction_add(payload):
    global role_message_id
    
    # Ensure the reaction is from the correct message
    if payload.message_id != role_message_id:
        return
    
    guild = client.get_guild(payload.guild_id)
    if guild is None:
        return  # Bot is not in the guild
    
    member = guild.get_member(payload.user_id)
    if member is None or member.bot:
        return  # Ignore bots or invalid members
    
    # Get or create the role
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        # If role doesn't exist, create it
        role = await guild.create_role(name=role_name)
        print(f"Created role {role.name}")
    
    # Add the role to the member
    try:
        await member.add_roles(role)
        print(f"Assigned {role.name} to {member.display_name}")
    except discord.Forbidden:
        print(f"Permission error: Can't assign role to {member.display_name}")
    except discord.HTTPException as e:
        print(f"Failed to assign role: {e}")

async def buttonRole_callback(interaction: Interaction):
    guild = interaction.guild
    
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        role = await guild.create_role(name=role_name)
        print(f"Created role: {role.name}")

    try:
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"give role {role.name} with {interaction.user.display_name} its done🔥", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission give role to other people.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.response.send_message(f"An error occurres while granting : {e}", ephemeral=True)

# command นี้เอาไว้ให้ยศคนในดิสคอร์ด
@client.tree.command(name="role", description="Click to get a role.")
async def reaction_role(interaction: Interaction):
    global role_message_id

    buttonRole = Button(label="✅ verified", style=discord.ButtonStyle.grey)
    buttonRole.callback = buttonRole_callback

    view = View()            
    view.add_item(buttonRole)

    embed = discord.Embed(
            title="You can click the button below to get a role.",
            description="Click ✅ verified button to get a role.",
            color=discord.Color.blue(),
        )

    await interaction.response.send_message(embed=embed, view=view)

    message = await interaction.response.send_message(embed=embed, view=view)
    role_message_id = message.id
    print(f"Role message ID is set to {role_message_id}")

# command เอาไว้แสดงว่าบอทตัวนี้ทำอะไรได้บ้าง
@client.tree.command(name="help",description="Show functions that bot can do.")
async def help(interaction: discord.Interaction):
    view = View()

    embed = discord.Embed(
        title="Bot for coding version 0",
        color=discord.Color.blue(),
    )
    embed.add_field(
        name="Features",
        value="**/practice** \nDescription: Show a coding question.\n **/join** \nDescription: Make the bot join your voice channel.\n **/leave** \nDescription: Make the bot leave your voice channel.\n **/play** \nDescription: Make the bot play a song.\n **/skip** \nDescription: Skip the current song.\n **/last_question** \nDescription: Show the last question.",
        inline=False,
    )
    
    embed.set_footer(text="Release Date: November 29, 2024")

    await interaction.response.send_message(embed=embed, view=view)

# commandเอาไว้เข้า
@client.tree.command(name="join", description="Make the bot join your voice channel.")
async def join(interaction: discord.Interaction):
    if interaction.user.voice is None:
        await interaction.response.send_message("you haven't invited me to the voicechat !", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    
    await channel.connect()
    await interaction.response.send_message(f"join voice channel {channel} done!")

# commandเอาไว้ออก
@client.tree.command(name="leave",description="Make the bot leave your voice channel.")
async def leave(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await interaction.response.send_message("leave voice channel!")
    else:
        await interaction.response.send_message("You haven't invited me to join a voice channel 😫")

# ตรงนี้เป็นcommandเล่นเพลง
@client.tree.command(name="play",description="Make the bot play a song.")
async def play(interaction: discord.Interaction, url: str):
    try:
        logging.debug("Play command invoked.")
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
                client.loop.create_task(interaction.followup.send(f"No more songs in the queue,I'm leaving voice channel!"))
                client.loop.create_task(vc.disconnect())

        vc.play(FFmpegPCMAudio(audio_url), after=play_next)
        await interaction.followup.send(f"Now playing: {title}")

    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")

# อันนี้เป็นcommandเอาไว้ข้ามเพลง
@client.tree.command(name="skip",description="Skip the current song.")
async def skip(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("You haven't invited me to join a voice channel 😫")
        return

    if interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop() 
        await interaction.response.send_message("Song skipped!")
    else:
        await interaction.response.send_message("There are no songs to skip :P.") 

# อันนี้เป็นcommandเอาไว้แสดงคําถาม
@client.tree.command(name="practice",description="Show a coding question.")
async def send_botton(interaction: discord.Interaction):
    quest_data = fetch_quest_data()
    if quest_data is None:
        await interaction.response.send_message("Error fetching quest data!")
        return

    button1 = Button(label="Level 1", style=discord.ButtonStyle.green)
    button1.callback = button1_callback

    button2 = Button(label="Level 2", style=discord.ButtonStyle.grey)
    button2.callback = button2_callback

    view = View()
    view.add_item(button1)
    view.add_item(button2)

    embed = discord.Embed(
        title="Bot for coding :P",
        color=discord.Color.blue(),
    )
    embed.add_field(
        name="testing",
        value="If you find any problems or malfunctions, you can report to jeng_7 for improvement and correction and thank you for using my bot.",
        inline=False,
    )
    embed.set_footer(text="Release Date: November 29, 2024")

    await interaction.response.send_message(embed=embed, view=view)

quest_data = fetch_quest_data()

level_1_questions = quest_data["quest_data"]["level 1"]
level_2_questions = quest_data["quest_data"]["level 2"]

random_question1 = random.choice(level_1_questions)
random_question2 = random.choice(level_2_questions)

# ตรงนี้เป็นcommandเอาไว้สุ่มข้อความ
async def button1_callback(interaction: discord.Interaction):
    random_question1 = random.choice(level_1_questions)
    question_text1 = random_question1.get("question", "No question found!")
    input_text1 = random_question1.get("input", "No input found!")
    output_text1 = random_question1.get("output", "No output found!")

    data = {
        "userID": interaction.user.id,
        "username": interaction.user.display_name,
        "question": question_text1,
        "level": "Level 1",
        "timestamp": interaction.created_at.isoformat(),
    }
    collection.insert_one(data)

    await interaction.response.send_message(f"**Question:** \n{question_text1} \n**input:** \n{input_text1} \n**output:** \n{output_text1}")

async def button2_callback(interaction: discord.Interaction):
    random_question2 = random.choice(level_2_questions)
    question_text2 = random_question2.get("question", "No question found!")
    input_text2 = random_question2.get("input", "No input found!")
    output_text2 = random_question2.get("output", "No output found!")

    data = {
        "userID": interaction.user.id,
        "username": interaction.user.display_name,
        "question": question_text2,
        "level": "Level 2",
        "timestamp": interaction.created_at.isoformat(),
    }
    collection.insert_one(data)

    await interaction.response.send_message(f"**Question:** \n{question_text2} \n**input:** \n{input_text2} \n**output:** \n{output_text2}")

# command เอาไว้ดูข้อที่เราทำล่าสุด
@client.tree.command(name="last_question",description="Show functions that bot can do.")
async def collect_data(interaction: discord.Interaction):
    try:
        # Find the latest question in MongoDB for this user
        query = {"userID": interaction.user.id}
        last_question_data = collection.find_one(query, sort=[("timestamp", -1)])

        if last_question_data:
            await interaction.response.send_message(
                f"**Last Question:** \n{last_question_data['question']}\n"
                f"**Input:** \n{last_question_data['input']}\n"
                f"**Output:** \n{last_question_data['output']}"
                f"**Level:** {last_question_data['level']}\n"
                f"**Timestamp:** \n{last_question_data['timestamp']}"
            )
        else:
            await interaction.response.send_message("No previous questions found for you.")
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}")

#ใส่ discord token ของตัวเอง
client.run(token)
