import re

import discord
from discord import app_commands

from serverTemplates.simple import TEMPLATE as SIMPLE
from serverTemplates.gaming import TEMPLATE as GAMING
from serverTemplates.community import TEMPLATE as COMMUNITY
from serverTemplates.support import TEMPLATE as SUPPORT
from serverTemplates.creator import TEMPLATE as CREATOR
from serverTemplates.study import TEMPLATE as STUDY
from serverTemplates.clan import TEMPLATE as CLAN
from commands.tickets import configure_tickets, send_ticket_panel

TEMPLATES = {
    "simple": SIMPLE,
    "gaming": GAMING,
    "community": COMMUNITY,
    "support": SUPPORT,
    "creator": CREATOR,
    "study": STUDY,
    "clan": CLAN,
}

CATEGORY_MARKER = re.compile(r"-\(;([a-zA-Z0-9_-]+);\)-")
CHANNEL_MARKER = re.compile(r"-\(:([a-zA-Z0-9_-]+):\)-")
ROLE_MARKER = re.compile(r"-\(\^([a-zA-Z0-9_-]+)\^\)-")
CHANNEL_REFERENCE = re.compile(r"<#-\(:([a-zA-Z0-9_-]+):\)->")
ROLE_REFERENCE = re.compile(r"<@&\(:([a-zA-Z0-9_-]+):\)->")


def replace_references(value, channels, roles, categories=None):
    categories = categories or {}

    def category_replace(match):
        item = categories.get(match.group(1))
        return item.mention if item else match.group(0)

    def channel_replace(match):
        item = channels.get(match.group(1))
        return item.mention if item else match.group(0)

    def role_replace(match):
        item = roles.get(match.group(1))
        return item.mention if item else match.group(0)

    value = CHANNEL_REFERENCE.sub(channel_replace, value)
    value = ROLE_REFERENCE.sub(role_replace, value)
    value = CATEGORY_MARKER.sub(category_replace, value)
    value = CHANNEL_MARKER.sub(channel_replace, value)
    return ROLE_MARKER.sub(role_replace, value)


def resolve_template_reference(token, channels, categories, roles):
    token = token.strip()

    channel_match = CHANNEL_MARKER.fullmatch(token)
    category_match = CATEGORY_MARKER.fullmatch(token)
    role_match = ROLE_MARKER.fullmatch(token)

    if channel_match:
        return channels.get(channel_match.group(1))
    if category_match:
        return categories.get(category_match.group(1))
    if role_match:
        return roles.get(role_match.group(1))

    return None


async def run_template_command(command, channel, guild, channels, categories, roles):
    command = command.strip()
    parts = command.split()
    if not parts:
        return "empty"

    action = parts[0].lower()
    subaction = parts[1].lower() if len(parts) > 1 else ""

    if action == "ticket" and subaction == "setup":
        category = None
        support_role = None

        for part in parts[2:]:
            resolved = resolve_template_reference(part, channels, categories, roles)
            if isinstance(resolved, discord.CategoryChannel):
                category = resolved
            elif isinstance(resolved, discord.Role):
                support_role = resolved
            elif isinstance(resolved, discord.TextChannel) and category is None:
                category = resolved.category

        if not isinstance(category, discord.CategoryChannel):
            raise RuntimeError(f"ticket setup could not resolve category from: {command}")
        if not isinstance(support_role, discord.Role):
            raise RuntimeError(f"ticket setup could not resolve support role from: {command}")

        await configure_tickets(guild, category, support_role)
        return "ticket setup"

    if action == "ticket" and subaction == "panel":
        if not isinstance(channel, discord.TextChannel):
            raise RuntimeError("ticket panel requires a text channel")
        await send_ticket_panel(channel)
        return "ticket panel"

    raise RuntimeError(f"unsupported template command: {command}")


async def resolve_role(guild, key, roles):
    if key in roles:
        return roles[key]
    return discord.utils.find(
        lambda item: item.name.lower() == key.lower(),
        guild.roles
    )


async def create_template_roles(guild, template):
    roles = {}
    for role_data in template.get("roles", []):
        role = await resolve_role(guild, role_data["id"], roles)
        if role is None:
            permissions = discord.Permissions.none()
            for permission in role_data.get("permissions", []):
                if hasattr(permissions, permission):
                    setattr(permissions, permission, True)
            role = await guild.create_role(
                name=role_data["name"],
                permissions=permissions,
                colour=discord.Colour(role_data.get("color", 0)),
                hoist=role_data.get("hoist", False),
                mentionable=role_data.get("mentionable", False),
                reason="Rovix server template"
            )
        roles[role_data["id"]] = role
    return roles


async def apply_permissions(channel, settings, guild, roles):
    if settings == "public":
        return
    if settings == "private":
        await channel.set_permissions(
            guild.default_role,
            view_channel=False,
            reason="Rovix server template"
        )
        return
    if not isinstance(settings, dict):
        return

    for target, overwrite in settings.items():
        role = guild.default_role if target in ("public", "everyone") else await resolve_role(guild, target, roles)
        if role and isinstance(overwrite, dict):
            await channel.set_permissions(
                role,
                reason="Rovix server template",
                **overwrite
            )


async def configure_channel(channel, data):
    if isinstance(channel, discord.TextChannel):
        edits = {}
        if "topic" in data:
            edits["topic"] = data["topic"]
        if "slowmode_delay" in data:
            edits["slowmode_delay"] = data["slowmode_delay"]
        if "nsfw" in data:
            edits["nsfw"] = data["nsfw"]
        if edits:
            await channel.edit(reason="Rovix server template", **edits)

    if isinstance(channel, discord.VoiceChannel):
        edits = {}
        for key in ("bitrate", "user_limit", "rtc_region"):
            if key in data:
                edits[key] = data[key]
        if edits:
            await channel.edit(reason="Rovix server template", **edits)


async def apply_template(guild, template):
    existing = await guild.fetch_channels()

    for channel in existing:
        if not isinstance(channel, discord.CategoryChannel):
            try:
                await channel.delete(reason="Rovix server template replacement")
            except discord.HTTPException:
                pass

    for category in existing:
        if isinstance(category, discord.CategoryChannel):
            try:
                await category.delete(reason="Rovix server template replacement")
            except discord.HTTPException:
                pass

    roles = await create_template_roles(guild, template)
    created_channels = {}
    created_categories = {}
    pending_messages = []
    pending_commands = []
    message_count = 0
    command_count = 0
    errors = []

    for category_data in template["categories"]:
        try:
            category = await guild.create_category(
                category_data["name"],
                reason="Rovix server template"
            )
            category_id = category_data.get("id")
            if category_id:
                created_categories[category_id] = category

            if category_data.get("permissions"):
                await apply_permissions(
                    category,
                    category_data["permissions"],
                    guild,
                    roles
                )

            for channel_data in category_data["channels"]:
                try:
                    channel_type = channel_data["type"]
                    if channel_type == "text":
                        channel = await guild.create_text_channel(
                            channel_data["name"],
                            category=category,
                            reason="Rovix server template"
                        )
                    elif channel_type == "voice":
                        channel = await guild.create_voice_channel(
                            channel_data["name"],
                            category=category,
                            reason="Rovix server template"
                        )
                    elif channel_type == "stage":
                        channel = await guild.create_stage_channel(
                            channel_data["name"],
                            category=category,
                            reason="Rovix server template"
                        )
                    elif channel_type == "forum":
                        channel = await guild.create_forum(
                            channel_data["name"],
                            category=category,
                            reason="Rovix server template"
                        )
                    else:
                        continue

                    channel_id = channel_data.get("id")
                    if channel_id:
                        created_channels[channel_id] = channel

                    await configure_channel(channel, channel_data)
                    await apply_permissions(
                        channel,
                        channel_data.get("permissions", "public"),
                        guild,
                        roles
                    )

                    if channel_type in ("text", "forum"):
                        for message in channel_data.get("messages", []):
                            pending_messages.append((channel, message))

                    for command in channel_data.get("commands", []):
                        pending_commands.append((channel, command))
                except Exception as exc:
                    errors.append(f"{category_data['name']} / {channel_data.get('name', 'unknown')}: {exc}")
        except Exception as exc:
            errors.append(f"Category {category_data.get('name', 'unknown')}: {exc}")

    for channel, message in pending_messages:
        try:
            message = replace_references(
                message,
                created_channels,
                roles,
                created_categories
            )
            if isinstance(channel, discord.ForumChannel):
                await channel.create_thread(
                    name="Template Post",
                    content=message
                )
            else:
                await channel.send(message)
            message_count += 1
        except Exception as exc:
            errors.append(f"Message in {channel.mention}: {exc}")

    for channel, command in pending_commands:
        try:
            await run_template_command(
                command,
                channel,
                guild,
                created_channels,
                created_categories,
                roles
            )
            command_count += 1
        except Exception as exc:
            errors.append(f"Command '{command}' in {channel.mention}: {exc}")

    return {
        "channels": len(created_channels),
        "categories": len(created_categories),
        "roles": len(roles),
        "messages": message_count,
        "commands": command_count,
        "errors": errors,
    }


async def setup(client):
    choices = [
        app_commands.Choice(name=data["name"], value=key)
        for key, data in TEMPLATES.items()
    ]

    @client.tree.command(
        name="template",
        description="Setup the server with a server template"
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(template="Choose a server template")
    @app_commands.choices(template=choices)
    async def template(
        interaction: discord.Interaction,
        template: app_commands.Choice[str]
    ):
        await interaction.response.defer()
        selected = TEMPLATES[template.value]
        result = await apply_template(interaction.guild, selected)

        description = (
            f"**{selected['name']} template applied.**\\n"
            f"Categories: {result['categories']}\\n"
            f"Channels: {result['channels']}\\n"
            f"Roles: {result['roles']}\\n"
            f"Messages sent: {result['messages']}\\n"
            f"Template actions executed: {result['commands']}"
        )

        if result["errors"]:
            description += f"\\n\\n⚠️ Errors: {len(result['errors'])}"
            description += "\\n" + "\\n".join(result["errors"][:5])

        await interaction.followup.send(description)
