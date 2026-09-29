import discord

from core import guild_config, send_log


async def setup(client):

    @client.event
    async def on_member_join(member):
        config = guild_config(member.guild.id)["member"]
        autorole = member.guild.get_role(config.get("autorole_id")) if config.get("autorole_id") else None
        if autorole and autorole < member.guild.me.top_role:
            try:
                await member.add_roles(autorole, reason="Rovix autorole")
            except discord.HTTPException:
                pass
        channel = member.guild.get_channel(config.get("welcome_channel_id")) if config.get("welcome_channel_id") else None
        if isinstance(channel, discord.TextChannel):
            try:
                await channel.send(config["welcome_message"].format(member=member.mention, server=member.guild.name))
            except discord.HTTPException:
                pass
        await send_log(member.guild, "Member Joined", f"{member.mention} joined the server.", "members", discord.Colour.green())

    @client.event
    async def on_member_remove(member):
        config = guild_config(member.guild.id)["member"]
        channel = member.guild.get_channel(config.get("goodbye_channel_id")) if config.get("goodbye_channel_id") else None
        if isinstance(channel, discord.TextChannel):
            try:
                await channel.send(config["goodbye_message"].format(member=member, server=member.guild.name))
            except discord.HTTPException:
                pass
        await send_log(member.guild, "Member Left", f"{member} left the server.", "members", discord.Colour.orange())

    @client.event
    async def on_member_update(before, after):
        changes = []
        if before.nick != after.nick:
            changes.append(f"Nickname: {before.nick or 'None'} → {after.nick or 'None'}")
        if before.roles != after.roles:
            changes.append("Roles changed")
        if changes:
            await send_log(after.guild, "Member Updated", f"{after.mention}\n" + "\n".join(changes), "members", discord.Colour.gold())

    @client.event
    async def on_guild_channel_create(channel):
        await send_log(channel.guild, "Channel Created", f"{channel.mention} was created.", "channels", discord.Colour.green())

    @client.event
    async def on_guild_channel_delete(channel):
        await send_log(channel.guild, "Channel Deleted", f"{channel.name} was deleted.", "channels", discord.Colour.red())

    @client.event
    async def on_guild_channel_update(before, after):
        changes = []
        if before.name != after.name:
            changes.append(f"Name: {before.name} → {after.name}")
        if getattr(before, "category_id", None) != getattr(after, "category_id", None):
            changes.append("Category changed")
        if changes:
            await send_log(after.guild, "Channel Updated", f"{after.mention}\n" + "\n".join(changes), "channels", discord.Colour.gold())

    @client.event
    async def on_guild_role_create(role):
        await send_log(role.guild, "Role Created", f"{role.mention} was created.", "roles", discord.Colour.green())

    @client.event
    async def on_guild_role_delete(role):
        await send_log(role.guild, "Role Deleted", f"{role.name} was deleted.", "roles", discord.Colour.red())

    @client.event
    async def on_guild_role_update(before, after):
        changes = []
        if before.name != after.name:
            changes.append(f"Name: {before.name} → {after.name}")
        if before.permissions != after.permissions:
            changes.append("Permissions changed")
        if changes:
            await send_log(after.guild, "Role Updated", f"{after.mention}\n" + "\n".join(changes), "roles", discord.Colour.gold())

    @client.event
    async def on_voice_state_update(member, before, after):
        if before.channel == after.channel:
            return
        before_name = before.channel.mention if before.channel else "None"
        after_name = after.channel.mention if after.channel else "None"
        await send_log(
            member.guild,
            "Voice State Changed",
            f"{member.mention}: {before_name} → {after_name}",
            "voice",
            discord.Colour.blurple()
        )

    @client.event
    async def on_guild_update(before, after):
        changes = []
        if before.name != after.name:
            changes.append(f"Name: {before.name} → {after.name}")
        if before.verification_level != after.verification_level:
            changes.append("Verification level changed")
        if changes:
            await send_log(after, "Server Updated", "\n".join(changes), "server", discord.Colour.gold())
