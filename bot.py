import os
import discord
from dotenv import load_dotenv

load_dotenv("stack.env")

TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(
        activity=discord.Game(name="https://rovixy.lauritz.games")
    )
    print(f"Logged in as {client.user}")

@tree.command(name="ping", description="Replies with pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong!")

@tree.command(name="setup", description="Helps you setup server")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("""
    # **Setup Guide**
1. to setup please visit the site **https://rovix.lauritz.games**
2. **login** and find the server you want to **setup**
3. now you can **setup** it and edit it

**for more click [here](https://rovix.lauritz.games)**
""", ephemeral=True)

@tree.command(name="template", description="Setup server with simple template")
async def ping(interaction: discord.Interaction):
    categoryA = await interaction.guild.create_category("❗IMPORTANT❗")
    await interaction.guild.create_text_channel("📣Announcements", category=categoryA)

@client.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        if message.author == client.user:
            return
        print(f"DM from {message.author}: {message.content}")
        await message.channel.send("Hello! 👋")


client.run(TOKEN)