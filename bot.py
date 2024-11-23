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
from discord import utils

queue = []

load_dotenv('Token.env')
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

client = commands.Bot(command_prefix='!', intents=intents)

with open('quest.json', 'r') as file:
    data = json.load(file)

role_message_id = None
emoji_to_role = {
    "✅": "Verified"
}

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.tree.sync()

@client.event
async def on_guild_join(guild):
    embed = discord.Embed(
        title=f"สวัสดีจ้าาา เรา คือ {client.user.name} นะะ",
        description="เราเป็นบอทเพื่อช่วยคนที่สนใจเกี่ยวกับการเรียนโค้ดได้ใช้งานสะดวกมากขึ้น และเรายังมี features หลายๆอย่างรองรับการใช้งานอีกด้วย \nถ้าอยากรู้ว่าเราทำไรได้บ้างลองใช้คำสั่ง **/help** ได้เลยนะะ :D",
        color=discord.Color.green(),
    )
    embed.add_field(
        name=f"ขอบคุณที่เอา {client.user.name} เข้ามาใน sever ด้วยนะครับ",
        value="ถ้าบอทมีปัญหาหรือมีการทำงานที่แปลกไป สามารถแจ้งกับ jeng_7 เพื่อที่นำไปปรับปรุงและแก้ไข",
        inline=False,
    )

    embed.set_footer(text="Release Date: November 20, 2024")

    # Find a suitable text channel to send the message
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            print(f"Sending intro message to heheha")
            await channel.send(embed=embed)
            break

'''
รอแก้งาน
'''
# @client.command(name="role")
# async def reaction_role(ctx):
#     global role_message_id
#     message = await ctx.send(
#         "React to this message to get a role!\n"
#         "✅ for Verified"
#     )

#     # Add reaction to the message
#     await message.add_reaction("✅")
#     role_message_id = message.id
#     print(f"Role message ID is set to {role_message_id}")

# @client.event
# async def on_raw_reaction_add(payload):
#     global role_message_id
    
#     # Ensure the reaction is from the correct message
#     if payload.message_id != role_message_id:
#         return
    
#     guild = client.get_guild(payload.guild_id)
#     if guild is None:
#         return  # Bot is not in the guild
    
#     member = guild.get_member(payload.user_id)
#     if member is None or member.bot:
#         return  # Ignore bots or invalid members
    
#     emoji = str(payload.emoji)
#     role_name = emoji_to_role.get(emoji)
#     if role_name is None:
#         return  # No role associated with this emoji
    
#     # Get or create the role
#     role = discord.utils.get(guild.roles, name=role_name)
#     if role is None:
#         # If role doesn't exist, create it
#         role = await guild.create_role(name=role_name)
#         print(f"Created role {role.name}")
    
#     # Add the role to the member
#     try:
#         await member.add_roles(role)
#         print(f"Assigned {role.name} to {member.display_name}")
#     except discord.Forbidden:
#         print(f"Permission error: Can't assign role to {member.display_name}")
#     except discord.HTTPException as e:
#         print(f"Failed to assign role: {e}")

@client.tree.command(name="help",description="Show functions that bot can do.")
# command เอาไว้แสดงว่าบอทตัวนี้ทำอะไรได้บ้าง
async def help(interaction: discord.Interaction):
    view = View()

    embed = discord.Embed(
        title="Bot for coding version 0",
        color=discord.Color.blue(),
    )
    embed.add_field(
        name="Features",
        value="**/coding** \nDescription: Show a coding question.\n **/join** \nDescription: Make the bot join your voice channel.\n **/leave** \nDescription: Make the bot leave your voice channel.\n **/play** \nDescription: Make the bot play a song.\n **/skip** \nDescription: Skip the current song.",
        inline=False,
    )
    
    embed.set_footer(text="Release Date: November 20, 2024")

    await interaction.response.send_message(embed=embed, view=view)

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

    view = View()
    view.add_item(button1)
    view.add_item(button2)

    embed = discord.Embed(
        title="Bot for coding version 0",
        description="This is a bot for learning code in discord,but we didn't finish yet, so we will add more features in the future.",
        color=discord.Color.blue(),
    )
    embed.add_field(
        name="Features",
        value="**/coding** Description: Show a coding question.\n **/join** \n **/leave** \n **/play** \n **/skip**",
        inline=False,
    )
    embed.add_field(
        name="Bug Fixes",
        value="- Resolved interaction timeout issues.\n- Improved randomization logic.",
        inline=False,
    )
    embed.set_footer(text="Release Date: November 19, 2024")

    # Send patch notes and buttons
    await interaction.response.send_message(embed=embed, view=view)

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
