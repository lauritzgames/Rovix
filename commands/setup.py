import discord
from discord import app_commands


async def setup(client):

    @client.tree.command(name="setup", description="Show the Rovix setup guide")
    async def setup_command(interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚡ Rovix Setup",
            description="Use the Rovix website to configure your server.",
            colour=discord.Colour.blurple()
        )
        embed.add_field(name="1. Open Rovix", value="Visit https://rovix.lauritz.games", inline=False)
        embed.add_field(name="2. Sign in", value="Log in with Discord and select your server.", inline=False)
        embed.add_field(name="3. Configure", value="Choose the features and settings you want.", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
