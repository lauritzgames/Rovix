from datetime import timedelta

import discord
from discord import app_commands

from core import add_warning, clear_warnings, guild_config, save_data, send_log, warning_entries


async def setup(client):

    @client.tree.command(name="ban", description="Ban a member")
    @app_commands.describe(member="Member to ban", reason="Reason", delete_days="Delete recent messages")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided", delete_days: app_commands.Range[int, 0, 7] = 0):
        if member == interaction.user or member == interaction.guild.owner:
            await interaction.response.send_message("❌ That member cannot be banned with this command.", ephemeral=True)
            return
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Rovix cannot act on that member because of role hierarchy.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await member.ban(reason=f"{reason} | By {interaction.user}", delete_message_days=delete_days)
        await send_log(interaction.guild, "Member Banned", f"{member.mention} was banned by {interaction.user.mention}.\\nReason: {reason}", "moderation", discord.Colour.red())
        await interaction.followup.send(f"🔨 Banned {member}.", ephemeral=True)

    @client.tree.command(name="unban", description="Unban a user by ID")
    @app_commands.describe(user_id="Discord user ID", reason="Reason")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        try:
            user = await client.fetch_user(int(user_id))
            await interaction.guild.unban(user, reason=f"{reason} | By {interaction.user}")
        except (ValueError, discord.NotFound, discord.Forbidden):
            await interaction.response.send_message("❌ The user ID is invalid or the user could not be unbanned.", ephemeral=True)
            return
        await send_log(interaction.guild, "Member Unbanned", f"{user} was unbanned by {interaction.user.mention}.\\nReason: {reason}", "moderation", discord.Colour.green())
        await interaction.response.send_message(f"✅ Unbanned {user}.", ephemeral=True)

    @client.tree.command(name="kick", description="Kick a member")
    @app_commands.describe(member="Member to kick", reason="Reason")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member == interaction.user or member == interaction.guild.owner:
            await interaction.response.send_message("❌ That member cannot be kicked with this command.", ephemeral=True)
            return
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Rovix cannot act on that member because of role hierarchy.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await member.kick(reason=f"{reason} | By {interaction.user}")
        await send_log(interaction.guild, "Member Kicked", f"{member.mention} was kicked by {interaction.user.mention}.\\nReason: {reason}", "moderation", discord.Colour.orange())
        await interaction.followup.send(f"👢 Kicked {member}.", ephemeral=True)

    @client.tree.command(name="timeout", description="Timeout a member")
    @app_commands.describe(member="Member to timeout", minutes="Timeout length", reason="Reason")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: app_commands.Range[int, 1, 40320], reason: str = "No reason provided"):
        if member == interaction.user or member == interaction.guild.owner:
            await interaction.response.send_message("❌ That member cannot be timed out.", ephemeral=True)
            return
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Rovix cannot act on that member because of role hierarchy.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await member.timeout(timedelta(minutes=minutes), reason=f"{reason} | By {interaction.user}")
        await send_log(interaction.guild, "Member Timed Out", f"{member.mention} was timed out for {minutes} minute(s) by {interaction.user.mention}.\\nReason: {reason}", "moderation", discord.Colour.orange())
        await interaction.followup.send(f"⏳ Timed out {member} for {minutes} minute(s).", ephemeral=True)

    @client.tree.command(name="untimeout", description="Remove a member timeout")
    @app_commands.describe(member="Member to restore", reason="Reason")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def untimeout(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.timeout(None, reason=f"{reason} | By {interaction.user}")
        await send_log(interaction.guild, "Timeout Removed", f"{member.mention} had their timeout removed by {interaction.user.mention}.", "moderation", discord.Colour.green())
        await interaction.response.send_message(f"✅ Removed {member}'s timeout.", ephemeral=True)

    @client.tree.command(name="warn", description="Warn a member")
    @app_commands.describe(member="Member to warn", reason="Reason")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        count = await add_warning(interaction.guild.id, member.id, interaction.user.id, reason)
        await send_log(interaction.guild, "Member Warned", f"{member.mention} received warning {count} from {interaction.user.mention}.\\nReason: {reason}", "moderation", discord.Colour.orange())
        try:
            await member.send(f"You received a warning in **{interaction.guild.name}**.\\nReason: {reason}")
        except discord.HTTPException:
            pass
        await interaction.response.send_message(f"⚠️ Warned {member}. They now have **{count}** warning(s).", ephemeral=True)

    @client.tree.command(name="warnings", description="View warnings for a member")
    @app_commands.describe(member="Member to inspect")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(interaction: discord.Interaction, member: discord.Member):
        entries = warning_entries(interaction.guild.id, member.id)
        if not entries:
            await interaction.response.send_message(f"✅ {member.mention} has no warnings.", ephemeral=True)
            return
        lines = []
        for index, entry in enumerate(entries[-10:], 1):
            lines.append(f"**{index}.** {entry['reason']} — <@{entry['moderator_id']}>")
        embed = discord.Embed(title=f"Warnings for {member}", description="\\n".join(lines), colour=discord.Colour.orange())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @client.tree.command(name="clearwarnings", description="Clear all warnings for a member")
    @app_commands.describe(member="Member to clear")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def clearwarnings(interaction: discord.Interaction, member: discord.Member):
        await clear_warnings(interaction.guild.id, member.id)
        await send_log(interaction.guild, "Warnings Cleared", f"{interaction.user.mention} cleared warnings for {member.mention}.", "moderation", discord.Colour.green())
        await interaction.response.send_message(f"🧽 Cleared warnings for {member}.", ephemeral=True)

    @client.tree.command(name="softban", description="Ban and immediately unban a member")
    @app_commands.describe(member="Member to softban", reason="Reason", delete_days="Delete recent messages")
    @app_commands.checks.has_permissions(ban_members=True)
    async def softban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided", delete_days: app_commands.Range[int, 0, 7] = 1):
        if member == interaction.user or member == interaction.guild.owner or member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Rovix cannot softban that member.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await member.ban(reason=f"Softban: {reason} | By {interaction.user}", delete_message_days=delete_days)
        await interaction.guild.unban(member, reason=f"Softban release | By {interaction.user}")
        await send_log(interaction.guild, "Member Softbanned", f"{member} was softbanned by {interaction.user.mention}.\\nReason: {reason}", "moderation", discord.Colour.orange())
        await interaction.followup.send(f"🧹 Softbanned {member}.", ephemeral=True)

    @client.tree.command(name="nick", description="Change a member nickname")
    @app_commands.describe(member="Member", nickname="New nickname, or leave empty to reset")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def nick(interaction: discord.Interaction, member: discord.Member, nickname: str | None = None):
        if member.top_role >= interaction.guild.me.top_role and member != interaction.user:
            await interaction.response.send_message("❌ Rovix cannot edit that member because of role hierarchy.", ephemeral=True)
            return
        await member.edit(nick=nickname, reason=f"Nickname changed by {interaction.user}")
        await send_log(interaction.guild, "Nickname Changed", f"{interaction.user.mention} changed {member.mention}'s nickname.", "moderation")
        await interaction.response.send_message("✅ Nickname updated.", ephemeral=True)

    @client.tree.command(name="purge", description="Bulk delete messages from a member")
    @app_commands.describe(member="Member whose messages to delete", amount="Maximum messages to scan")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(interaction: discord.Interaction, member: discord.Member, amount: app_commands.Range[int, 1, 100]):
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("This command requires a text channel.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount, check=lambda message: message.author.id == member.id)
        await send_log(interaction.guild, "Messages Purged", f"{interaction.user.mention} purged {len(deleted)} message(s) from {member.mention}.", "messages", discord.Colour.orange())
        await interaction.followup.send(f"🧹 Deleted {len(deleted)} message(s) from {member}.", ephemeral=True)

    @client.tree.command(name="history", description="Show recent audit activity involving a member")
    @app_commands.describe(member="Member to inspect")
    @app_commands.checks.has_permissions(view_audit_log=True)
    async def history(interaction: discord.Interaction, member: discord.Member):
        rows = []
        async for entry in interaction.guild.audit_logs(limit=50):
            target = getattr(entry, "target", None)
            if getattr(target, "id", None) == member.id:
                rows.append(f"• {entry.action.name} — {entry.user.mention if entry.user else 'Unknown'}")
            if len(rows) >= 10:
                break
        embed = discord.Embed(title=f"Moderation History: {member}", description="\\n".join(rows) or "No recent audit entries were found.", colour=discord.Colour.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @client.tree.command(name="modlogs", description="Set the moderation log channel")
    @app_commands.describe(channel="Text channel for moderation logs")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def modlogs(interaction: discord.Interaction, channel: discord.TextChannel):
        guild_config(interaction.guild.id)["logging"]["channel_id"] = channel.id
        await save_data()
        await send_log(interaction.guild, "Moderation Logging Enabled", f"Configured by {interaction.user.mention}.", "moderation", discord.Colour.green())
        await interaction.response.send_message(f"✅ Log channel set to {channel.mention}.", ephemeral=True)
