import re
import time
from collections import defaultdict, deque

import discord

from core import guild_config, normalize_text, send_log


spam_cache = defaultdict(lambda: defaultdict(deque))


async def setup(client):

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if isinstance(message.channel, discord.DMChannel):
            await message.channel.send("Hello! 👋")
            return
        if not message.guild or message.author.bot or message.webhook_id:
            return

        afk = getattr(client, "_rovix_afk", {})
        own_status = afk.pop(message.author.id, None)
        if own_status:
            try:
                await message.channel.send(f"👋 {message.author.mention}, your AFK status has been cleared.", delete_after=5)
            except discord.HTTPException:
                pass
        for mentioned in message.mentions:
            reason = afk.get(mentioned.id)
            if reason:
                try:
                    await message.channel.send(f"💤 {mentioned.display_name} is AFK: {reason}", delete_after=8)
                except discord.HTTPException:
                    pass

        config = guild_config(message.guild.id)["automod"]
        text = message.content
        normalized = normalize_text(text)
        reason = None

        for word in config["words"]:
            candidate = normalize_text(word).strip()
            if candidate and candidate in normalized:
                reason = "Blocked word"
                break

        if not reason and config["invites"] and re.search(r"discord(?:\.gg|\.com/invite)/\S+", text.casefold()):
            reason = "Discord invite"

        if not reason and config["links"]:
            domains = re.findall(r"(?:https?://|www\.)([^/\s]+)", text.casefold())
            for domain in domains:
                if not any(domain == allowed or domain.endswith("." + allowed) for allowed in config["whitelist"]):
                    reason = "Unapproved link"
                    break

        if not reason and config["mentions"]:
            count = len(message.mentions) + len(message.role_mentions)
            if count > config["max_mentions"]:
                reason = "Mention spam"

        if not reason and config["caps"]:
            letters = [char for char in text if char.isalpha()]
            if len(letters) >= 10 and sum(char.isupper() for char in letters) / len(letters) >= 0.8:
                reason = "Excessive caps"

        if not reason and config["spam"]:
            now = time.monotonic()
            history = spam_cache[message.guild.id][message.author.id]
            history.append(now)
            while history and now - history[0] > config["spam_window"]:
                history.popleft()
            if len(history) > config["spam_limit"]:
                reason = "Spam"

        if reason:
            try:
                await message.delete(reason=f"Rovix AutoMod: {reason}")
            except discord.HTTPException:
                pass
            await send_log(
                message.guild,
                "AutoMod Action",
                f"Deleted a message from {message.author.mention} in {message.channel.mention}.\nReason: **{reason}**",
                "moderation",
                discord.Colour.orange()
            )
            try:
                await message.channel.send(f"🛡️ {message.author.mention}, your message was removed: **{reason}**.", delete_after=5)
            except discord.HTTPException:
                pass

    @client.event
    async def on_message_delete(message):
        if message.guild and message.author != client.user:
            await send_log(
                message.guild,
                "Message Deleted",
                f"Author: {message.author.mention}\nChannel: {message.channel.mention}\nContent: {message.content[:1500] or '[No text]'}",
                "messages",
                discord.Colour.red()
            )

    @client.event
    async def on_message_edit(before, after):
        if before.guild and before.content != after.content:
            await send_log(
                before.guild,
                "Message Edited",
                f"{before.author.mention} edited {before.channel.mention}.\nBefore: {before.content[:700]}\nAfter: {after.content[:700]}",
                "messages",
                discord.Colour.gold()
            )

    @client.event
    async def on_raw_reaction_add(payload):
        if not payload.guild_id:
            return
        guild = client.get_guild(payload.guild_id)
        if not guild:
            return
        config = guild_config(guild.id)
        data = config["reaction_roles"].get(str(payload.message_id))
        if not data or str(payload.emoji) != data["emoji"]:
            return
        member = guild.get_member(payload.user_id)
        role = guild.get_role(data["role_id"])
        if member and role and not member.bot and role < guild.me.top_role:
            try:
                await member.add_roles(role, reason="Rovix reaction role")
            except discord.HTTPException:
                pass

    @client.event
    async def on_raw_reaction_remove(payload):
        if not payload.guild_id:
            return
        guild = client.get_guild(payload.guild_id)
        if not guild:
            return
        data = guild_config(guild.id)["reaction_roles"].get(str(payload.message_id))
        if not data or str(payload.emoji) != data["emoji"]:
            return
        member = guild.get_member(payload.user_id)
        role = guild.get_role(data["role_id"])
        if member and role and role < guild.me.top_role:
            try:
                await member.remove_roles(role, reason="Rovix reaction role")
            except discord.HTTPException:
                pass
