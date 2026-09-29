import asyncio
import secrets
from datetime import timedelta

import discord
from discord import app_commands


async def setup(client):

    @client.tree.command(name="poll", description="Create a native Discord poll")
    @app_commands.describe(question="Poll question", options="Options separated by |", hours="Duration in hours", multiple="Allow multiple choices")
    async def poll(interaction: discord.Interaction, question: str, options: str, hours: app_commands.Range[int, 1, 168] = 24, multiple: bool = False):
        values = [item.strip() for item in options.split("|") if item.strip()]
        if not 2 <= len(values) <= 10:
            await interaction.response.send_message("❌ Provide 2 to 10 options separated by |.", ephemeral=True)
            return
        poll_obj = discord.Poll(question, timedelta(hours=hours), multiple=multiple)
        for value in values:
            poll_obj.add_answer(text=value)
        await interaction.response.send_message(poll=poll_obj)

    @client.tree.command(name="embed", description="Send an embed")
    @app_commands.describe(title="Embed title", description="Embed body")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def embed(interaction: discord.Interaction, title: str, description: str):
        await interaction.response.defer(ephemeral=True)
        embed_obj = discord.Embed(title=title[:256], description=description[:4096], colour=discord.Colour.blurple())
        await interaction.channel.send(embed=embed_obj)
        await interaction.followup.send("✅ Embed sent.", ephemeral=True)

    @client.tree.command(name="announce", description="Send an announcement")
    @app_commands.describe(title="Announcement title", message="Announcement body")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def announce(interaction: discord.Interaction, title: str, message: str):
        await interaction.response.defer(ephemeral=True)
        embed_obj = discord.Embed(title=title[:256], description=message[:4096], colour=discord.Colour.gold())
        await interaction.channel.send(embed=embed_obj)
        await interaction.followup.send("✅ Announcement sent.", ephemeral=True)

    @client.tree.command(name="say", description="Make Rovix send a message")
    @app_commands.describe(message="Message to send")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def say(interaction: discord.Interaction, message: str):
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.send(message[:2000], allowed_mentions=discord.AllowedMentions.none())
        await interaction.followup.send("✅ Message sent.", ephemeral=True)

    @client.tree.command(name="remind", description="Schedule a reminder")
    @app_commands.describe(minutes="Minutes from now", message="Reminder text")
    async def remind(interaction: discord.Interaction, minutes: app_commands.Range[int, 1, 10080], message: str):
        await interaction.response.send_message(f"⏰ Reminder scheduled for {minutes} minute(s).", ephemeral=True)

        async def deliver():
            await asyncio.sleep(minutes * 60)
            try:
                await interaction.user.send(f"⏰ Reminder from {interaction.guild.name}: {message}")
            except discord.HTTPException:
                pass

        task = asyncio.create_task(deliver())
        client._rovix_tasks = getattr(client, "_rovix_tasks", set())
        client._rovix_tasks.add(task)
        task.add_done_callback(client._rovix_tasks.discard)

    @client.tree.command(name="timer", description="Start a channel timer")
    @app_commands.describe(seconds="Timer length", message="Completion message")
    async def timer(interaction: discord.Interaction, seconds: app_commands.Range[int, 1, 86400], message: str = "Timer finished."):
        await interaction.response.send_message(f"⏱️ Timer started for {seconds} second(s).", ephemeral=True)

        async def deliver(channel_id, user_id):
            await asyncio.sleep(seconds)
            channel = client.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(f"⏱️ <@{user_id}> {message}")
                except discord.HTTPException:
                    pass

        task = asyncio.create_task(deliver(interaction.channel.id, interaction.user.id))
        client._rovix_tasks = getattr(client, "_rovix_tasks", set())
        client._rovix_tasks.add(task)
        task.add_done_callback(client._rovix_tasks.discard)

    @client.tree.command(name="reactionrole", description="Create a reaction role")
    @app_commands.describe(role="Role to grant", emoji="Emoji", message="Prompt")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def reactionrole(interaction: discord.Interaction, role: discord.Role, emoji: str, message: str):
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Rovix cannot manage that role.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        sent = await interaction.channel.send(f"{message}\nReact with {emoji} to receive {role.mention}.")
        await sent.add_reaction(emoji)
        from core import guild_config, save_data
        config = guild_config(interaction.guild.id)
        config["reaction_roles"][str(sent.id)] = {"role_id": role.id, "emoji": emoji}
        await save_data()
        await interaction.followup.send("✅ Reaction role created.", ephemeral=True)

    @client.tree.command(name="suggest", description="Submit a suggestion")
    @app_commands.describe(text="Suggestion")
    async def suggest(interaction: discord.Interaction, text: str):
        await interaction.response.send_message("💡 Suggestion submitted.", ephemeral=True)
        embed_obj = discord.Embed(title="💡 Suggestion", description=text[:4000], colour=discord.Colour.blurple())
        embed_obj.set_footer(text=f"Submitted by {interaction.user}")
        await interaction.channel.send(embed=embed_obj)

    @client.tree.command(name="afk", description="Set or clear your AFK status")
    @app_commands.describe(reason="AFK reason")
    async def afk(interaction: discord.Interaction, reason: str = "AFK"):
        client._rovix_afk = getattr(client, "_rovix_afk", {})
        client._rovix_afk[interaction.user.id] = reason[:200]
        await interaction.response.send_message(f"💤 AFK enabled: {reason}", ephemeral=True)

    @client.tree.command(name="8ball", description="Ask a question")
    @app_commands.describe(question="Question")
    async def eightball(interaction: discord.Interaction, question: str):
        answers = ["Yes.", "No.", "Probably.", "Probably not.", "Definitely.", "Ask again later.", "It is possible."]
        await interaction.response.send_message(f"🎱 Question: {question}\nAnswer: {secrets.choice(answers)}")

    @client.tree.command(name="choose", description="Choose one option")
    @app_commands.describe(options="Options separated by |")
    async def choose(interaction: discord.Interaction, options: str):
        values = [item.strip() for item in options.split("|") if item.strip()]
        if len(values) < 2:
            await interaction.response.send_message("❌ Provide at least 2 options separated by |.", ephemeral=True)
            return
        await interaction.response.send_message(f"🎲 Chosen: **{secrets.choice(values)}**")
