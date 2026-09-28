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
    print(f"Logged in as {client.user}")

@tree.command(name="ping", description="Replies with pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong!")

@client.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        if message.author == client.user:
            return
        print(f"DM from {message.author}: {message.content}")
        await message.channel.send("Hello! 👋")


client.run(TOKEN)