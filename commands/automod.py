import discord
from discord import app_commands

from core import guild_config, normalize_text, save_data


automod = app_commands.Group(name="automod", description="Configure Rovix AutoMod")


async def setup(client):
    client.tree.add_command(automod)

    @automod.command(name="words", description="Add, remove, or list blocked words")
    @app_commands.describe(action="What to do", word="Word to add or remove")
    @app_commands.choices(action=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove"),
        app_commands.Choice(name="List", value="list")
    ])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def words(interaction: discord.Interaction, action: str, word: str | None = None):
        values = guild_config(interaction.guild.id)["automod"]["words"]
        if action == "list":
            await interaction.response.send_message(", ".join(f"**{value}**" for value in values) or "No blocked words are configured.", ephemeral=True)
            return
        if not word:
            await interaction.response.send_message("❌ A word is required for this action.", ephemeral=True)
            return
        word = word.casefold().strip()
        if action == "add":
            if word not in values:
                values.append(word)
                await save_data()
            await interaction.response.send_message(f"✅ Added {word} to AutoMod.", ephemeral=True)
            return
        if word in values:
            values.remove(word)
            await save_data()
            await interaction.response.send_message(f"✅ Removed {word} from AutoMod.", ephemeral=True)
            return
        await interaction.response.send_message("That word is not configured.", ephemeral=True)

    @automod.command(name="links", description="Enable or disable link filtering")
    @app_commands.choices(enabled=[app_commands.Choice(name="Enabled", value="true"), app_commands.Choice(name="Disabled", value="false")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def links(interaction: discord.Interaction, enabled: str):
        guild_config(interaction.guild.id)["automod"]["links"] = enabled == "true"
        await save_data()
        await interaction.response.send_message(f"🔗 Link filtering {'enabled' if enabled == 'true' else 'disabled'}.", ephemeral=True)

    @automod.command(name="spam", description="Enable or disable spam protection")
    @app_commands.choices(enabled=[app_commands.Choice(name="Enabled", value="true"), app_commands.Choice(name="Disabled", value="false")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def spam(interaction: discord.Interaction, enabled: str):
        guild_config(interaction.guild.id)["automod"]["spam"] = enabled == "true"
        await save_data()
        await interaction.response.send_message(f"🚨 Spam protection {'enabled' if enabled == 'true' else 'disabled'}.", ephemeral=True)

    @automod.command(name="mentions", description="Configure mention spam protection")
    @app_commands.describe(enabled="Enable or disable", maximum="Maximum combined user and role mentions")
    @app_commands.choices(enabled=[app_commands.Choice(name="Enabled", value="true"), app_commands.Choice(name="Disabled", value="false")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def mentions(interaction: discord.Interaction, enabled: str, maximum: app_commands.Range[int, 1, 20] = 5):
        config = guild_config(interaction.guild.id)["automod"]
        config["mentions"] = enabled == "true"
        config["max_mentions"] = maximum
        await save_data()
        await interaction.response.send_message(f"📢 Mention protection {'enabled' if enabled == 'true' else 'disabled'} with limit {maximum}.", ephemeral=True)

    @automod.command(name="invites", description="Enable or disable Discord invite filtering")
    @app_commands.choices(enabled=[app_commands.Choice(name="Enabled", value="true"), app_commands.Choice(name="Disabled", value="false")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def invites(interaction: discord.Interaction, enabled: str):
        guild_config(interaction.guild.id)["automod"]["invites"] = enabled == "true"
        await save_data()
        await interaction.response.send_message(f"📨 Invite filtering {'enabled' if enabled == 'true' else 'disabled'}.", ephemeral=True)

    @automod.command(name="caps", description="Enable or disable excessive caps filtering")
    @app_commands.choices(enabled=[app_commands.Choice(name="Enabled", value="true"), app_commands.Choice(name="Disabled", value="false")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def caps(interaction: discord.Interaction, enabled: str):
        guild_config(interaction.guild.id)["automod"]["caps"] = enabled == "true"
        await save_data()
        await interaction.response.send_message(f"🔠 Caps filtering {'enabled' if enabled == 'true' else 'disabled'}.", ephemeral=True)

    @automod.command(name="settings", description="View AutoMod configuration")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def settings(interaction: discord.Interaction):
        config = guild_config(interaction.guild.id)["automod"]
        embed = discord.Embed(title="Rovix AutoMod", colour=discord.Colour.blurple())
        embed.add_field(name="Blocked words", value=str(len(config["words"])))
        embed.add_field(name="Links", value="Enabled" if config["links"] else "Disabled")
        embed.add_field(name="Spam", value="Enabled" if config["spam"] else "Disabled")
        embed.add_field(name="Mentions", value=f"{'Enabled' if config['mentions'] else 'Disabled'} ({config['max_mentions']})")
        embed.add_field(name="Invites", value="Enabled" if config["invites"] else "Disabled")
        embed.add_field(name="Caps", value="Enabled" if config["caps"] else "Disabled")
        embed.add_field(name="Whitelist", value=str(len(config["whitelist"])))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @automod.command(name="whitelist", description="Add, remove, or list allowed link domains")
    @app_commands.describe(action="What to do", domain="Domain such as example.com")
    @app_commands.choices(action=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove"),
        app_commands.Choice(name="List", value="list")
    ])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def whitelist(interaction: discord.Interaction, action: str, domain: str | None = None):
        values = guild_config(interaction.guild.id)["automod"]["whitelist"]
        if action == "list":
            await interaction.response.send_message(", ".join(f"**{value}**" for value in values) or "No domains are whitelisted.", ephemeral=True)
            return
        if not domain:
            await interaction.response.send_message("❌ A domain is required.", ephemeral=True)
            return
        domain = domain.casefold().strip().removeprefix("https://").removeprefix("http://").split("/")[0]
        if action == "add" and domain not in values:
            values.append(domain)
            await save_data()
            await interaction.response.send_message(f"✅ Whitelisted {domain}.", ephemeral=True)
            return
        if action == "remove" and domain in values:
            values.remove(domain)
            await save_data()
            await interaction.response.send_message(f"✅ Removed {domain} from the whitelist.", ephemeral=True)
            return
        await interaction.response.send_message("No change was made.", ephemeral=True)
