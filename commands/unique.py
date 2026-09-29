import discord
from discord import app_commands

from core import guild_config, normalize_name


unique = app_commands.Group(name="rovix", description="Advanced Rovix server tools")


async def _snapshot_channel(channel):
    overwrites = {}
    for target, overwrite in channel.overwrites.items():
        if isinstance(target, discord.Role):
            overwrites[target] = overwrite
        elif isinstance(target, discord.Member):
            overwrites[target] = overwrite

    data = {
        "id": channel.id,
        "name": channel.name,
        "position": channel.position,
        "category_id": channel.category.id if channel.category else None,
        "overwrites": overwrites,
        "type": channel.type,
    }

    if isinstance(channel, discord.TextChannel):
        data.update({
            "topic": channel.topic,
            "slowmode_delay": channel.slowmode_delay,
            "nsfw": channel.nsfw,
            "news": channel.is_news(),
        })
    elif isinstance(channel, discord.VoiceChannel):
        data.update({
            "bitrate": channel.bitrate,
            "user_limit": channel.user_limit,
            "rtc_region": channel.rtc_region,
        })
    elif isinstance(channel, discord.StageChannel):
        data.update({
            "bitrate": channel.bitrate,
            "user_limit": channel.user_limit,
            "rtc_region": channel.rtc_region,
        })
    elif isinstance(channel, discord.ForumChannel):
        data.update({
            "topic": channel.topic,
            "slowmode_delay": channel.slowmode_delay,
            "nsfw": channel.nsfw,
        })

    return data


async def _snapshot_messages(channel):
    saved = []
    async for message in channel.history(limit=10, oldest_first=True):
        attachments = [attachment.url for attachment in message.attachments]
        saved.append({
            "author": str(message.author),
            "content": message.content,
            "attachments": attachments,
        })
    return saved


async def _restore_messages(channel, messages):
    for message in messages:
        parts = [f"**Original message by {message['author']}**"]
        if message["content"]:
            parts.append(message["content"])
        if message["attachments"]:
            parts.append("\n".join(message["attachments"]))
        await channel.send("\n".join(parts)[:2000])


async def _recreate_channel(guild, data, categories):
    category = categories.get(data["category_id"])
    kwargs = {
        "name": data["name"],
        "category": category,
        "overwrites": data["overwrites"],
    }

    if data["type"] == discord.ChannelType.text:
        channel = await guild.create_text_channel(
            **kwargs,
            topic=data.get("topic"),
            slowmode_delay=data.get("slowmode_delay", 0),
            nsfw=data.get("nsfw", False),
            news=data.get("news", False),
        )
    elif data["type"] == discord.ChannelType.voice:
        channel = await guild.create_voice_channel(
            **kwargs,
            bitrate=data.get("bitrate"),
            user_limit=data.get("user_limit", 0),
            rtc_region=data.get("rtc_region"),
        )
    elif data["type"] == discord.ChannelType.stage_voice:
        channel = await guild.create_stage_channel(
            **kwargs,
            bitrate=data.get("bitrate"),
            user_limit=data.get("user_limit", 0),
            rtc_region=data.get("rtc_region"),
        )
    elif data["type"] == discord.ChannelType.forum:
        channel = await guild.create_forum(
            **kwargs,
            topic=data.get("topic"),
            slowmode_delay=data.get("slowmode_delay", 0),
            nsfw=data.get("nsfw", False),
        )
    else:
        return None

    await channel.edit(position=data["position"])
    return channel


async def _reset_server(guild, preserved_channels):
    preserved_ids = {channel.id for channel in preserved_channels}
    categories = list(guild.categories)
    channels = [channel for channel in guild.channels if channel.id not in preserved_ids]

    category_snapshots = []
    for category in categories:
        category_snapshots.append({
            "id": category.id,
            "name": category.name,
            "position": category.position,
            "overwrites": dict(category.overwrites),
        })

    channel_snapshots = []
    for channel in channels:
        channel_snapshots.append(await _snapshot_channel(channel))

    saved_messages = {}
    preserved_snapshots = {}
    for channel in preserved_channels:
        preserved_snapshots[channel.id] = await _snapshot_channel(channel)
        saved_messages[channel.id] = await _snapshot_messages(channel)

    for channel in sorted(channels, key=lambda item: item.position, reverse=True):
        try:
            await channel.delete(reason=f"Rovix server reset by {guild.me}")
        except discord.HTTPException:
            pass

    for category in sorted(categories, key=lambda item: item.position, reverse=True):
        try:
            await category.delete(reason=f"Rovix server reset by {guild.me}")
        except discord.HTTPException:
            pass

    recreated_categories = {}
    for data in sorted(category_snapshots, key=lambda item: item["position"]):
        category = await guild.create_category(
            data["name"],
            overwrites=data["overwrites"],
        )
        await category.edit(position=data["position"])
        recreated_categories[data["id"]] = category

    recreated_channels = {}
    for data in sorted(channel_snapshots, key=lambda item: item["position"]):
        channel = await _recreate_channel(guild, data, recreated_categories)
        if channel:
            recreated_channels[data["id"]] = channel

    for channel in preserved_channels:
        original_category_id = preserved_snapshots[channel.id]["category_id"]
        if original_category_id in recreated_categories:
            await channel.edit(category=recreated_categories[original_category_id])

        try:
            await channel.edit(position=preserved_snapshots[channel.id]["position"])
        except discord.HTTPException:
            pass

        await _restore_messages(channel, saved_messages.get(channel.id, []))

    return len(categories), len(channels), sum(len(messages) for messages in saved_messages.values())


async def setup(client):
    client.tree.add_command(unique)


    @unique.command(name="serverreset", description="Rebuild the server from its current structure")
    @app_commands.describe(
        preserve1="Text channel to keep and restore its 10 oldest messages",
        preserve2="Second text channel to keep",
        preserve3="Third text channel to keep",
        confirm="Actually delete and rebuild the server",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def serverreset(
        interaction: discord.Interaction,
        preserve1: discord.TextChannel | None = None,
        preserve2: discord.TextChannel | None = None,
        preserve3: discord.TextChannel | None = None,
        confirm: bool = False,
    ):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        me = guild.me
        if me is None or not me.guild_permissions.manage_channels:
            await interaction.response.send_message("Rovix needs Manage Channels to rebuild this server.", ephemeral=True)
            return

        preserved = []
        for channel in (preserve1, preserve2, preserve3):
            if channel and channel.id not in {item.id for item in preserved}:
                preserved.append(channel)

        deletable_channels = [channel for channel in guild.channels if channel.id not in {item.id for item in preserved}]
        preserved_text = ", ".join(channel.mention for channel in preserved) or "None"

        if not confirm:
            embed = discord.Embed(
                title="Ã¢Å¡Â Ã¯Â¸Â Rovix Server Reset",
                description=(
                    "This will delete and recreate the server structure. "
                    "Categories, channels, and their permission overwrites will be rebuilt from the current server."
                ),
                colour=discord.Colour.orange(),
            )
            embed.add_field(name="Categories", value=str(len(guild.categories)))
            embed.add_field(name="Channels to recreate", value=str(len(deletable_channels)))
            embed.add_field(name="Channels preserved", value=preserved_text, inline=False)
            embed.add_field(
                name="Preserved messages",
                value="Up to 10 oldest messages from each preserved text channel will be reposted.",
                inline=False,
            )
            embed.set_footer(text="Run /rovix serverreset again with confirm:true to continue.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not preserved:
            preserved_warning = "No channels are preserved, so every channel will be deleted."
        else:
            preserved_warning = f"Preserving {len(preserved)} channel(s): {preserved_text}"

        await interaction.response.send_message(
            f"Ã°Å¸â€â€ž Starting server reset. {preserved_warning}",
            ephemeral=True,
        )

        try:
            categories, channels, messages = await _reset_server(guild, preserved)
        except Exception as error:
            print(f"Rovix server reset failed in {guild.id}: {error}")
            return

        print(
            f"Rovix server reset completed in {guild.id}: "
            f"{categories} categories, {channels} channels recreated, {messages} messages restored."
        )

    @unique.command(name="serveraudit", description="Audit important server configuration")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def serveraudit(interaction: discord.Interaction):
        guild = interaction.guild
        findings = []
        me = guild.me
        if not guild.system_channel:
            findings.append("No system channel is configured.")
        if not any(role.name.casefold() == "staff" for role in guild.roles):
            findings.append("No Staff role exists.")
        if me and not me.guild_permissions.manage_channels:
            findings.append("Rovix does not have Manage Channels.")
        if me and not me.guild_permissions.manage_messages:
            findings.append("Rovix does not have Manage Messages.")
        if len(guild.channels) >= 450:
            findings.append("The server is near the channel limit.")
        if not findings:
            findings.append("No obvious configuration issues were detected.")
        embed = discord.Embed(title="Rovix Server Audit", description="\n".join(f"Ã¢â‚¬Â¢ {item}" for item in findings), colour=discord.Colour.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @unique.command(name="permissionsaudit", description="Find high-risk role permissions")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def permissionsaudit(interaction: discord.Interaction):
        issues = []
        everyone = interaction.guild.default_role
        if everyone.permissions.administrator:
            issues.append("@everyone has Administrator.")
        if everyone.permissions.manage_guild:
            issues.append("@everyone has Manage Server.")
        for role in interaction.guild.roles:
            if role.is_default() or role.managed:
                continue
            if role.permissions.administrator:
                issues.append(f"{role.mention} has Administrator.")
        embed = discord.Embed(
            title="Permission Audit",
            description="\n".join(f"Ã¢â‚¬Â¢ {item}" for item in issues[:25]) if issues else "No high-risk role permissions were detected.",
            colour=discord.Colour.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @unique.command(name="cleanup", description="Find or delete empty text channels")
    @app_commands.describe(delete="Delete the empty channels")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def cleanup(interaction: discord.Interaction, delete: bool = False):
        empty = []
        for channel in interaction.guild.text_channels:
            try:
                messages = [message async for message in channel.history(limit=1)]
            except discord.HTTPException:
                continue
            if not messages:
                empty.append(channel)
        if delete:
            deleted = 0
            for channel in empty:
                try:
                    await channel.delete(reason=f"Rovix cleanup by {interaction.user}")
                    deleted += 1
                except discord.HTTPException:
                    pass
            await interaction.response.send_message(f"Ã°Å¸Â§Â¹ Deleted {deleted} empty channel(s).", ephemeral=True)
            return
        value = ", ".join(channel.mention for channel in empty[:30]) or "No empty text channels found."
        await interaction.response.send_message(f"Empty text channels:\n{value}", ephemeral=True)

    @unique.command(name="duplicatechannels", description="Find duplicate channel names")
    async def duplicatechannels(interaction: discord.Interaction):
        groups = {}
        for channel in interaction.guild.channels:
            groups.setdefault(normalize_name(channel.name), []).append(channel)
        duplicates = [channels for channels in groups.values() if len(channels) > 1]
        lines = [", ".join(channel.mention for channel in channels) for channels in duplicates[:20]]
        await interaction.response.send_message("\n".join(lines) if lines else "No duplicate channel names found.", ephemeral=True)

    @unique.command(name="roleaudit", description="Show unused and managed roles")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def roleaudit(interaction: discord.Interaction):
        unused = []
        managed = []
        for role in interaction.guild.roles:
            if role.is_default():
                continue
            if role.managed:
                managed.append(role.mention)
            elif not role.members:
                unused.append(role.mention)
        embed = discord.Embed(title="Role Audit", colour=discord.Colour.blurple())
        embed.add_field(name="Unused", value=", ".join(unused[:40]) or "None", inline=False)
        embed.add_field(name="Managed", value=", ".join(managed[:40]) or "None", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @unique.command(name="channelstats", description="Show channel statistics")
    async def channelstats(interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title="Channel Statistics", colour=discord.Colour.blurple())
        embed.add_field(name="Text", value=str(len(guild.text_channels)))
        embed.add_field(name="Voice", value=str(len(guild.voice_channels)))
        embed.add_field(name="Forums", value=str(len(guild.forums)))
        embed.add_field(name="Categories", value=str(len(guild.categories)))
        threads = sum(len(channel.threads) for channel in guild.text_channels)
        embed.add_field(name="Cached threads", value=str(threads))
        await interaction.response.send_message(embed=embed)

    @unique.command(name="activity", description="Show recent server audit activity")
    @app_commands.checks.has_permissions(view_audit_log=True)
    async def activity(interaction: discord.Interaction):
        rows = []
        async for entry in interaction.guild.audit_logs(limit=15):
            actor = entry.user.mention if entry.user else "Unknown"
            rows.append(f"Ã¢â‚¬Â¢ {entry.action.name} Ã¢â‚¬â€ {actor}")
        await interaction.response.send_message("\n".join(rows) or "No recent activity was found.", ephemeral=True)

    @unique.command(name="whois", description="Show detailed user information")
    @app_commands.describe(member="Member to inspect")
    async def whois(interaction: discord.Interaction, member: discord.Member | None = None):
        member = member or interaction.user
        roles = ", ".join(role.mention for role in member.roles[1:]) or "None"
        embed = discord.Embed(title=f"User: {member}", colour=member.colour)
        embed.add_field(name="ID", value=str(member.id))
        embed.add_field(name="Created", value=discord.utils.format_dt(member.created_at, "F"))
        embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, "F") if member.joined_at else "Unknown")
        embed.add_field(name="Roles", value=roles[:1024], inline=False)
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        await interaction.response.send_message(embed=embed)

    @unique.command(name="serverhealth", description="Show server health indicators")
    async def serverhealth(interaction: discord.Interaction):
        guild = interaction.guild
        me = guild.me
        config = guild_config(guild.id)
        embed = discord.Embed(title="Rovix Server Health", colour=discord.Colour.green())
        embed.add_field(name="Members", value=str(guild.member_count))
        embed.add_field(name="Channels", value=str(len(guild.channels)))
        embed.add_field(name="Roles", value=str(len(guild.roles)))
        embed.add_field(name="Rovix", value="Administrator" if me and me.guild_permissions.administrator else "Standard permissions")
        embed.add_field(name="Logging", value="Configured" if config["logging"]["channel_id"] else "Not configured")
        embed.add_field(name="Tickets", value="Configured" if config["tickets"]["category_id"] else "Not configured")
        embed.add_field(name="AutoMod", value="Configured")
        await interaction.response.send_message(embed=embed)

    @unique.command(name="botlist", description="List bots in the server")
    async def botlist(interaction: discord.Interaction):
        bots = [member for member in interaction.guild.members if member.bot]
        text = "\n".join(f"Ã¢â‚¬Â¢ {member.mention}" for member in bots[:50]) or "No bots found."
        await interaction.response.send_message(embed=discord.Embed(title="Bots", description=text, colour=discord.Colour.blurple()))

    @unique.command(name="commands", description="Browse Rovix commands")
    async def command_browser(interaction: discord.Interaction):
        embed = discord.Embed(title="Rovix Commands", description="Use /server for the interactive control panel.", colour=discord.Colour.blurple())
        embed.add_field(name="Management", value="/lock /unlock /clear /hide /unhide /rename /topic /movechannel /createforum", inline=False)
        embed.add_field(name="Moderation", value="/ban /unban /kick /timeout /untimeout /warn /warnings /clearwarnings /softban /nick /purge /history /modlogs", inline=False)
        embed.add_field(name="Systems", value="/automod /ticket /logs /welcome /goodbye /autorole /verification /rules /membercount /serverstats", inline=False)
        embed.add_field(name="Utilities", value="/poll /embed /announce /say /remind /timer /reactionrole /suggest /afk /8ball /choose", inline=False)
        embed.add_field(name="Advanced", value="/rovix serveraudit /rovix serverreset /rovix permissionsaudit /rovix cleanup /rovix duplicatechannels /rovix roleaudit /rovix channelstats /rovix activity /rovix whois /rovix serverhealth /rovix botlist /rovix commands /rovix help /rovix report /rovix feedback /rovix suggestion", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @unique.command(name="help", description="Open Rovix help")
    async def help_command(interaction: discord.Interaction):
        embed = discord.Embed(title="Rovix Help", description="Use /server for the interactive control panel or /rovix commands for the full command index.", colour=discord.Colour.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @unique.command(name="report", description="Send a server report")
    @app_commands.describe(text="Report contents")
    async def report(interaction: discord.Interaction, text: str):
        channel_id = guild_config(interaction.guild.id)["member"].get("report_channel_id")
        channel = interaction.guild.get_channel(channel_id) if channel_id else interaction.channel
        await channel.send(embed=discord.Embed(title="Ã°Å¸Å¡Â¨ User Report", description=text[:4000], colour=discord.Colour.red()).set_footer(text=f"From {interaction.user}"))
        await interaction.response.send_message("Ã¢Å“â€¦ Report sent.", ephemeral=True)

    @unique.command(name="feedback", description="Send server feedback")
    @app_commands.describe(text="Feedback contents")
    async def feedback(interaction: discord.Interaction, text: str):
        channel_id = guild_config(interaction.guild.id)["member"].get("feedback_channel_id")
        channel = interaction.guild.get_channel(channel_id) if channel_id else interaction.channel
        await channel.send(embed=discord.Embed(title="Ã°Å¸â€™Â¬ Feedback", description=text[:4000], colour=discord.Colour.blurple()).set_footer(text=f"From {interaction.user}"))
        await interaction.response.send_message("Ã¢Å“â€¦ Feedback sent.", ephemeral=True)

    @unique.command(name="suggestion", description="Post a suggestion")
    @app_commands.describe(text="Suggestion contents")
    async def suggestion(interaction: discord.Interaction, text: str):
        channel_id = guild_config(interaction.guild.id)["member"].get("suggestion_channel_id")
        channel = interaction.guild.get_channel(channel_id) if channel_id else interaction.channel
        await channel.send(embed=discord.Embed(title="Ã°Å¸â€™Â¡ Suggestion", description=text[:4000], colour=discord.Colour.green()).set_footer(text=f"From {interaction.user}"))
        await interaction.response.send_message("Ã¢Å“â€¦ Suggestion posted.", ephemeral=True)




