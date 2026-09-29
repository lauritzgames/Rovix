import discord
from discord import app_commands

from core import guild_config, save_data


logs = app_commands.Group(name="logs", description="Configure Rovix logging")


async def setup(client):
    client.tree.add_command(logs)

    async def set_event(interaction, event, enabled):
        guild_config(interaction.guild.id)["logging"]["events"][event] = enabled == "true"
        await save_data()
        state = "enabled" if enabled == "true" else "disabled"
        await interaction.response.send_message(f"✅ {event.title()} logging {state}.", ephemeral=True)

    @logs.command(name="setup", description="Set the logging channel")
    @app_commands.describe(channel="Text channel for logs")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup_logs(interaction: discord.Interaction, channel: discord.TextChannel):
        guild_config(interaction.guild.id)["logging"]["channel_id"] = channel.id
        await save_data()
        await interaction.response.send_message(f"✅ Log channel set to {channel.mention}.", ephemeral=True)

    @logs.command(name="messages", description="Toggle message logs")
    @app_commands.choices(enabled=[app_commands.Choice(name="Enabled", value="true"), app_commands.Choice(name="Disabled", value="false")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def messages(interaction: discord.Interaction, enabled: str):
        await set_event(interaction, "messages", enabled)

    @logs.command(name="moderation", description="Toggle moderation logs")
    @app_commands.choices(enabled=[app_commands.Choice(name="Enabled", value="true"), app_commands.Choice(name="Disabled", value="false")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def moderation(interaction: discord.Interaction, enabled: str):
        await set_event(interaction, "moderation", enabled)

    @logs.command(name="channels", description="Toggle channel logs")
    @app_commands.choices(enabled=[app_commands.Choice(name="Enabled", value="true"), app_commands.Choice(name="Disabled", value="false")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def channels(interaction: discord.Interaction, enabled: str):
        await set_event(interaction, "channels", enabled)

    @logs.command(name="roles", description="Toggle role logs")
    @app_commands.choices(enabled=[app_commands.Choice(name="Enabled", value="true"), app_commands.Choice(name="Disabled", value="false")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def roles(interaction: discord.Interaction, enabled: str):
        await set_event(interaction, "roles", enabled)

    @logs.command(name="members", description="Toggle member logs")
    @app_commands.choices(enabled=[app_commands.Choice(name="Enabled", value="true"), app_commands.Choice(name="Disabled", value="false")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def members(interaction: discord.Interaction, enabled: str):
        await set_event(interaction, "members", enabled)

    @logs.command(name="voice", description="Toggle voice logs")
    @app_commands.choices(enabled=[app_commands.Choice(name="Enabled", value="true"), app_commands.Choice(name="Disabled", value="false")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def voice(interaction: discord.Interaction, enabled: str):
        await set_event(interaction, "voice", enabled)

    @logs.command(name="server", description="Toggle server logs")
    @app_commands.choices(enabled=[app_commands.Choice(name="Enabled", value="true"), app_commands.Choice(name="Disabled", value="false")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def server(interaction: discord.Interaction, enabled: str):
        await set_event(interaction, "server", enabled)
