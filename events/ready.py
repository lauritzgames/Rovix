import discord

async def setup(client):
    @client.event
    async def on_ready():
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands")

        await client.change_presence(
            activity=discord.Game(name="https://rovixy.lauritz.games")
        )
        print(f"Logged in as {client.user}")