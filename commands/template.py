import re

import discord
from discord import app_commands

from serverTemplates.simple import TEMPLATE as SIMPLE
from serverTemplates.gaming import TEMPLATE as GAMING
from serverTemplates.community import TEMPLATE as COMMUNITY


TEMPLATES = {
    "simple": SIMPLE,
    "gaming": GAMING,
    "community": COMMUNITY,
}


def replace_channel_references(
    message: str,
    channels: dict[str, discord.abc.GuildChannel]
) -> str:

    pattern = r"<#-\(:([a-zA-Z0-9_-]+):\)->"

    def replace(match):
        channel_key = match.group(1)

        channel = channels.get(channel_key)

        if channel:
            return f"<#{channel.id}>"

        return match.group(0)

    return re.sub(pattern, replace, message)


async def apply_permissions(
    channel: discord.abc.GuildChannel,
    permission_settings,
    guild: discord.Guild
):
    if permission_settings == "public":
        return

    if permission_settings == "private":
        await channel.set_permissions(
            guild.default_role,
            view_channel=False
        )
        return

    if isinstance(permission_settings, dict):

        everyone_settings = permission_settings.get("public")

        if everyone_settings:
            await channel.set_permissions(
                guild.default_role,
                **everyone_settings
            )

        staff_settings = permission_settings.get("staff")

        if staff_settings:
            staff_role = discord.utils.find(
                lambda role: role.name.lower() == "staff",
                guild.roles
            )

            if staff_role:
                await channel.set_permissions(
                    staff_role,
                    **staff_settings
                )


async def apply_template(
    guild: discord.Guild,
    template: dict
):

    for channel in await guild.fetch_channels():
        await channel.delete()

    created_channels = {}

    pending_messages = []

    for category_data in template["categories"]:

        category = await guild.create_category(
            category_data["name"]
        )

        for channel_data in category_data["channels"]:

            channel_type = channel_data["type"]

            if channel_type == "text":

                channel = await guild.create_text_channel(
                    channel_data["name"],
                    category=category
                )

            elif channel_type == "voice":

                channel = await guild.create_voice_channel(
                    channel_data["name"],
                    category=category
                )

            else:
                continue

            channel_id = channel_data.get("id")

            if channel_id:
                created_channels[channel_id] = channel

            permissions = channel_data.get(
                "permissions",
                "public"
            )

            await apply_permissions(
                channel,
                permissions,
                guild
            )

            if channel_type == "text":

                messages = channel_data.get(
                    "messages",
                    []
                )

                for message in messages:
                    pending_messages.append(
                        (channel, message)
                    )

    for channel, message in pending_messages:

        message = replace_channel_references(
            message,
            created_channels
        )

        await channel.send(message)


async def setup(client):

    @client.tree.command(
        name="template",
        description="Setup the server with a template"
    )
    @app_commands.describe(
        template="Choose a server template"
    )
    @app_commands.choices(
        template=[
            app_commands.Choice(
                name="Simple",
                value="simple"
            ),
            app_commands.Choice(
                name="Gaming",
                value="gaming"
            ),
            app_commands.Choice(
                name="Community",
                value="community"
            ),
        ]
    )
    async def template(
        interaction: discord.Interaction,
        template: app_commands.Choice[str]
    ):

        await interaction.response.defer()

        selected = TEMPLATES[template.value]

        await apply_template(
            interaction.guild,
            selected
        )

        await interaction.followup.send(
            f"✅ `{selected['name']}` template applied!"
        )