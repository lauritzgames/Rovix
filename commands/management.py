import discord
from discord import app_commands

from core import send_log


async def setup(client):

    @client.tree.command(name="lock", description="Lock the current channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(interaction: discord.Interaction):
        channel = interaction.channel
        if not isinstance(channel, discord.abc.GuildChannel):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await send_log(interaction.guild, "Channel Locked", f"{channel.mention} was locked by {interaction.user.mention}.", "channels")
        await interaction.followup.send(f"🔒 Locked {channel.mention}.", ephemeral=True)

    @client.tree.command(name="unlock", description="Unlock the current channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(interaction: discord.Interaction):
        channel = interaction.channel
        if not isinstance(channel, discord.abc.GuildChannel):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await channel.set_permissions(interaction.guild.default_role, send_messages=None)
        await send_log(interaction.guild, "Channel Unlocked", f"{channel.mention} was unlocked by {interaction.user.mention}.", "channels")
        await interaction.followup.send(f"🔓 Unlocked {channel.mention}.", ephemeral=True)

    @client.tree.command(name="clear", description="Delete recent messages")
    @app_commands.describe(amount="Number of messages to delete, from 1 to 100")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("This command requires a text channel.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount, reason=f"Clear requested by {interaction.user}")
        await send_log(interaction.guild, "Messages Cleared", f"{interaction.user.mention} deleted {len(deleted)} message(s) in {interaction.channel.mention}.", "messages", discord.Colour.orange())
        await interaction.followup.send(f"🧹 Deleted {len(deleted)} message(s).", ephemeral=True)

    @client.tree.command(name="hide", description="Hide the current channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def hide(interaction: discord.Interaction):
        channel = interaction.channel
        if not isinstance(channel, discord.abc.GuildChannel):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await channel.set_permissions(interaction.guild.default_role, view_channel=False)
        await send_log(interaction.guild, "Channel Hidden", f"{channel.mention} was hidden by {interaction.user.mention}.", "channels")
        await interaction.followup.send(f"👁️‍🗨️ Hidden {channel.mention}.", ephemeral=True)

    @client.tree.command(name="unhide", description="Unhide the current channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unhide(interaction: discord.Interaction):
        channel = interaction.channel
        if not isinstance(channel, discord.abc.GuildChannel):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await channel.set_permissions(interaction.guild.default_role, view_channel=None)
        await send_log(interaction.guild, "Channel Unhidden", f"{channel.mention} was unhidden by {interaction.user.mention}.", "channels")
        await interaction.followup.send(f"👁️ Visible again: {channel.mention}.", ephemeral=True)

    @client.tree.command(name="rename", description="Rename the current channel")
    @app_commands.describe(name="New channel name")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def rename(interaction: discord.Interaction, name: str):
        channel = interaction.channel
        if not isinstance(channel, discord.abc.GuildChannel):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        old_name = channel.name
        await channel.edit(name=name[:100], reason=f"Rename requested by {interaction.user}")
        await send_log(interaction.guild, "Channel Renamed", f"{interaction.user.mention} renamed {old_name} to {channel.name}.", "channels")
        await interaction.followup.send(f"✏️ Renamed to {channel.name}.", ephemeral=True)

    @client.tree.command(name="topic", description="Set the current text channel topic")
    @app_commands.describe(topic="New topic")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def topic(interaction: discord.Interaction, topic: str):
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("This command requires a text channel.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.edit(topic=topic[:1024], reason=f"Topic changed by {interaction.user}")
        await send_log(interaction.guild, "Channel Topic Changed", f"{interaction.user.mention} updated {interaction.channel.mention}.", "channels")
        await interaction.followup.send("📝 Channel topic updated.", ephemeral=True)

    @client.tree.command(name="movechannel", description="Move a text channel into a category")
    @app_commands.describe(channel="Text channel to move", category="Destination category")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def movechannel(interaction: discord.Interaction, channel: discord.TextChannel, category: discord.CategoryChannel):
        await interaction.response.defer(ephemeral=True)
        await channel.edit(category=category, reason=f"Channel moved by {interaction.user}")
        await send_log(interaction.guild, "Channel Moved", f"{channel.mention} was moved into {category.name} by {interaction.user.mention}.", "channels")
        await interaction.followup.send(f"📂 Moved {channel.mention} into {category.name}.", ephemeral=True)

    @client.tree.command(name="createforum", description="Create a forum channel")
    @app_commands.describe(name="Forum name", category="Optional category")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def createforum(interaction: discord.Interaction, name: str, category: discord.CategoryChannel | None = None):
        await interaction.response.defer(ephemeral=True)
        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.followup.send("❌ Rovix needs Manage Channels.", ephemeral=True)
            return
        forum = await interaction.guild.create_forum(name=name[:100], category=category, reason=f"Forum created by {interaction.user}")
        await send_log(interaction.guild, "Forum Created", f"{interaction.user.mention} created {forum.mention}.", "channels", discord.Colour.green())
        await interaction.followup.send(f"🧵 Created {forum.mention}.", ephemeral=True)
