import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv("stack.env")

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not configured in stack.env")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


async def load_extensions():
    for folder in ("commands", "events"):
        path = f"./{folder}"
        for filename in sorted(os.listdir(path)):
            if filename.endswith(".py") and not filename.startswith("_"):
                await client.load_extension(f"{folder}.{filename[:-3]}")


async def main():
    async with client:
        await load_extensions()
        await client.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
