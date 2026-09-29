import io

import discord
from discord import app_commands

from core import create_text_channel, find_ticket_for_user, guild_config, save_data, send_log, ticket_owner_id


ticket = app_commands.Group(name="ticket", description="Manage Rovix support tickets")


def ticket_config(guild):
    config = guild_config(guild.id)["tickets"]
    config.setdefault("category_id", None)
    config.setdefault("support_role_id", None)
    config.setdefault("logs_channel_id", None)
    config.setdefault("panel_channel_id", None)
    return config


async def send_ticket_log(guild, title, description, colour=None):
    config = ticket_config(guild)
    channel = guild.get_channel(config.get("logs_channel_id"))
    if not isinstance(channel, discord.TextChannel):
        return
    embed = discord.Embed(
        title=title,
        description=description[:4000],
        colour=colour or discord.Colour.blurple(),
        timestamp=discord.utils.utcnow()
    )
    try:
        await channel.send(embed=embed)
    except discord.HTTPException:
        pass


async def configure_tickets(guild, category=None, support_role=None, logs_channel=None, panel_channel=None):
    config = ticket_config(guild)
    if category is not None:
        config["category_id"] = category.id
    if support_role is not None:
        config["support_role_id"] = support_role.id
    if logs_channel is not None:
        config["logs_channel_id"] = logs_channel.id
    if panel_channel is not None:
        config["panel_channel_id"] = panel_channel.id
    await save_data()


async def get_or_create_setup(guild, category=None, support_role=None):
    config = ticket_config(guild)
    if not isinstance(category, discord.CategoryChannel):
        category = guild.get_channel(config.get("category_id"))
    if not isinstance(category, discord.CategoryChannel):
        category = await guild.create_category("🎫 TICKETS", reason="Rovix ticket setup")
        config["category_id"] = category.id

    if not isinstance(support_role, discord.Role):
        support_role = guild.get_role(config.get("support_role_id"))
    if not isinstance(support_role, discord.Role):
        support_role = discord.utils.get(guild.roles, name="Support")
    if not isinstance(support_role, discord.Role):
        support_role = await guild.create_role(name="Support", reason="Rovix ticket setup")
    config["support_role_id"] = support_role.id

    return category, support_role


async def create_ticket(interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("❌ Tickets can only be used inside a server.", ephemeral=True)
        return

    existing = find_ticket_for_user(guild, interaction.user.id)
    if existing:
        await interaction.response.send_message(f"🎫 You already have {existing.mention}.", ephemeral=True)
        return

    config = ticket_config(guild)
    category = guild.get_channel(config.get("category_id"))
    support_role = guild.get_role(config.get("support_role_id"))
    if not isinstance(category, discord.CategoryChannel) or not isinstance(support_role, discord.Role):
        await interaction.response.send_message("❌ Tickets are not configured yet. Ask a server manager to run the ticket setup command.", ephemeral=True)
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    }

    await interaction.response.defer(ephemeral=True)
    channel = await create_text_channel(
        guild,
        f"ticket-{interaction.user.name}",
        category=category,
        overwrites=overwrites,
        topic=f"rovix-ticket:{interaction.user.id}"
    )

    await channel.send(
        f"{support_role.mention} {interaction.user.mention} opened a support ticket.\n\n"
        "Use the buttons below to close the ticket when the issue is resolved.",
        view=TicketControlsView()
    )

    await send_ticket_log(guild, "🎫 Ticket Created", f"{channel.mention} was opened by {interaction.user.mention}.")
    await send_log(guild, "Ticket Created", f"{channel.mention} was opened for {interaction.user.mention}.", "server", discord.Colour.green())
    await interaction.followup.send(f"✅ Ticket created: {channel.mention}", ephemeral=True)


class CloseReasonModal(discord.ui.Modal, title="Close Ticket"):
    reason = discord.ui.TextInput(
        label="Close reason",
        placeholder="Why is this ticket being closed?",
        required=True,
        max_length=1000,
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction):
        await close_ticket(interaction, str(self.reason))


class TicketControlsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="rovix:ticket:close:reason")
    async def close_with_reason(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await can_close(interaction):
            return
        await interaction.response.send_modal(CloseReasonModal())

    @discord.ui.button(label="Close Without Reason", style=discord.ButtonStyle.secondary, emoji="🔒", custom_id="rovix:ticket:close:none")
    async def close_without_reason(self, interaction: discord.Interaction, button: discord.ui.Button):
        await close_ticket(interaction, "No reason provided.")


async def can_close(interaction):
    channel = interaction.channel
    owner_id = ticket_owner_id(channel) if isinstance(channel, discord.TextChannel) else None
    if owner_id is None:
        await interaction.response.send_message("❌ This is not a Rovix ticket.", ephemeral=True)
        return False
    config = ticket_config(interaction.guild)
    role = interaction.guild.get_role(config.get("support_role_id"))
    allowed = interaction.user.id == owner_id or interaction.user.guild_permissions.manage_channels or (role is not None and role in interaction.user.roles)
    if not allowed:
        await interaction.response.send_message("❌ You cannot close this ticket.", ephemeral=True)
        return False
    return True


async def close_ticket(interaction, reason):
    if not await can_close(interaction):
        return
    channel = interaction.channel
    owner_id = ticket_owner_id(channel)
    await interaction.response.defer(ephemeral=True)
    owner = interaction.guild.get_member(owner_id)
    config = ticket_config(interaction.guild)
    support_role = interaction.guild.get_role(config.get("support_role_id"))
    if owner:
        await channel.set_permissions(owner, view_channel=True, send_messages=False)
    if support_role:
        await channel.set_permissions(support_role, view_channel=True, send_messages=False, read_message_history=True)
    await channel.edit(name=f"closed-{channel.name.removeprefix('ticket-').removeprefix('closed-')}"[:100])
    await channel.send(f"🔒 Ticket closed by {interaction.user.mention}.\n**Reason:** {reason}")
    await send_ticket_log(interaction.guild, "🔒 Ticket Closed", f"{channel.mention} was closed by {interaction.user.mention}.\n**Reason:** {reason}", discord.Colour.orange())
    await send_log(interaction.guild, "Ticket Closed", f"{channel.mention} was closed by {interaction.user.mention}. Reason: {reason}", "server", discord.Colour.orange())
    await interaction.followup.send("🔒 Ticket closed.", ephemeral=True)


async def send_ticket_panel(channel):
    if not isinstance(channel, discord.TextChannel):
        raise RuntimeError("Ticket panels can only be sent to text channels.")
    embed = discord.Embed(title="🎫 Support Tickets", description="Need help? Click the button below to create a private ticket.", colour=discord.Colour.blurple())
    await channel.send(embed=embed, view=TicketPanelView())


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green, emoji="🎫", custom_id="rovix:ticket:create")
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction)


async def setup(client):
    client.tree.add_command(ticket)
    client.add_view(TicketPanelView())
    client.add_view(TicketControlsView())

    @ticket.command(name="setup", description="Create and configure the complete ticket system")
    @app_commands.describe(category="Existing ticket category", support_role="Existing support role", logs_channel="Existing ticket log channel", panel_channel="Existing ticket panel channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ticket(
        interaction: discord.Interaction,
        category: discord.CategoryChannel | None = None,
        support_role: discord.Role | None = None,
        logs_channel: discord.TextChannel | None = None,
        panel_channel: discord.TextChannel | None = None
    ):
        await interaction.response.defer(ephemeral=True)
        config = ticket_config(interaction.guild)
        category, support_role = await get_or_create_setup(interaction.guild, category, support_role)

        if not isinstance(logs_channel, discord.TextChannel):
            logs_channel = interaction.guild.get_channel(config.get("logs_channel_id"))
        if not isinstance(logs_channel, discord.TextChannel):
            logs_category = discord.utils.get(interaction.guild.categories, name="🔒 LOGS")
            if logs_category is None:
                logs_category = await interaction.guild.create_category("🔒 LOGS", reason="Rovix ticket setup")
            logs_channel = await interaction.guild.create_text_channel("ticket-logs", category=logs_category, reason="Rovix ticket setup")
            await logs_channel.set_permissions(interaction.guild.default_role, view_channel=False)
            await logs_channel.set_permissions(support_role, view_channel=True, read_message_history=True)
            config["logs_channel_id"] = logs_channel.id

        if not isinstance(panel_channel, discord.TextChannel):
            panel_channel = interaction.guild.get_channel(config.get("panel_channel_id"))
        if not isinstance(panel_channel, discord.TextChannel):
            panel_channel = await interaction.guild.create_text_channel("ticket-panel", reason="Rovix ticket setup")
            await panel_channel.set_permissions(interaction.guild.default_role, view_channel=True, send_messages=False, read_message_history=True)
            config["panel_channel_id"] = panel_channel.id

        config["category_id"] = category.id
        config["support_role_id"] = support_role.id
        await save_data()
        await send_ticket_panel(panel_channel)
        await interaction.followup.send(
            f"✅ Ticket system ready.\n🎫 Category: {category.name}\n🛡️ Support: {support_role.mention}\n📋 Logs: {logs_channel.mention}\n📌 Panel: {panel_channel.mention}",
            ephemeral=True
        )
    @ticket.command(name="panel", description="Send the ticket creation panel")
    @app_commands.describe(channel="Channel where the panel should be sent")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(interaction: discord.Interaction, channel: discord.TextChannel | None = None):
        target = channel or interaction.channel
        await send_ticket_panel(target)
        await interaction.response.send_message("✅ Ticket panel sent.", ephemeral=True)

    @ticket.command(name="create", description="Create a private support ticket")
    async def create(interaction):
        await create_ticket(interaction)

    @ticket.command(name="close", description="Close the current ticket with an optional reason")
    @app_commands.describe(reason="Optional close reason")
    async def close(interaction: discord.Interaction, reason: str | None = None):
        await close_ticket(interaction, reason or "No reason provided.")

    @ticket.command(name="delete", description="Delete the current ticket")
    @app_commands.checks.has_permissions(administrator=True)
    async def delete(interaction):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or ticket_owner_id(channel) is None:
            await interaction.response.send_message("❌ This is not a Rovix ticket.", ephemeral=True)
            return
        name = channel.name
        await send_ticket_log(interaction.guild, "🗑️ Ticket Deleted", f"{channel.mention} was deleted by {interaction.user.mention}.", discord.Colour.red())
        await channel.delete(reason=f"Ticket deleted by {interaction.user}")

    @ticket.command(name="add", description="Add a member to the current ticket")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(member="Member to add")
    async def add(interaction, member: discord.Member):
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
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(member="Member to remove")
    async def remove(interaction, member: discord.Member):
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
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(name="New ticket name")
    async def rename(interaction, name: str):
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
    @app_commands.checks.has_permissions(administrator=True)
    async def transcript(interaction):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or ticket_owner_id(channel) is None:
            await interaction.response.send_message("❌ This is not a Rovix ticket.", ephemeral=True)
            return
        owner_id = ticket_owner_id(channel)
        config = ticket_config(interaction.guild)
        role = interaction.guild.get_role(config.get("support_role_id"))
        allowed = interaction.user.id == owner_id or interaction.user.guild_permissions.manage_channels or (role is not None and role in interaction.user.roles)
        if not allowed:
            await interaction.response.send_message("❌ You cannot create this transcript.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        lines = [f"Rovix transcript: {channel.name}", ""]
        async for message in channel.history(limit=None, oldest_first=True):
            lines.append(f"[{message.created_at.isoformat()}] {message.author} ({message.author.id}): {message.content}")
            for attachment in message.attachments:
                lines.append(f"Attachment: {attachment.url}")
        file = discord.File(io.BytesIO("\n".join(lines).encode("utf-8", "replace")), filename=f"{channel.name}-transcript.txt")
        await interaction.followup.send("📄 Transcript created.", file=file, ephemeral=True)

    @ticket.command(name="settings", description="View ticket configuration")
    @app_commands.checks.has_permissions(administrator=True)
    async def settings(interaction):
        config = ticket_config(interaction.guild)
        category = interaction.guild.get_channel(config.get("category_id"))
        role = interaction.guild.get_role(config.get("support_role_id"))
        logs_channel = interaction.guild.get_channel(config.get("logs_channel_id"))
        panel_channel = interaction.guild.get_channel(config.get("panel_channel_id"))
        embed = discord.Embed(title="Rovix Tickets", colour=discord.Colour.blurple())
        embed.add_field(name="Category", value=category.name if category else "Not configured")
        embed.add_field(name="Support role", value=role.mention if role else "Not configured")
        embed.add_field(name="Logs", value=logs_channel.mention if logs_channel else "Not configured")
        embed.add_field(name="Panel", value=panel_channel.mention if panel_channel else "Not configured")
        await interaction.response.send_message(embed=embed, ephemeral=True)
