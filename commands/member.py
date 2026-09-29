import discord
from discord import app_commands

from core import guild_config, save_data, send_log


class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.success, emoji="✅", custom_id="rovix:verify")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = guild_config(interaction.guild.id)["member"]
        role_id = config.get("verification_role_id")
        role = interaction.guild.get_role(role_id) if role_id else None
        if not role:
            await interaction.response.send_message("❌ Verification is not configured.", ephemeral=True)
            return
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Rovix cannot assign the verification role.", ephemeral=True)
            return
        try:
            await interaction.user.add_roles(role, reason="Rovix verification")
        except discord.HTTPException:
            await interaction.response.send_message("❌ Discord rejected the role update.", ephemeral=True)
            return
        await interaction.response.send_message(f"✅ You are verified with {role.mention}.", ephemeral=True)


async def setup(client):
    client.add_view(VerificationView())

    @client.tree.command(name="welcome", description="Configure or test welcome messages")
    @app_commands.describe(channel="Welcome channel", message="Message using {member} and {server}")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def welcome(interaction: discord.Interaction, channel: discord.TextChannel | None = None, message: str | None = None):
        config = guild_config(interaction.guild.id)["member"]
        if channel:
            config["welcome_channel_id"] = channel.id
        if message:
            config["welcome_message"] = message[:2000]
        await save_data()
        target = interaction.guild.get_channel(config.get("welcome_channel_id"))
        if target:
            await target.send(config["welcome_message"].format(member=interaction.user.mention, server=interaction.guild.name))
        await interaction.response.send_message("✅ Welcome settings saved.", ephemeral=True)

    @client.tree.command(name="goodbye", description="Configure goodbye messages")
    @app_commands.describe(channel="Goodbye channel", message="Message using {member} and {server}")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def goodbye(interaction: discord.Interaction, channel: discord.TextChannel | None = None, message: str | None = None):
        config = guild_config(interaction.guild.id)["member"]
        if channel:
            config["goodbye_channel_id"] = channel.id
        if message:
            config["goodbye_message"] = message[:2000]
        await save_data()
        await interaction.response.send_message("✅ Goodbye settings saved.", ephemeral=True)

    @client.tree.command(name="autorole", description="Configure the automatic role for new members")
    @app_commands.describe(role="Role to assign, or leave empty to disable")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def autorole(interaction: discord.Interaction, role: discord.Role | None = None):
        if role and role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Rovix cannot assign that role.", ephemeral=True)
            return
        guild_config(interaction.guild.id)["member"]["autorole_id"] = role.id if role else None
        await save_data()
        await interaction.response.send_message(f"✅ Autorole set to {role.mention}." if role else "✅ Autorole disabled.", ephemeral=True)

    @client.tree.command(name="verification", description="Create the Rovix verification panel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def verification(interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name="Verified")
        if not role:
            role = await interaction.guild.create_role(name="Verified", reason="Rovix verification setup")
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Rovix cannot assign the Verified role.", ephemeral=True)
            return
        guild_config(interaction.guild.id)["member"]["verification_role_id"] = role.id
        await save_data()
        embed = discord.Embed(title="Server Verification", description="Press the button below to receive the Verified role.", colour=discord.Colour.green())
        await interaction.channel.send(embed=embed, view=VerificationView())
        await interaction.response.send_message("✅ Verification panel created.", ephemeral=True)

    @client.tree.command(name="rules", description="Publish server rules")
    @app_commands.describe(text="Rules content")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def rules(interaction: discord.Interaction, text: str = "1. Be respectful.\\n2. No spam or harassment.\\n3. Keep content appropriate.\\n4. Follow Discord and server rules."):
        embed = discord.Embed(title="📜 Server Rules", description=text[:4000], colour=discord.Colour.blurple())
        await interaction.response.send_message(embed=embed)

    @client.tree.command(name="membercount", description="Show member counts")
    async def membercount(interaction: discord.Interaction):
        humans = sum(not member.bot for member in interaction.guild.members)
        bots = sum(member.bot for member in interaction.guild.members)
        await interaction.response.send_message(f"👥 Total: **{interaction.guild.member_count}**\n👤 Humans: **{humans}**\n🤖 Bots: **{bots}**")

    @client.tree.command(name="serverstats", description="Show server statistics")
    async def serverstats(interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"📊 {guild.name}", colour=discord.Colour.blurple())
        embed.add_field(name="Members", value=str(guild.member_count))
        embed.add_field(name="Channels", value=str(len(guild.channels)))
        embed.add_field(name="Roles", value=str(len(guild.roles)))
        embed.add_field(name="Text", value=str(len(guild.text_channels)))
        embed.add_field(name="Voice", value=str(len(guild.voice_channels)))
        embed.add_field(name="Forums", value=str(len(guild.forums)))
        embed.add_field(name="Boosts", value=str(guild.premium_subscription_count))
        await interaction.response.send_message(embed=embed)
