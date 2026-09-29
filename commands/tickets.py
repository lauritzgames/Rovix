import io

import discord
from discord import app_commands

from core import create_text_channel, find_ticket_for_user, guild_config, save_data, send_log, ticket_owner_id


ticket = app_commands.Group(name="ticket", description="Manage Rovix support tickets")


async def setup(client):
    client.tree.add_command(ticket)

    @ticket.command(name="setup", description="Configure ticket category and support role")
    @app_commands.describe(category="Category for tickets", support_role="Support role")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup_ticket(interaction: discord.Interaction, category: discord.CategoryChannel | None = None, support_role: discord.Role | None = None):
        config = guild_config(interaction.guild.id)["tickets"]
        if category:
            config["category_id"] = category.id
        if support_role:
            config["support_role_id"] = support_role.id
        await save_data()
        await interaction.response.send_message("✅ Ticket configuration saved.", ephemeral=True)

    @ticket.command(name="create", description="Create a private support ticket")
    async def create(interaction: discord.Interaction):
        guild = interaction.guild
        existing = find_ticket_for_user(guild, interaction.user.id)
        if existing:
            await interaction.response.send_message(f"🎫 You already have {existing.mention}.", ephemeral=True)
            return
        config = guild_config(guild.id)["tickets"]
        category = guild.get_channel(config.get("category_id")) if config.get("category_id") else None
        if not isinstance(category, discord.CategoryChannel):
            category = await guild.create_category("🎫 TICKETS", reason="Rovix ticket setup")
            config["category_id"] = category.id
            await save_data()
        role_id = config.get("support_role_id")
        support_role = guild.get_role(role_id) if role_id else None
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        await interaction.response.defer(ephemeral=True)
        channel = await create_text_channel(
            guild,
            f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites,
            topic=f"rovix-ticket:{interaction.user.id}"
        )
        await channel.send(f"🎫 Welcome {interaction.user.mention}. A support member will help you here.")
        await send_log(guild, "Ticket Created", f"{channel.mention} was opened for {interaction.user.mention}.", "server", discord.Colour.green())
        await interaction.followup.send(f"✅ Ticket created: {channel.mention}", ephemeral=True)

    @ticket.command(name="close", description="Close the current ticket")
    async def close(interaction: discord.Interaction):
        channel = interaction.channel
        owner_id = ticket_owner_id(channel) if isinstance(channel, discord.TextChannel) else None
        if owner_id is None:
            await interaction.response.send_message("❌ This is not a Rovix ticket.", ephemeral=True)
            return
        config = guild_config(interaction.guild.id)["tickets"]
        role = interaction.guild.get_role(config.get("support_role_id")) if config.get("support_role_id") else None
        allowed = interaction.user.id == owner_id or interaction.user.guild_permissions.manage_channels or (role and role in interaction.user.roles)
        if not allowed:
            await interaction.response.send_message("❌ You cannot close this ticket.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        owner = interaction.guild.get_member(owner_id)
        if owner:
            await channel.set_permissions(owner, view_channel=True, send_messages=False)
        await channel.edit(name=f"closed-{channel.name.removeprefix('ticket-')}"[:100])
        await send_log(interaction.guild, "Ticket Closed", f"{channel.mention} was closed by {interaction.user.mention}.", "server", discord.Colour.orange())
        await interaction.followup.send("🔒 Ticket closed.", ephemeral=True)

    @ticket.command(name="delete", description="Delete the current ticket")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def delete(interaction: discord.Interaction):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or ticket_owner_id(channel) is None:
            await interaction.response.send_message("❌ This is not a Rovix ticket.", ephemeral=True)
            return
        name = channel.name
        await channel.delete(reason=f"Ticket deleted by {interaction.user}")
        await interaction.response.send_message(f"🗑️ Deleted {name}.", ephemeral=True)

    @ticket.command(name="add", description="Add a member to the current ticket")
    @app_commands.describe(member="Member to add")
    async def add(interaction: discord.Interaction, member: discord.Member):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or ticket_owner_id(channel) is None:
            await interaction.response.send_message("❌ This is not a Rovix ticket.", ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Manage Channels is required.", ephemeral=True)
            return
        await channel.set_permissions(member, view_channel=True, send_messages=True, read_message_history=True)
        await interaction.response.send_message(f"✅ Added {member.mention}.", ephemeral=True)

    @ticket.command(name="remove", description="Remove a member from the current ticket")
    @app_commands.describe(member="Member to remove")
    async def remove(interaction: discord.Interaction, member: discord.Member):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or ticket_owner_id(channel) is None:
            await interaction.response.send_message("❌ This is not a Rovix ticket.", ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Manage Channels is required.", ephemeral=True)
            return
        await channel.set_permissions(member, overwrite=None)
        await interaction.response.send_message(f"✅ Removed {member.mention}.", ephemeral=True)

    @ticket.command(name="rename", description="Rename the current ticket")
    @app_commands.describe(name="New ticket name")
    async def rename(interaction: discord.Interaction, name: str):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or ticket_owner_id(channel) is None:
            await interaction.response.send_message("❌ This is not a Rovix ticket.", ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Manage Channels is required.", ephemeral=True)
            return
        await channel.edit(name=name[:100])
        await interaction.response.send_message(f"✅ Renamed to {channel.name}.", ephemeral=True)

    @ticket.command(name="transcript", description="Create a ticket transcript")
    async def transcript(interaction: discord.Interaction):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or ticket_owner_id(channel) is None:
            await interaction.response.send_message("❌ This is not a Rovix ticket.", ephemeral=True)
            return
        owner_id = ticket_owner_id(channel)
        config = guild_config(interaction.guild.id)["tickets"]
        role = interaction.guild.get_role(config.get("support_role_id")) if config.get("support_role_id") else None
        allowed = interaction.user.id == owner_id or interaction.user.guild_permissions.manage_channels or (role and role in interaction.user.roles)
        if not allowed:
            await interaction.response.send_message("❌ You cannot create this transcript.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        lines = [f"Rovix transcript: {channel.name}", ""]
        async for message in channel.history(limit=None, oldest_first=True):
            lines.append(f"[{message.created_at.isoformat()}] {message.author} ({message.author.id}): {message.content}")
            if message.attachments:
                for attachment in message.attachments:
                    lines.append(f"Attachment: {attachment.url}")
        data = "\\n".join(lines).encode("utf-8", "replace")
        file = discord.File(io.BytesIO(data), filename=f"{channel.name}-transcript.txt")
        await interaction.followup.send("📄 Transcript created.", file=file, ephemeral=True)

    @ticket.command(name="settings", description="View ticket configuration")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def settings(interaction: discord.Interaction):
        config = guild_config(interaction.guild.id)["tickets"]
        category = interaction.guild.get_channel(config.get("category_id"))
        role = interaction.guild.get_role(config.get("support_role_id"))
        embed = discord.Embed(title="Rovix Tickets", colour=discord.Colour.blurple())
        embed.add_field(name="Category", value=category.mention if category else "Not configured")
        embed.add_field(name="Support role", value=role.mention if role else "Not configured")
        await interaction.response.send_message(embed=embed, ephemeral=True)
